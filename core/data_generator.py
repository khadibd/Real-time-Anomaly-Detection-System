"""
Data generation utilities
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_training_data(n_samples: int = 1000, anomaly_rate: float = 0.1) -> tuple:
    """
    Generate synthetic training data for anomaly detection
    
    Args:
        n_samples: Number of samples to generate
        anomaly_rate: Proportion of anomalies in data
    
    Returns:
        tuple: (X, y) where X is feature matrix and y is labels (1=anomaly, 0=normal)
    """
    np.random.seed(42)
    
    # Generate normal data
    n_normal = int(n_samples * (1 - anomaly_rate))
    n_anomaly = n_samples - n_normal
    
    # Normal sensor readings
    normal_temp = 20 + np.random.normal(0, 2, n_normal)
    normal_pressure = 1013 + np.random.normal(0, 10, n_normal)
    normal_humidity = 50 + np.random.normal(0, 5, n_normal)
    normal_vibration = np.random.uniform(0, 0.5, n_normal)
    
    # Anomalous sensor readings (various types)
    # Type 1: Temperature spikes
    anomaly_temp1 = 20 + np.random.uniform(15, 30, n_anomaly // 3)
    anomaly_pressure1 = 1013 + np.random.normal(0, 10, n_anomaly // 3)
    anomaly_humidity1 = 50 + np.random.normal(0, 5, n_anomaly // 3)
    anomaly_vibration1 = np.random.uniform(0, 0.5, n_anomaly // 3)
    
    # Type 2: Pressure drops
    anomaly_temp2 = 20 + np.random.normal(0, 2, n_anomaly // 3)
    anomaly_pressure2 = 1013 - np.random.uniform(50, 100, n_anomaly // 3)
    anomaly_humidity2 = 50 + np.random.normal(0, 5, n_anomaly // 3)
    anomaly_vibration2 = np.random.uniform(0, 0.5, n_anomaly // 3)
    
    # Type 3: High vibration
    anomaly_temp3 = 20 + np.random.normal(0, 2, n_anomaly - 2*(n_anomaly // 3))
    anomaly_pressure3 = 1013 + np.random.normal(0, 10, n_anomaly - 2*(n_anomaly // 3))
    anomaly_humidity3 = 50 + np.random.normal(0, 5, n_anomaly - 2*(n_anomaly // 3))
    anomaly_vibration3 = np.random.uniform(1.0, 2.0, n_anomaly - 2*(n_anomaly // 3))
    
    # Combine all data
    temperature = np.concatenate([normal_temp, anomaly_temp1, anomaly_temp2, anomaly_temp3])
    pressure = np.concatenate([normal_pressure, anomaly_pressure1, anomaly_pressure2, anomaly_pressure3])
    humidity = np.concatenate([normal_humidity, anomaly_humidity1, anomaly_humidity2, anomaly_humidity3])
    vibration = np.concatenate([normal_vibration, anomaly_vibration1, anomaly_vibration2, anomaly_vibration3])
    
    # Create feature matrix
    X = np.column_stack([temperature, pressure, humidity, vibration])
    
    # Create labels (1 for anomalies, 0 for normal)
    y = np.concatenate([
        np.zeros(n_normal),
        np.ones(n_anomaly)
    ])
    
    # Shuffle data
    indices = np.arange(n_samples)
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]
    
    return X, y

def generate_live_sensor_data(n_sensors: int = 10, hours: int = 24) -> pd.DataFrame:
    """
    Generate time-series sensor data for testing
    """
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(hours=hours),
        end=datetime.now(),
        freq='5min'
    )
    
    data = []
    
    for sensor_id in range(n_sensors):
        for ts in timestamps:
            # Base values with some sensor-specific offset
            base_temp = 20 + sensor_id * 0.5
            base_pressure = 1013 + sensor_id * 2
            
            # Add daily pattern
            hour = ts.hour
            temp_variation = 3 * np.sin(2 * np.pi * hour / 24)
            
            # Add random noise
            temp = base_temp + temp_variation + np.random.normal(0, 0.5)
            pressure = base_pressure + np.random.normal(0, 2)
            humidity = 50 + np.random.normal(0, 3)
            vibration = np.random.uniform(0, 0.2)
            
            # Occasionally add anomaly
            is_anomaly = np.random.random() < 0.02
            if is_anomaly:
                anomaly_type = np.random.choice(['temp_spike', 'pressure_drop', 'vibration_high'])
                if anomaly_type == 'temp_spike':
                    temp += np.random.uniform(10, 25)
                elif anomaly_type == 'pressure_drop':
                    pressure -= np.random.uniform(50, 100)
                else:
                    vibration += np.random.uniform(1.0, 2.0)
            
            data.append({
                'sensor_id': f'sensor_{sensor_id:03d}',
                'timestamp': ts,
                'temperature': temp,
                'pressure': pressure,
                'humidity': humidity,
                'vibration': vibration,
                'is_anomaly': int(is_anomaly)
            })
    
    return pd.DataFrame(data)