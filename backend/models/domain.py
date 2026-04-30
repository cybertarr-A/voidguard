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

class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True, index=True)
    target_url = Column(String, index=True)
    status = Column(String) # RUNNING, COMPLETED, FAILED
    scan_type = Column(String) # PASSIVE, ACTIVE, AI
    depth = Column(Integer)
    risk_score = Column(Float, nullable=True)
    ai_explanation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(String, index=True)
    vuln_type = Column(String)
    severity = Column(String)
    description = Column(String)
    evidence = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScanLog(Base):
    __tablename__ = "scan_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(String, index=True)
    message = Column(String)
    level = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
