from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import IngestPayload
from agents.sentinel import SentinelAgent
from agents.decision import DecisionEngine
from core.redis_client import get_redis

router = APIRouter()

async def check_rate_limit(agent_id: str):
    redis = await get_redis()
    key = f"rate_limit:{agent_id}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60) # 1 minute window
    if current > 100: # 100 req/min
        raise HTTPException(status_code=429, detail="Too Many Requests")

@router.post("/")
async def ingest_telemetry(payload: IngestPayload, background_tasks: BackgroundTasks):
    """
    Ingest encrypted telemetry from Client Agents.
    """
    await check_rate_limit(payload.agent_id)
    
    # Fast path: run AI logic in background to not block the agent
    background_tasks.add_task(process_telemetry, payload)
    
    return {"status": "accepted"}

async def process_telemetry(payload: IngestPayload):
    # 1. Sentinel agent normalizes data
    telemetry = SentinelAgent.process_payload(payload)
    if not telemetry:
        return
        
    # Check if IP is in redis blocklist
    redis = await get_redis()
    block_key = f"block:ip:{telemetry.ip_address}"
    if await redis.exists(block_key):
        # Drop it completely or handle blocked IP specifically
        return
        
    # 2. Pass to DecisionEngine
    await DecisionEngine.process(telemetry, payload.agent_id)

