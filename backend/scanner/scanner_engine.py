import asyncio
import uuid
from datetime import datetime
from models.domain import Scan, Vulnerability, ScanLog
from models.schemas import ScanRequest
from scanner.crawler import WebCrawler
from scanner.analyzer import VulnerabilityAnalyzer
from agents.ai_agent import ai_agent
from core.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)

class ScannerEngine:
    async def start_scan(self, request: ScanRequest) -> str:
        scan_id = str(uuid.uuid4())
        
        async with AsyncSessionLocal() as session:
            new_scan = Scan(
                id=scan_id,
                target_url=request.url,
                status="RUNNING",
                scan_type=request.scan_type,
                depth=request.depth
            )
            session.add(new_scan)
            session.add(ScanLog(scan_id=scan_id, message="Scan initialized", level="INFO"))
            await session.commit()

        # Run scan in background
        asyncio.create_task(self._run_scan(scan_id, request))
        return scan_id

    async def _run_scan(self, scan_id: str, request: ScanRequest):
        try:
            async with AsyncSessionLocal() as session:
                session.add(ScanLog(scan_id=scan_id, message=f"Crawling {request.url} with depth {request.depth}", level="INFO"))
                await session.commit()

            crawler = WebCrawler(request.url, request.depth)
            endpoints = await crawler.crawl()

            async with AsyncSessionLocal() as session:
                session.add(ScanLog(scan_id=scan_id, message=f"Found {len(endpoints)} endpoints. Starting analysis.", level="INFO"))
                await session.commit()

            results = await VulnerabilityAnalyzer.run_all(endpoints)
            
            ai_explanation = None
            if request.scan_type == "AI" and results:
                ai_explanation = await ai_agent.analyze_vulnerability(results)
                
            risk_score = min(100.0, len(results) * 10.0) # Simple heuristic

            async with AsyncSessionLocal() as session:
                for res in results:
                    vuln = Vulnerability(
                        scan_id=scan_id,
                        vuln_type=res["vuln_type"],
                        severity=res["severity"],
                        description=res["description"],
                        evidence=res["evidence"]
                    )
                    session.add(vuln)
                
                scan_record = await session.get(Scan, scan_id)
                if scan_record:
                    scan_record.status = "COMPLETED"
                    scan_record.risk_score = risk_score
                    scan_record.ai_explanation = ai_explanation
                    
                session.add(ScanLog(scan_id=scan_id, message="Scan completed", level="INFO"))
                await session.commit()
                
        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {e}")
            async with AsyncSessionLocal() as session:
                scan_record = await session.get(Scan, scan_id)
                if scan_record:
                    scan_record.status = "FAILED"
                session.add(ScanLog(scan_id=scan_id, message=f"Scan failed: {str(e)}", level="ERROR"))
                await session.commit()

scanner_engine = ScannerEngine()
