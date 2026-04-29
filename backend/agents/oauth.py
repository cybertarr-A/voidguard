import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import TelemetryData

class OAuthAgent:
    """
    OAuth Agent inspects the authentication tokens and specific OAuth behaviors.
    """
    
    @staticmethod
    def analyze(telemetry: TelemetryData) -> float:
        risk_score = 0.0
        token = telemetry.auth_token
        
        if not token:
            # If no token but accessing sensitive route
            if "api/v1/admin" in telemetry.endpoint:
                risk_score += 80.0
            return risk_score
            
        # Basic static analysis of token structure
        parts = token.split('.')
        if len(parts) != 3:
            # Malformed JWT
            risk_score += 90.0
        
        # Check token entropy / length
        if len(token) < 20: 
            risk_score += 50.0
            
        return risk_score
