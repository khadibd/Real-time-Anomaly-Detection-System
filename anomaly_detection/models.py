import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.callbacks import EarlyStopping

class IsolationForestDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        
    def fit(self, X):
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        
    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

class LSTMAutoencoder:
    def __init__(self, timesteps=10, n_features=5):
        self.timesteps = timesteps
        self.n_features = n_features
        self.model = self.build_model()
        
    def build_model(self):
        model = Sequential([
            LSTM(64, activation='relu', 
                 input_shape=(self.timesteps, self.n_features),
                 return_sequences=True),
            LSTM(32, activation='relu', return_sequences=False),
            RepeatVector(self.timesteps),
            LSTM(32, activation='relu', return_sequences=True),
            LSTM(64, activation='relu', return_sequences=True),
            TimeDistributed(Dense(self.n_features))
        ])
        
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def detect_anomalies(self, data, threshold_quantile=0.95):
        predictions = self.model.predict(data)
        mse = np.mean(np.power(data - predictions, 2), axis=1)
        threshold = np.quantile(mse, threshold_quantile)
        anomalies = mse > threshold
        return anomalies, mse, threshold