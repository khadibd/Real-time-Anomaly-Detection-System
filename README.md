A production-ready anomaly detection API for IoT sensor data with real-time monitoring, alerting, and MLOps capabilities.


✨ Features



\- Real-time Anomaly Detection: Detect anomalies in streaming sensor data

\- RESTful API: Fully documented FastAPI endpoints

\- Multiple Algorithms: Isolation Forest, One-Class SVM, Local Outlier Factor

\- WebSocket Support: Real-time anomaly alerts

\- Dashboard: Interactive web dashboard

\- Model Management: Versioning, training, and evaluation

\- Monitoring: System metrics and health checks

\- Alert System: Email/Slack/Teams notifications

\- Docker Support: Easy deployment with Docker Compose

_____________________________________________________________________________________________________________________________________________________________________________


### 🏗️ Architecture

┌─────────────┐ ┌─────────────┐ ┌─────────────┐

│ Sensors │────▶│ Kafka │────▶│ PySpark │

│ (IoT) │ │ (Stream) │ │ (Processing)│

└─────────────┘ └─────────────┘ └─────────────┘

│

┌─────────────┐ ┌─────────────┐ ┌─────────────┐

│ Grafana │◀────│ FastAPI │◀────│ Models │

│ (Dashboard) │ │ (API) │ │ (ML) │

└─────────────┘ └─────────────┘ └─────────────┘


_____________________________________________________________________________________________________________________________________________________________________________


### 🚀 Quick Start



### 1. Installation



```bash

\# Clone repository

git clone https://github.com/khadibd/Real-time-Anomaly-Detection-System

cd AnomaLens
```


```bash
\# Create virtual environment

python -m venv venv

source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```


```bash
\# Install dependencies

pip install -r requirements.txt
```




### 2. Start the API



```bash
\# Run the FastAPI server

python -m api.main
```



```bash
The API will be available at: http://localhost:8000

```



### 3. Access the Dashboard


```bash
Open your browser and go to: http://localhost:8000/dashboard
```


### 4. Test the API



```bash
\# Run the test suite

python test\_api.py
```


_____________________________________________________________________________________________________________________________________________________________________________


### 📚 API Documentation


```bash
Interactive Docs

Swagger UI: http://localhost:8000/docs



ReDoc: http://localhost:8000/redoc

```

_____________________________________________________________________________________________________________________________________________________________________________



### 🐳 Docker Deployment


```bash
\# Build and run with Docker Compose

docker-compose up --build
```


```bash

\# Run in background

docker-compose up -d
```


```bash
\# View logs

docker-compose logs -f
```


```bash
\# Stop services

docker-compose down
```


_____________________________________________________________________________________________________________________________________________________________________________


### 📊 Monitoring \& Observability



Built-in Monitoring

Health checks: /health endpoint



Metrics: /api/v1/metrics endpoint



Logging: Structured logs in logs/ directory



External Integrations

Prometheus: Metrics endpoint at /metrics (port 9090)



Grafana: Pre-built dashboards available



MLflow: Experiment tracking at http://localhost:5000

_____________________________________________________________________________________________________________________________________________________________________________

### 🤖 MLOps Features

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

_____________________________________________________________________________________________________________________________________________________________________________


### 🧪 Testing


```bash
\# Run unit tests

pytest tests/
```


```bash
\# Run with coverage

pytest --cov=api tests/
```


```bash
\# Run performance tests

python test\_api.py
```


_____________________________________________________________________________________________________________________________________________________________________________



### 📈 Performance

Latency: < 50ms per prediction



Throughput: 1000+ predictions per second



Accuracy: 95%+ on synthetic data



Scalability: Horizontal scaling with Docker

_____________________________________________________________________________________________________________________________________________________________________________


### 🔒 Security

CORS configuration



API key authentication (optional)



Input validation with Pydantic



Rate limiting (planned)



HTTPS support (planned)

_____________________________________________________________________________________________________________________________________________________________________________


### 📁 Project Structure


```bash

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
```

_____________________________________________________________________________________________________________________________________________________________________________


### 🚀 Production Deployment

### 1. Environment Setup


```bash
\# Set production environment

export DEBUG=False

export PORT=80
```



### 2. Database Setup


```bash
\# Setup PostgreSQL (optional)

docker run --name anomalens-db -e POSTGRES\_PASSWORD=secret -d postgres
```



### 3. Deploy with Docker


```bash
\# Build production image

docker build -t anomalens:latest .
```


### 4. Deploy to Cloud

AWS: ECS/EKS with Fargate



GCP: Cloud Run or GKE



Azure: AKS or App Service



Heroku: Simple one-click deploy

_____________________________________________________________________________________________________________________________________________________________________________


🎯 Use Cases

### 1. Industrial IoT

Predictive maintenance



Equipment monitoring



Quality control



### 2. Smart Cities

Traffic pattern analysis



Utility consumption monitoring



Environmental monitoring



### 3. Healthcare

Patient monitoring



Medical device tracking



Hospital equipment management



### 4. Finance

Fraud detection



Transaction monitoring



Risk assessment

_____________________________________________________________________________________________________________________________________________________________________________


### 🤝 Contributing

Fork the repository



Create a feature branch



Make your changes



Add tests



Submit a pull request


_____________________________________________________________________________________________________________________________________________________________________________

### 📄 License

MIT License - see LICENSE file


_____________________________________________________________________________________________________________________________________________________________________________


###  Acknowledgments

Built with FastAPI



Machine learning with scikit-learn



Real-time processing with Kafka



Monitoring with Prometheus/Grafana



Containerization with Docker


_____________________________________________________________________________________________________________________________________________________________________________


### 👩‍💻 Author

Eng. Khadija Bouadi


### 📧 Contact

For any queries, reach out to:

GitHub: @khadibd

Email:  khadibd00@gmail.com





