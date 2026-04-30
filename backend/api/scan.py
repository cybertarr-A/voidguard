from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.domain import Scan, Vulnerability
from models.schemas import ScanRequest, ScanResponse, VulnerabilitySchema
from scanner.scanner_engine import scanner_engine

router = APIRouter()

@router.post("/", response_model=dict)
async def trigger_scan(request: ScanRequest):
    scan_id = await scanner_engine.start_scan(request)
    return {"scan_id": scan_id, "message": "Scan started successfully"}

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan_results(scan_id: str, db: AsyncSession = Depends(get_db)):
    scan_record = await db.get(Scan, scan_id)
    if not scan_record:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    stmt = select(Vulnerability).where(Vulnerability.scan_id == scan_id)
    result = await db.execute(stmt)
    vulns = result.scalars().all()
    
    vuln_schemas = [
        VulnerabilitySchema(
            id=v.id,
            scan_id=v.scan_id,
            vuln_type=v.vuln_type,
            severity=v.severity,
            description=v.description,
            evidence=v.evidence,
            created_at=v.created_at
        ) for v in vulns
    ]
    
    return ScanResponse(
        id=scan_record.id,
        target_url=scan_record.target_url,
        status=scan_record.status,
        scan_type=scan_record.scan_type,
        depth=scan_record.depth,
        risk_score=scan_record.risk_score,
        ai_explanation=scan_record.ai_explanation,
        vulnerabilities=vuln_schemas,
        created_at=scan_record.created_at
    )
