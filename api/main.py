"""
AnomaLens FastAPI Application
Real-time Anomaly Detection API
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
import logging
from typing import List, Optional, Dict, Any
import asyncio

# Import local modules
from api.models import (
    SensorData, BatchSensorData, PredictionResponse, 
    ModelInfo, HealthCheck, TrainingRequest
)
from core.anomaly_detector import AnomalyDetector
from core.config import settings
from api.endpoints import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AnomaLens API",
    description="Real-time Anomaly Detection System for IoT Sensor Data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global anomaly detector instance
detector = None

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    global detector
    logger.info("🚀 Starting AnomaLens API...")
    
    # Initialize anomaly detector
    detector = AnomalyDetector()
    
    # Load or train initial model
    try:
        if os.path.exists(settings.MODEL_PATH):
            detector.load_model(settings.MODEL_PATH)
            logger.info(f"✅ Model loaded from {settings.MODEL_PATH}")
        else:
            logger.warning("⚠️ No pre-trained model found. Training initial model...")
            # Generate synthetic data for initial training
            from core.data_generator import generate_training_data
            X_train, _ = generate_training_data(n_samples=1000)
            detector.train(X_train)
            detector.save_model(settings.MODEL_PATH)
            logger.info("✅ Initial model trained and saved")
    except Exception as e:
        logger.error(f"❌ Failed to initialize model: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down AnomaLens API...")
    # Save any pending data or models
    if detector and hasattr(detector, 'model'):
        detector.save_model(settings.MODEL_PATH + ".backup")

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AnomaLens API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "predict": "/api/v1/predict",
            "batch_predict": "/api/v1/predict/batch",
            "model_info": "/api/v1/model",
            "dashboard": "/dashboard"  # If you add a dashboard
        }
    }

@app.get("/health", response_model=HealthCheck, tags=["monitoring"])
async def health_check():
    """Health check endpoint"""
    model_status = "healthy" if detector and detector.is_ready else "unhealthy"
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage("/")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_status": model_status,
        "version": "1.0.0",
        "disk_usage": {
            "total_gb": total // (2**30),
            "used_gb": used // (2**30),
            "free_gb": free // (2**30),
            "used_percent": round((used / total) * 100, 2)
        }
    }

@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    """Serve a simple dashboard"""
    return FileResponse("static/dashboard.html")

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# WebSocket for real-time updates (optional)
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time anomaly alerts"""
    await websocket.accept()
    try:
        while True:
            # Simulate real-time data (in production, connect to Kafka)
            await asyncio.sleep(2)
            
            # Generate mock sensor data
            mock_data = {
                "sensor_id": f"sensor_{np.random.randint(1, 10):03d}",
                "timestamp": datetime.now().isoformat(),
                "temperature": 20 + np.random.normal(0, 3),
                "pressure": 1013 + np.random.normal(0, 15),
                "is_anomaly": np.random.random() > 0.9
            }
            
            # Predict if not already marked
            if not mock_data["is_anomaly"]:
                sensor_data = SensorData(**mock_data)
                prediction = await detector.predict_single(sensor_data)
                mock_data["is_anomaly"] = prediction.is_anomaly
                mock_data["anomaly_score"] = prediction.anomaly_score
            
            await websocket.send_json(mock_data)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )