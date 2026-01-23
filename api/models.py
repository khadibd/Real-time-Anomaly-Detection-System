"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    """Anomaly severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class SensorData(BaseModel):
    """Single sensor reading"""
    sensor_id: str = Field(..., description="Unique sensor identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp of reading")
    temperature: float = Field(..., ge=-50, le=100, description="Temperature in Celsius")
    pressure: float = Field(..., ge=900, le=1100, description="Pressure in hPa")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    vibration: float = Field(..., ge=0, le=10, description="Vibration level")
    location: Optional[str] = Field(None, description="Sensor location")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('timestamp', pre=True, always=True)
    def parse_timestamp(cls, v):
        if v is None:
            return datetime.now()
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except:
                return datetime.now()
        return v

class BatchSensorData(BaseModel):
    """Batch of sensor readings"""
    readings: List[SensorData] = Field(..., min_items=1, max_items=1000)
    
    @validator('readings')
    def check_unique_sensor_ids(cls, v):
        sensor_ids = [reading.sensor_id for reading in v]
        if len(set(sensor_ids)) < len(sensor_ids):
            raise ValueError("Duplicate sensor_ids found in batch")
        return v

class PredictionResponse(BaseModel):
    """Prediction response"""
    sensor_id: str
    timestamp: datetime
    is_anomaly: bool
    anomaly_score: float = Field(..., ge=0, le=1, description="Anomaly score (0=normal, 1=anomaly)")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")
    severity: Severity = Field(default=Severity.INFO, description="Anomaly severity")
    features: Dict[str, float] = Field(..., description="Original feature values")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")
    
    @validator('severity', always=True)
    def set_severity_based_on_score(cls, v, values):
        """Set severity based on anomaly score"""
        if 'anomaly_score' in values:
            score = values['anomaly_score']
            if score > 0.8:
                return Severity.CRITICAL
            elif score > 0.6:
                return Severity.WARNING
        return Severity.INFO

class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    predictions: List[PredictionResponse]
    summary: Dict[str, Any] = Field(..., description="Prediction summary")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")

class ModelInfo(BaseModel):
    """Model information"""
    model_type: str
    version: str
    training_date: datetime
    accuracy: Optional[float] = Field(None, ge=0, le=1)
    precision: Optional[float] = Field(None, ge=0, le=1)
    recall: Optional[float] = Field(None, ge=0, le=1)
    features: List[str]
    contamination: float = Field(..., ge=0, le=0.5)
    parameters: Dict[str, Any]

class TrainingRequest(BaseModel):
    """Model training request"""
    n_samples: int = Field(default=1000, ge=100, le=10000, description="Number of samples to generate for training")
    contamination: float = Field(default=0.1, ge=0.01, le=0.3, description="Expected anomaly rate")
    algorithm: str = Field(default="isolation_forest", description="Algorithm to use")
    
    @validator('algorithm')
    def validate_algorithm(cls, v):
        valid_algorithms = ['isolation_forest', 'one_class_svm', 'lof']
        if v not in valid_algorithms:
            raise ValueError(f"Algorithm must be one of {valid_algorithms}")
        return v

class TrainingResponse(BaseModel):
    """Training response"""
    success: bool
    model_id: str
    training_time_seconds: float
    model_metrics: Dict[str, float]
    message: str

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    model_status: str
    version: str
    disk_usage: Dict[str, float]

class AnomalyAlert(BaseModel):
    """Anomaly alert for notification"""
    alert_id: str
    timestamp: datetime
    sensor_id: str
    severity: Severity
    anomaly_score: float
    data: SensorData
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None