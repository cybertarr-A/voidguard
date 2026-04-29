import json
import base64
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.security import decrypt_payload
from models.schemas import TelemetryData, IngestPayload

class SentinelAgent:
    """
    Sentinel Agent takes raw encrypted payloads from client agents,
    decrypts them, and normalizes them into TelemetryData.
    """
    
    @staticmethod
    def process_payload(payload: IngestPayload) -> Optional[TelemetryData]:
        try:
            # 1. Base64 decode
            encrypted_bytes = base64.b64decode(payload.encrypted_data, validate=True)
            
            # 2. Decrypt with AES-256-GCM
            decrypted_str = decrypt_payload(encrypted_bytes)
            
            # 3. Parse JSON
            data = json.loads(decrypted_str)
            
            # 4. Normalize to structured Pydantic model
            telemetry = TelemetryData(**data)
            return telemetry
        except Exception as e:
            print(f"[Sentinel] Failed to process payload: {e}")
            return None
