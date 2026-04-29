import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.redis_client import get_redis
from core.database import AsyncSessionLocal
from models.domain import Alert
from models.schemas import TelemetryData
import json

class ResponseAgent:
    """
    Executes real-time mitigation actions like IP blocking
    and database logging.
    """
    
    @staticmethod
    async def execute_action(telemetry: TelemetryData, agent_id: str, score: float, action: str, reason: str):
        redis = await get_redis()
        
        # Action execution logic
        if action == "BLOCK":
            # Push IP to Redis BlockList (TTL: 24 hours)
            block_key = f"block:ip:{telemetry.ip_address}"
            await redis.setex(block_key, 86400, "malicious_activity")
            print(f"[Response] Blocked IP {telemetry.ip_address} for 24h")
            
        # Log to PostgreSQL
        try:
            async with AsyncSessionLocal() as session:
                alert = Alert(
                    agent_id=agent_id,
                    ip_address=telemetry.ip_address,
                    risk_score=score,
                    action_taken=action,
                    reason=reason,
                    raw_telemetry=telemetry.model_dump()
                )
                session.add(alert)
                await session.commit()
                
                # Publish alert to Redis Stream for real-time dashboard updates
                alert_payload = {
                    "agent_id": agent_id,
                    "ip": telemetry.ip_address,
                    "score": score,
                    "action": action,
                    "reason": reason
                }
                await redis.xadd("alerts_stream", {"data": json.dumps(alert_payload)})
                
        except Exception as e:
            print(f"[Response] Failed to save alert: {e}")
