"""
Configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "AnomaLens"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Model Settings
    MODEL_PATH: str = "models/anomaly_detector.joblib"
    MODEL_TYPE: str = "isolation_forest"
    DEFAULT_CONTAMINATION: float = 0.1
    
    # Data Settings
    FEATURE_COLUMNS: list = ['temperature', 'pressure', 'humidity', 'vibration']
    
    # Alert Settings
    ALERT_THRESHOLD_CRITICAL: float = 0.8
    ALERT_THRESHOLD_WARNING: float = 0.6
    
    # Database Settings (for future use)
    DATABASE_URL: Optional[str] = None
    
    # Security
    API_KEY: Optional[str] = None
    CORS_ORIGINS: list = ["*"]
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Create directories if they don't exist
os.makedirs("models", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("static", exist_ok=True)