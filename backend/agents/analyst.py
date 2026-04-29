from sklearn.ensemble import IsolationForest
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import TelemetryData

class AnalystAgent:
    """
    Analyst Agent is responsible for anomaly detection using a hybrid 
    rule-based and ML (Isolation Forest) approach.
    """
    
    def __init__(self):
        # Initialize an Isolation forest.
        # In a real deployed environment, this would be loaded from disk and continuously retrained.
        self.model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        # Create a baseline dataset to fit initially so predict() works without failing.
        baseline_X = [
            [1000, 2.5, 30.0], [1200, 3.0, 31.0], [900, 1.5, 29.0], 
            [1100, 2.0, 32.0], [1050, 2.2, 30.5], [500, 1.0, 20.0],
            [1500, 4.0, 40.0], [1150, 2.8, 30.2], [950, 1.8, 29.5],
            [1020, 2.1, 30.8]
        ]
        self.model.fit(baseline_X)

    def extract_features(self, telemetry: TelemetryData) -> list:
        # Simple feature vector: [body_size, system_cpu, system_mem]
        # In real systems, this would include header entropy, request rates, etc.
        return [telemetry.body_size, telemetry.system_cpu, telemetry.system_mem]
        
    def analyze(self, telemetry: TelemetryData) -> float:
        risk_score = 0.0
        
        # 1. Rule-based checks
        if telemetry.body_size > 10_000_000:  # 10MB request size
            risk_score += 40.0
        
        if len(telemetry.headers) > 50:
            risk_score += 20.0
            
        danger_keywords = ["union select", "1=1", "script", "exec", "eval"]
        target = str(telemetry.endpoint).lower()
        if any(keyword in target for keyword in danger_keywords):
            risk_score += 70.0
            
        # 2. ML Anomaly Check
        feature_vector = np.array(self.extract_features(telemetry)).reshape(1, -1)
        # IF returns 1 for normal, -1 for anomaly
        prediction = self.model.predict(feature_vector)[0]
        
        if prediction == -1:
            risk_score += 35.0
            
        return min(risk_score, 100.0)

# Singleton instance
analyst = AnalystAgent()
