from agents.analyst import analyst
from agents.oauth import OAuthAgent
from agents.memory import MemoryAgent
from agents.response import ResponseAgent
from models.schemas import TelemetryData
import asyncio

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
        # 1. Gather scores from Analyst, OAuth, and Memory Agents
        analyst_score = analyst.analyze(telemetry)
        oauth_score = OAuthAgent.analyze(telemetry)
        memory_score = MemoryAgent.analyze(telemetry)
        
        # 2. Heuristic aggregation (weighted)
        total_score = (analyst_score * 0.5) + (oauth_score * 0.3) + (memory_score * 0.2)
        
        # Ensure max score is 100
        final_score = min(total_score, 100.0)
        
        action = "ALLOW"
        reason = "Traffic Normal"
        
        if final_score >= DecisionEngine.BLOCK_THRESHOLD:
            action = "BLOCK"
            reason = "High risk activity detected. Threshold exceeded."
            MemoryAgent.store_pattern(telemetry)
        elif final_score >= DecisionEngine.ALERT_THRESHOLD:
            action = "ALERT"
            reason = "Suspicious activity detected."
            
        # 3. Action execution
        await ResponseAgent.execute_action(telemetry, agent_id, final_score, action, reason)
        
        return {
            "score": final_score,
            "action": action,
            "reason": reason
        }
