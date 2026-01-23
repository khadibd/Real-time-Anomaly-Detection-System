"""
API endpoints/routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, File, UploadFile
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
import tempfile
import os

from api.models import (
    SensorData, BatchSensorData, PredictionResponse, 
    BatchPredictionResponse, ModelInfo, TrainingRequest,
    TrainingResponse, AnomalyAlert
)
from core.anomaly_detector import detector
from core.config import settings

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse, tags=["predictions"])
async def predict_anomaly(data: SensorData):
    """
    Predict if a single sensor reading is anomalous
    
    - **sensor_id**: Unique identifier of the sensor
    - **temperature**: Temperature in Celsius
    - **pressure**: Pressure in hPa
    - **humidity**: Humidity percentage
    - **vibration**: Vibration level
    
    Returns prediction with anomaly score and confidence.
    """
    try:
        if not detector.is_ready:
            raise HTTPException(status_code=503, detail="Model not ready. Please train a model first.")
        
        prediction = await detector.predict_single(data)
        return prediction
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict/batch", response_model=BatchPredictionResponse, tags=["predictions"])
async def predict_batch_anomalies(data: BatchSensorData):
    """
    Predict anomalies for multiple sensor readings at once
    
    - **readings**: List of sensor readings (max 1000)
    
    Returns predictions for all readings with summary statistics.
    """
    try:
        if not detector.is_ready:
            raise HTTPException(status_code=503, detail="Model not ready")
        
        start_time = datetime.now()
        
        # Process in batches to avoid memory issues
        batch_size = 100
        all_predictions = []
        
        for i in range(0, len(data.readings), batch_size):
            batch = data.readings[i:i + batch_size]
            batch_predictions = await detector.predict_batch(batch)
            all_predictions.extend(batch_predictions)
        
        # Calculate summary
        anomaly_count = sum(1 for p in all_predictions if p.is_anomaly)
        avg_score = np.mean([p.anomaly_score for p in all_predictions])
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BatchPredictionResponse(
            predictions=all_predictions,
            summary={
                "total_readings": len(all_predictions),
                "anomalies_detected": anomaly_count,
                "anomaly_rate": anomaly_count / len(all_predictions),
                "average_anomaly_score": float(avg_score),
                "critical_anomalies": sum(1 for p in all_predictions if p.severity.value == "critical")
            },
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@router.post("/predict/upload", response_model=BatchPredictionResponse, tags=["predictions"])
async def predict_from_file(
    file: UploadFile = File(..., description="CSV file with sensor data"),
    delimiter: str = Query(",", description="CSV delimiter")
):
    """
    Upload a CSV file with sensor data for batch prediction
    
    CSV should have columns: sensor_id,temperature,pressure,humidity,vibration,timestamp
    """
    try:
        # Read and validate CSV
        contents = await file.read()
        
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
            try:
                df = pd.read_csv(io.BytesIO(contents), delimiter=delimiter, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise HTTPException(status_code=400, detail="Could not decode file. Try UTF-8 encoding.")
        
        # Validate required columns
        required_columns = ['sensor_id', 'temperature', 'pressure', 'humidity', 'vibration']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing}"
            )
        
        # Convert to SensorData objects
        readings = []
        for _, row in df.iterrows():
            readings.append(SensorData(
                sensor_id=str(row['sensor_id']),
                temperature=float(row['temperature']),
                pressure=float(row['pressure']),
                humidity=float(row['humidity']),
                vibration=float(row['vibration']),
                timestamp=row.get('timestamp', datetime.now())
            ))
        
        # Create batch data
        batch_data = BatchSensorData(readings=readings)
        
        # Predict
        response = await predict_batch_anomalies(batch_data)
        
        # Save predictions to file
        output_df = pd.DataFrame([p.dict() for p in response.predictions])
        output_path = tempfile.mktemp(suffix=".csv")
        output_df.to_csv(output_path, index=False)
        
        # Add download link to response
        response.summary["download_url"] = f"/api/v1/predict/download/{os.path.basename(output_path)}"
        
        return response
    
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.get("/predict/download/{filename}", tags=["predictions"])
async def download_predictions(filename: str):
    """
    Download predictions as CSV file
    """
    file_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path, 
        media_type='text/csv',
        filename=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

@router.get("/model", response_model=ModelInfo, tags=["model"])
async def get_model_info():
    """
    Get information about the current anomaly detection model
    
    Returns model type, version, training date, and performance metrics.
    """
    try:
        if not detector.is_ready:
            raise HTTPException(status_code=503, detail="No model loaded")
        
        info = detector.get_model_info()
        return ModelInfo(**info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

@router.post("/model/train", response_model=TrainingResponse, tags=["model"])
async def train_model(
    request: TrainingRequest, 
    background_tasks: BackgroundTasks
):
    """
    Train a new anomaly detection model
    
    - **n_samples**: Number of samples to generate for training
    - **contamination**: Expected anomaly rate
    - **algorithm**: Algorithm to use (isolation_forest, one_class_svm, lof)
    
    Training happens in the background. Check /model endpoint for status.
    """
    try:
        # Start training in background
        background_tasks.add_task(
            detector.train_new_model,
            n_samples=request.n_samples,
            contamination=request.contamination,
            algorithm=request.algorithm
        )
        
        return TrainingResponse(
            success=True,
            model_id=f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            training_time_seconds=0,  # Will be updated by background task
            model_metrics={},
            message="Training started in background. Check /model endpoint for progress."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")

@router.get("/alerts", response_model=List[AnomalyAlert], tags=["alerts"])
async def get_recent_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    sensor_id: Optional[str] = Query(None, description="Filter by sensor ID")
):
    """
    Get recent anomaly alerts
    
    - **hours**: Number of hours to look back (1-168)
    - **severity**: Filter by severity level
    - **sensor_id**: Filter by specific sensor
    
    Returns list of recent alerts.
    """
    try:
        # In production, this would query a database
        # For now, return mock data
        alerts = []
        
        # Generate mock alerts for demonstration
        for i in range(min(50, hours * 6)):  # Up to 50 alerts
            alert_time = datetime.now() - timedelta(minutes=i*10)
            alerts.append(AnomalyAlert(
                alert_id=f"alert_{alert_time.strftime('%Y%m%d_%H%M%S')}_{i}",
                timestamp=alert_time,
                sensor_id=f"sensor_{(i % 10):03d}",
                severity="critical" if i % 5 == 0 else "warning",
                anomaly_score=0.7 + (i * 0.01) % 0.3,
                data=SensorData(
                    sensor_id=f"sensor_{(i % 10):03d}",
                    temperature=20 + np.random.normal(0, 5),
                    pressure=1013 + np.random.normal(0, 20),
                    humidity=50 + np.random.normal(0, 10),
                    vibration=np.random.uniform(0, 2)
                ),
                acknowledged=i % 3 == 0,
                acknowledged_by="admin" if i % 3 == 0 else None,
                acknowledged_at=alert_time + timedelta(minutes=5) if i % 3 == 0 else None
            ))
        
        # Apply filters
        if severity:
            alerts = [a for a in alerts if a.severity.value == severity]
        if sensor_id:
            alerts = [a for a in alerts if a.sensor_id == sensor_id]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return alerts[:100]  # Limit to 100 alerts
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.post("/alerts/{alert_id}/acknowledge", tags=["alerts"])
async def acknowledge_alert(
    alert_id: str,
    user: str = Query(..., description="User acknowledging the alert")
):
    """
    Acknowledge an anomaly alert
    
    - **alert_id**: ID of the alert to acknowledge
    - **user**: User acknowledging the alert
    
    Marks the alert as acknowledged.
    """
    try:
        # In production, update in database
        # For now, return success
        return {
            "success": True,
            "message": f"Alert {alert_id} acknowledged by {user}",
            "acknowledged_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """
    Get system and model metrics
    
    Returns various metrics for monitoring and dashboards.
    """
    try:
        import psutil
        import platform
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Model metrics
        model_info = await get_model_info()
        
        # API metrics (mock for now)
        total_predictions = np.random.randint(1000, 10000)
        anomalies_detected = total_predictions * 0.05  # 5% anomaly rate
        
        return {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "uptime_seconds": psutil.boot_time()
            },
            "api": {
                "total_predictions": total_predictions,
                "anomalies_detected": int(anomalies_detected),
                "average_response_time_ms": 45.2,
                "active_connections": 5
            },
            "model": model_info.dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")