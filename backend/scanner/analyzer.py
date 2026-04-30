import httpx
from scanner.payloads import SQLI_PAYLOADS, XSS_PAYLOADS, SENSITIVE_ENDPOINTS, get_headers_to_check
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class VulnerabilityAnalyzer:
    @staticmethod
    async def analyze_headers(url: str, client: httpx.AsyncClient):
        vulns = []
        try:
            response = await client.get(url)
            headers = response.headers
            for header in get_headers_to_check():
                if header.lower() not in [h.lower() for h in headers.keys()]:
                    vulns.append({
                        "vuln_type": "Missing Security Header",
                        "severity": "LOW",
                        "description": f"Missing header: {header}",
                        "evidence": {"header": header, "url": url}
                    })
        except Exception as e:
            logger.error(f"Error analyzing headers for {url}: {e}")
        return vulns

    @staticmethod
    async def analyze_sqli(url: str, client: httpx.AsyncClient):
        vulns = []
        for payload in SQLI_PAYLOADS:
            try:
                # Basic test appending to URL
                test_url = f"{url}?id={payload}"
                response = await client.get(test_url)
                if "syntax error" in response.text.lower() or "mysql" in response.text.lower() or "sqlite" in response.text.lower():
                    vulns.append({
                        "vuln_type": "SQL Injection",
                        "severity": "HIGH",
                        "description": "Possible SQLi detected",
                        "evidence": {"payload": payload, "url": test_url}
                    })
            except Exception:
                pass
        return vulns

    @staticmethod
    async def analyze_xss(url: str, client: httpx.AsyncClient):
        vulns = []
        for payload in XSS_PAYLOADS:
            try:
                test_url = f"{url}?q={payload}"
                response = await client.get(test_url)
                if payload in response.text:
                    vulns.append({
                        "vuln_type": "Cross-Site Scripting (XSS)",
                        "severity": "HIGH",
                        "description": "Reflected XSS detected",
                        "evidence": {"payload": payload, "url": test_url}
                    })
            except Exception:
                pass
        return vulns

    @staticmethod
    async def check_sensitive_endpoints(base_url: str, client: httpx.AsyncClient):
        vulns = []
        for endpoint in SENSITIVE_ENDPOINTS:
            try:
                test_url = urljoin(base_url, endpoint)
                response = await client.get(test_url, follow_redirects=False)
                if response.status_code in [200, 401, 403]:
                    vulns.append({
                        "vuln_type": "Exposed Sensitive Endpoint",
                        "severity": "MEDIUM",
                        "description": f"Endpoint {endpoint} is accessible or exists",
                        "evidence": {"url": test_url, "status_code": response.status_code}
                    })
            except Exception:
                pass
        return vulns

    @staticmethod
    async def run_all(endpoints: list[str]):
        results = []
        async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
            for url in endpoints:
                results.extend(await VulnerabilityAnalyzer.analyze_headers(url, client))
                results.extend(await VulnerabilityAnalyzer.analyze_sqli(url, client))
                results.extend(await VulnerabilityAnalyzer.analyze_xss(url, client))
            
            if endpoints:
                base_url = endpoints[0]
                results.extend(await VulnerabilityAnalyzer.check_sensitive_endpoints(base_url, client))
        return results
