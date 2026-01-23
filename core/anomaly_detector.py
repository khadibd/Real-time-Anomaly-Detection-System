"""
Anomaly detection model wrapper
"""
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

from api.models import SensorData, PredictionResponse
from core.config import settings

class AnomalyDetector:
    """Main anomaly detection class"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_ready = False
        self.model_info = {}
        self.training_history = []
    
    def load_model(self, model_path: str) -> bool:
        """Load pre-trained model from file"""
        try:
            loaded_data = joblib.load(model_path)
            self.model = loaded_data['model']
            self.scaler = loaded_data['scaler']
            self.model_info = loaded_data.get('model_info', {})
            self.is_ready = True
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False
    
    def save_model(self, model_path: str) -> bool:
        """Save model to file"""
        try:
            save_data = {
                'model': self.model,
                'scaler': self.scaler,
                'model_info': self.model_info,
                'timestamp': datetime.now().isoformat()
            }
            joblib.dump(save_data, model_path)
            return True
        except Exception as e:
            print(f"Failed to save model: {e}")
            return False
    
    def train(self, X: np.ndarray, algorithm: str = "isolation_forest", contamination: float = 0.1):
        """Train anomaly detection model"""
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        # Choose algorithm
        if algorithm == "isolation_forest":
            self.model = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100,
                max_samples='auto'
            )
        elif algorithm == "one_class_svm":
            self.model = OneClassSVM(
                nu=contamination,
                kernel='rbf',
                gamma='scale'
            )
        elif algorithm == "lof":
            self.model = LocalOutlierFactor(
                n_neighbors=20,
                contamination=contamination,
                novelty=True
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Train model
        self.model.fit(X_scaled)
        
        # Update model info
        self.model_info = {
            'model_type': algorithm,
            'version': '1.0',
            'training_date': datetime.now().isoformat(),
            'features': settings.FEATURE_COLUMNS,
            'contamination': contamination,
            'n_samples': len(X),
            'parameters': self.model.get_params()
        }
        
        self.is_ready = True
        self.training_history.append({
            'timestamp': datetime.now(),
            'algorithm': algorithm,
            'samples': len(X),
            'contamination': contamination
        })
    
    async def train_new_model(self, n_samples: int = 1000, contamination: float = 0.1, algorithm: str = "isolation_forest"):
        """Train new model asynchronously"""
        # Generate training data
        from core.data_generator import generate_training_data
        X_train, _ = generate_training_data(n_samples=n_samples, anomaly_rate=contamination)
        
        # Train model
        self.train(X_train, algorithm=algorithm, contamination=contamination)
        
        # Save model
        self.save_model(settings.MODEL_PATH)
        
        print(f"✅ New model trained with {n_samples} samples using {algorithm}")
    
    async def predict_single(self, sensor_data: SensorData) -> PredictionResponse:
        """Predict anomaly for single sensor reading"""
        if not self.is_ready:
            raise ValueError("Model not trained. Please train or load a model first.")
        
        # Prepare features
        features = np.array([[
            sensor_data.temperature,
            sensor_data.pressure,
            sensor_data.humidity,
            sensor_data.vibration
        ]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)
        score_samples = self.model.score_samples(features_scaled)
        
        # Convert to anomaly score (0=normal, 1=anomaly)
        # IsolationForest: lower score = more anomalous
        if hasattr(self.model, 'score_samples'):
            anomaly_score = -score_samples[0]  # Negative because lower score = more anomalous
            # Normalize to 0-1
            anomaly_score = 1 / (1 + np.exp(-anomaly_score))
        else:
            anomaly_score = 0.5 if prediction[0] == -1 else 0.1
        
        is_anomaly = prediction[0] == -1
        
        # Determine severity
        if anomaly_score > settings.ALERT_THRESHOLD_CRITICAL:
            severity = "critical"
            recommendations = [
                "Immediate investigation required",
                "Check sensor for faults",
                "Review recent sensor history"
            ]
        elif anomaly_score > settings.ALERT_THRESHOLD_WARNING:
            severity = "warning"
            recommendations = [
                "Monitor sensor closely",
                "Check for environmental changes"
            ]
        else:
            severity = "info"
            recommendations = ["Continue normal monitoring"]
        
        return PredictionResponse(
            sensor_id=sensor_data.sensor_id,
            timestamp=sensor_data.timestamp or datetime.now(),
            is_anomaly=bool(is_anomaly),
            anomaly_score=float(anomaly_score),
            confidence=float(min(anomaly_score * 1.5, 1.0)),  # Simple confidence calculation
            severity=severity,
            features={
                'temperature': sensor_data.temperature,
                'pressure': sensor_data.pressure,
                'humidity': sensor_data.humidity,
                'vibration': sensor_data.vibration
            },
            recommendations=recommendations
        )
    
    async def predict_batch(self, sensor_readings: List[SensorData]) -> List[PredictionResponse]:
        """Predict anomalies for batch of sensor readings"""
        predictions = []
        
        for reading in sensor_readings:
            prediction = await self.predict_single(reading)
            predictions.append(prediction)
        
        return predictions
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if not self.is_ready:
            return {"status": "No model loaded"}
        
        return self.model_info

# Create global detector instance
detector = AnomalyDetector()