import time
import psutil
import requests
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import logging

class MetricsCollector:
    def __init__(self, port=9090):
        self.port = port
        
        # Define metrics
        self.anomalies_detected = Counter(
            'anomalens_anomalies_total',
            'Total number of anomalies detected',
            ['sensor_id', 'severity']
        )
        
        self.prediction_latency = Histogram(
            'anomalens_prediction_latency_seconds',
            'Prediction latency in seconds',
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
        )
        
        self.model_accuracy = Gauge(
            'anomalens_model_accuracy',
            'Current model accuracy'
        )
        
        self.system_cpu = Gauge(
            'anomalens_system_cpu_percent',
            'System CPU usage percentage'
        )
        
        self.system_memory = Gauge(
            'anomalens_system_memory_percent',
            'System memory usage percentage'
        )
    
    def start(self):
        """Start metrics server"""
        start_http_server(self.port)
        print(f"📊 Metrics server started on port {self.port}")
        
        # Start background collection
        import threading
        thread = threading.Thread(target=self.collect_system_metrics)
        thread.daemon = True
        thread.start()
    
    def collect_system_metrics(self):
        """Continuously collect system metrics"""
        while True:
            self.system_cpu.set(psutil.cpu_percent())
            self.system_memory.set(psutil.virtual_memory().percent)
            time.sleep(5)
    
    def record_prediction(self, sensor_id: str, is_anomaly: bool, latency: float):
        """Record a prediction"""
        with self.prediction_latency.time():
            if is_anomaly:
                self.anomalies_detected.labels(
                    sensor_id=sensor_id,
                    severity='critical'
                ).inc()