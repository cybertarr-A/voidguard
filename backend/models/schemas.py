from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field

class IngestPayload(BaseModel):
    agent_id: str = Field(min_length=1)
    encrypted_data: str = Field(min_length=1)  # Base64 encoded AES payload

# Decrypted internal usage model
class TelemetryData(BaseModel):
    timestamp: float
    ip_address: str = Field(min_length=1)
    endpoint: str = Field(min_length=1)
    method: str = Field(min_length=1)
    headers: Dict[str, str]
    body_size: int = Field(ge=0)
    auth_token: Optional[str] = None
    system_cpu: float = Field(ge=0, le=100)
    system_mem: float = Field(ge=0, le=100)

class AlertResponse(BaseModel):
    id: int
    agent_id: str
    ip_address: str
    risk_score: float
    action_taken: str
    reason: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
