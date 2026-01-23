"""
Test script for AnomaLens API
"""
import requests
import json
import time
import random
from datetime import datetime

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_single_prediction():
    """Test single prediction endpoint"""
    print("\nTesting single prediction endpoint...")
    
    data = {
        "sensor_id": "sensor_001",
        "temperature": 22.5,
        "pressure": 1013.2,
        "humidity": 52.1,
        "vibration": 0.12
    }
    
    response = requests.post(f"{API_URL}/api/v1/predict", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction: {result['is_anomaly']}")
        print(f"Anomaly Score: {result['anomaly_score']:.3f}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Severity: {result['severity']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_batch_prediction():
    """Test batch prediction endpoint"""
    print("\nTesting batch prediction endpoint...")
    
    readings = []
    for i in range(5):
        readings.append({
            "sensor_id": f"sensor_{i:03d}",
            "temperature": 20 + random.uniform(-2, 2),
            "pressure": 1013 + random.uniform(-10, 10),
            "humidity": 50 + random.uniform(-5, 5),
            "vibration": random.uniform(0, 0.5)
        })
    
    data = {"readings": readings}
    
    response = requests.post(f"{API_URL}/api/v1/predict/batch", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total predictions: {len(result['predictions'])}")
        print(f"Summary: {json.dumps(result['summary'], indent=2)}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print("\nTesting model info endpoint...")
    response = requests.get(f"{API_URL}/api/v1/model")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Model Type: {result['model_type']}")
        print(f"Version: {result['version']}")
        print(f"Training Date: {result['training_date']}")
        print(f"Features: {result['features']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_metrics():
    """Test metrics endpoint"""
    print("\nTesting metrics endpoint...")
    response = requests.get(f"{API_URL}/api/v1/metrics")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"CPU Usage: {result['system']['cpu_percent']}%")
        print(f"Memory Usage: {result['system']['memory_percent']}%")
        print(f"Platform: {result['system']['platform']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_alerts():
    """Test alerts endpoint"""
    print("\nTesting alerts endpoint...")
    response = requests.get(f"{API_URL}/api/v1/alerts?hours=24")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        alerts = response.json()
        print(f"Total alerts: {len(alerts)}")
        if alerts:
            print(f"First alert: {alerts[0]['alert_id']}")
            print(f"Severity: {alerts[0]['severity']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def run_performance_test():
    """Run performance test"""
    print("\nRunning performance test...")
    
    # Generate 100 predictions
    start_time = time.time()
    
    successful = 0
    for i in range(10):  # Reduced for demo
        data = {
            "sensor_id": f"sensor_{i:03d}",
            "temperature": 20 + random.uniform(-2, 2),
            "pressure": 1013 + random.uniform(-10, 10),
            "humidity": 50 + random.uniform(-5, 5),
            "vibration": random.uniform(0, 0.5)
        }
        
        response = requests.post(f"{API_URL}/api/v1/predict", json=data)
        if response.status_code == 200:
            successful += 1
    
    end_time = time.time()
    
    print(f"Successful predictions: {successful}/10")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Average time per prediction: {(end_time - start_time) / 10 * 1000:.2f} ms")
    
    return successful == 10

def main():
    """Run all tests"""
    print("=" * 60)
    print("ANOMALENS API TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Single Prediction", test_single_prediction),
        ("Batch Prediction", test_batch_prediction),
        ("Model Info", test_model_info),
        ("Metrics", test_metrics),
        ("Alerts", test_alerts),
        ("Performance Test", run_performance_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Test: {test_name}")
        print('='*40)
        
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"✓ PASS" if success else "✗ FAIL")
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    if passed == total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    main()