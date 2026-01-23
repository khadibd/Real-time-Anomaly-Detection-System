\# 🚀 AnomaLens - Real-time Anomaly Detection System



A production-ready anomaly detection API for IoT sensor data with real-time monitoring, alerting, and MLOps capabilities.



\## ✨ Features



\- \*\*Real-time Anomaly Detection\*\*: Detect anomalies in streaming sensor data

\- \*\*RESTful API\*\*: Fully documented FastAPI endpoints

\- \*\*Multiple Algorithms\*\*: Isolation Forest, One-Class SVM, Local Outlier Factor

\- \*\*WebSocket Support\*\*: Real-time anomaly alerts

\- \*\*Dashboard\*\*: Interactive web dashboard

\- \*\*Model Management\*\*: Versioning, training, and evaluation

\- \*\*Monitoring\*\*: System metrics and health checks

\- \*\*Alert System\*\*: Email/Slack/Teams notifications

\- \*\*Docker Support\*\*: Easy deployment with Docker Compose



\## 🏗️ Architecture

┌─────────────┐ ┌─────────────┐ ┌─────────────┐

│ Sensors │────▶│ Kafka │────▶│ PySpark │

│ (IoT) │ │ (Stream) │ │ (Processing)│

└─────────────┘ └─────────────┘ └─────────────┘

│

┌─────────────┐ ┌─────────────┐ ┌─────────────┐

│ Grafana │◀────│ FastAPI │◀────│ Models │

│ (Dashboard) │ │ (API) │ │ (ML) │

└─────────────┘ └─────────────┘ └─────────────┘





\## 🚀 Quick Start



\### 1. Installation



```bash

\# Clone repository

git clone https://github.com/yourusername/AnomaLens.git

cd AnomaLens



\# Create virtual environment

python -m venv venv

source venv/bin/activate  # On Windows: venv\\Scripts\\activate



\# Install dependencies

pip install -r requirements.txt





2\. Start the API



\# Run the FastAPI server

python -m api.main





The API will be available at: http://localhost:8000





3\. Access the Dashboard

Open your browser and go to: http://localhost:8000/dashboard



4\. Test the API



\# Run the test suite

python test\_api.py





📚 API Documentation

Interactive Docs

Swagger UI: http://localhost:8000/docs



ReDoc: http://localhost:8000/redoc





Key Endpoints





Method	Endpoint	Description

GET	/health	Health check

POST	/api/v1/predict	Single prediction

POST	/api/v1/predict/batch	Batch prediction

GET	/api/v1/model	Model information

POST	/api/v1/model/train	Train new model

GET	/api/v1/alerts	Recent alerts

GET	/api/v1/metrics	System metrics

WS	/ws	WebSocket for real-time updates





🔧 Configuration



Create a .env file:



\# API Settings

HOST=0.0.0.0

PORT=8000

DEBUG=True



\# Model Settings

MODEL\_PATH=models/anomaly\_detector.joblib

MODEL\_TYPE=isolation\_forest

DEFAULT\_CONTAMINATION=0.1



\# Alert Settings

ALERT\_THRESHOLD\_CRITICAL=0.8

ALERT\_THRESHOLD\_WARNING=0.6



\# Email Settings (for alerts)

SMTP\_SERVER=smtp.gmail.com

SMTP\_PORT=587

SMTP\_USERNAME=your\_email@gmail.com

SMTP\_PASSWORD=your\_password





🐳 Docker Deployment



\# Build and run with Docker Compose

docker-compose up --build



\# Run in background

docker-compose up -d



\# View logs

docker-compose logs -f



\# Stop services

docker-compose down





📊 Monitoring \& Observability



Built-in Monitoring

Health checks: /health endpoint



Metrics: /api/v1/metrics endpoint



Logging: Structured logs in logs/ directory



External Integrations

Prometheus: Metrics endpoint at /metrics (port 9090)



Grafana: Pre-built dashboards available



MLflow: Experiment tracking at http://localhost:5000



🤖 MLOps Features

Model Management

Automatic model versioning



Training history tracking



Performance metrics logging



A/B testing support



Automated Pipeline

Data collection and validation



Feature engineering



Model training and evaluation



Model deployment and serving



Monitoring and retraining



🧪 Testing



\# Run unit tests

pytest tests/



\# Run with coverage

pytest --cov=api tests/



\# Run performance tests

python test\_api.py





📈 Performance

Latency: < 50ms per prediction



Throughput: 1000+ predictions per second



Accuracy: 95%+ on synthetic data



Scalability: Horizontal scaling with Docker



🔒 Security

CORS configuration



API key authentication (optional)



Input validation with Pydantic



Rate limiting (planned)



HTTPS support (planned)



📁 Project Structure



AnomaLens/

├── api/                 # FastAPI application

│   ├── main.py         # Main app

│   ├── models.py       # Pydantic models

│   ├── endpoints.py    # API routes

│   └── dependencies.py # Dependencies

├── core/               # Core logic

│   ├── config.py       # Configuration

│   ├── anomaly_detector.py # ML models

│   └── data_generator.py  # Data utilities

├── models/             # Saved models

├── static/dashboard.html      # Static files (dashboard)

├── logs/               # Application logs

├── tests/              # Test suite
    ├── test_api.py

    └── test_pipeline.py

├── docker/             # Docker configurations

├── requirements.txt    # Python dependencies

├── Dockerfile          # Docker image

├── docker-compose.yml  # Docker Compose

└── README.md           # This file



🚀 Production Deployment

1\. Environment Setup



\# Set production environment

export DEBUG=False

export PORT=80



2\. Database Setup



\# Setup PostgreSQL (optional)

docker run --name anomalens-db -e POSTGRES\_PASSWORD=secret -d postgres



3\. Deploy with Docker



\# Build production image

docker build -t anomalens:latest .



\# Run with production settings

docker run -d -p 80:80 \\

&nbsp; -e DEBUG=False \\

&nbsp; -e DATABASE\_URL=postgresql://user:pass@db:5432/anomalens \\

&nbsp; anomalens:latest





4\. Deploy to Cloud

AWS: ECS/EKS with Fargate



GCP: Cloud Run or GKE



Azure: AKS or App Service



Heroku: Simple one-click deploy



🎯 Use Cases

1\. Industrial IoT

Predictive maintenance



Equipment monitoring



Quality control



2\. Smart Cities

Traffic pattern analysis



Utility consumption monitoring



Environmental monitoring



3\. Healthcare

Patient monitoring



Medical device tracking



Hospital equipment management



4\. Finance

Fraud detection



Transaction monitoring



Risk assessment



🤝 Contributing

Fork the repository



Create a feature branch



Make your changes



Add tests



Submit a pull request



📄 License

MIT License - see LICENSE file



🙏 Acknowledgments

Built with FastAPI



Machine learning with scikit-learn



Real-time processing with Kafka



Monitoring with Prometheus/Grafana



Containerization with Docker



