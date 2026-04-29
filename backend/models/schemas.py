from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class IngestPayload(BaseModel):
    agent_id: str
    encrypted_data: str  # Base64 encoded AES payload

# Decrypted internal usage model
class TelemetryData(BaseModel):
    timestamp: float
    ip_address: str
    endpoint: str
    method: str
    headers: Dict[str, str]
    body_size: int
    auth_token: Optional[str] = None
    system_cpu: float
    system_mem: float

class AlertResponse(BaseModel):
    id: int
    agent_id: str
    risk_score: float
    action_taken: str
    reason: str
    created_at: datetime
    
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
