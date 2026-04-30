from agents.analyst import analyst
from agents.oauth import OAuthAgent
from agents.memory import MemoryAgent
from agents.response import ResponseAgent
from agents.ai_agent import ai_agent
from models.schemas import TelemetryData
from api.ws import ws_manager
from datetime import datetime

class DecisionEngine:
    """
    Coordinates agents to gather risk scores, calculates final score,
    and dispatches Response Agent.
    """
    
    # Thresholds
    BLOCK_THRESHOLD = 75.0
    ALERT_THRESHOLD = 40.0
    
    @staticmethod
    async def process(telemetry: TelemetryData, agent_id: str):
        # 1. Gather scores from Analyst, OAuth, Memory Agents, and AI
        analyst_score = analyst.analyze(telemetry)
        oauth_score = OAuthAgent.analyze(telemetry)
        memory_score = MemoryAgent.analyze(telemetry)
        ai_result = await ai_agent.analyze(telemetry)
        ai_score = ai_result["score"]
        ai_reason = ai_result["reason"]
        
        # 2. Heuristic aggregation (weighted)
        # We give AI a strong weight, while retaining the baseline agents
        total_score = (analyst_score * 0.4) + (oauth_score * 0.2) + (memory_score * 0.2) + (ai_score * 0.2)
        
        # If AI is highly confident it's an attack, auto-escalate the score
        if ai_score >= 85.0:
            total_score = max(total_score, 90.0)
            
        # Ensure max score is 100
        final_score = min(total_score, 100.0)
        
        action = "ALLOW"
        reason = "Traffic Normal"
        
        if final_score >= DecisionEngine.BLOCK_THRESHOLD:
            action = "BLOCK"
            reason = f"High risk activity detected. {ai_reason}" if ai_score > 50 else "High risk activity detected. Threshold exceeded."
            MemoryAgent.store_pattern(telemetry)
        elif final_score >= DecisionEngine.ALERT_THRESHOLD:
            action = "ALERT"
            reason = f"Suspicious activity. {ai_reason}" if ai_score > 30 else "Suspicious activity detected."
            
        # 3. Action execution
        await ResponseAgent.execute_action(telemetry, agent_id, final_score, action, reason)
        
        # 4. Broadcast to WebSocket
        alert_data = {
            "id": int(datetime.utcnow().timestamp() * 1000), # dummy ID for UI uniqueness
            "agent_id": agent_id,
            "ip_address": telemetry.ip_address,
            "risk_score": final_score,
            "action_taken": action,
            "reason": reason,
            "created_at": datetime.utcnow().isoformat()
        }
        await ws_manager.broadcast_alert(alert_data)
        
        return {
            "score": final_score,
            "action": action,
            "reason": reason
        }
