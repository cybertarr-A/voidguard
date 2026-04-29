from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import get_db
from models.domain import Alert
from models.schemas import AlertResponse
from api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Get recent alerts for the dashboard. Protected route.
    """
    _ = current_user
    stmt = select(Alert).order_by(Alert.created_at.desc()).limit(100)
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    return [
        {
            "id": a.id,
            "agent_id": a.agent_id,
            "ip_address": a.ip_address,
            "risk_score": a.risk_score,
            "action_taken": a.action_taken,
            "reason": a.reason,
            "created_at": a.created_at
        }
        for a in alerts
    ]
