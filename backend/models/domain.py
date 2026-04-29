from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import Base

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    os_info = Column(String)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agent_id = Column(String, index=True)
    ip_address = Column(String, index=True)
    risk_score = Column(Float)
    action_taken = Column(String) # ALLOW, ALERT, BLOCK
    reason = Column(String)
    raw_telemetry = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
