#!/bin/bash

# AnomaLens Deployment Script

set -e  # Exit on error

echo "🚀 Starting AnomaLens Deployment..."

# Check Python version
python --version

# Create virtual environment
echo "📦 Setting up virtual environment..."
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data models logs

# Start Kafka
echo "🌀 Starting Kafka..."
docker-compose up -d zookeeper kafka

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
sleep 30

# Initialize MLflow
echo "📊 Initializing MLflow..."
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns &

# Train initial model
echo "🤖 Training initial model..."
python scripts/train_initial_model.py

# Start the application
echo "🚀 Starting AnomaLens application..."
python app/main.py &

echo "✅ Deployment complete!"
echo "📊 Dashboard: http://localhost:8050"
echo "📈 MLflow: http://localhost:5000"
echo "📋 API Docs: http://localhost:8000/docs"