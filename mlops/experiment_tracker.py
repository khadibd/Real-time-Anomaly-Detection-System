import mlflow
import mlflow.sklearn
from datetime import datetime
import pandas as pd
import joblib

class ExperimentTracker:
    def __init__(self, experiment_name="AnomaLens_Experiments"):
        mlflow.set_experiment(experiment_name)
        
    def log_experiment(self, model, params, metrics, X_test, y_test, model_name="isolation_forest"):
        """Log experiment to MLflow"""
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(params)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(model, model_name)
            
            # Log test data sample
            test_sample = pd.DataFrame(X_test[:100])
            test_sample.to_csv("test_sample.csv", index=False)
            mlflow.log_artifact("test_sample.csv")
            
            # Log confusion matrix plot
            import matplotlib.pyplot as plt
            from sklearn.metrics import ConfusionMatrixDisplay
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ConfusionMatrixDisplay.from_predictions(y_test, model.predict(X_test), ax=ax)
            plt.savefig("confusion_matrix.png")
            mlflow.log_artifact("confusion_matrix.png")
            
        print(f"✅ Experiment logged to MLflow: {mlflow.active_run().info.run_id}")