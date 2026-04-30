import sys
import os
import json
from groq import AsyncGroq
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import TelemetryData
from config import settings

class AIAgent:
    """
    AIAgent leverages the Groq API (LLM) to perform semantic analysis on incoming
    telemetry data and assess the security risk. Also analyzes vulnerabilities.
    """
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if self.api_key:
            self.client = AsyncGroq(api_key=self.api_key)
        else:
            self.client = None

    async def analyze(self, telemetry: TelemetryData) -> dict:
        if not self.client:
            print("[AIAgent] GROQ_API_KEY not set, skipping AI analysis.")
            return {"score": 0.0, "reason": "AI Analysis Disabled (No API Key)"}

        prompt = f"""
You are an advanced cybersecurity AI analyzing web telemetry for malicious activity.
Evaluate the following telemetry data and assign a risk score from 0.0 to 100.0.
A score of 0.0 means completely benign. A score of 100.0 means definitively malicious (e.g., SQL injection, XSS, malformed payloads).
Provide a brief reason for your score.

Telemetry Data:
- IP Address: {telemetry.ip_address}
- Endpoint: {telemetry.endpoint}
- Method: {telemetry.method}
- Body Size: {telemetry.body_size} bytes
- Auth Token Present: {'Yes' if telemetry.auth_token else 'No'}
- Headers Count: {len(telemetry.headers)}
- System CPU: {telemetry.system_cpu}%
- System Mem: {telemetry.system_mem}%

Respond ONLY with a valid JSON object in the following format:
{{
    "risk_score": <float>,
    "reason": "<string>"
}}
"""
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a specialized cybersecurity analysis engine. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            risk_score = float(result_json.get("risk_score", 0.0))
            reason = result_json.get("reason", "No reason provided.")
            
            return {
                "score": risk_score,
                "reason": f"AIAgent: {reason}"
            }
            
        except Exception as e:
            print(f"[AIAgent] API Error: {e}")
            return {"score": 0.0, "reason": f"AI Analysis Failed: {str(e)}"}

    async def analyze_vulnerability(self, findings: list[Dict[str, Any]]) -> str:
        if not self.client:
            return "AI Analysis disabled due to missing API key."

        prompt = f"""
You are an expert SOC analyst. Review the following vulnerability scanner findings and provide a summary of the risk and recommended actions.
Findings: {json.dumps(findings, indent=2)}

Respond with a concise, actionable summary explaining the vulnerabilities and their potential impact.
"""
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a specialized cybersecurity analyst. Provide a brief summary."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Failed to generate AI explanation: {e}"

# Singleton instance
ai_agent = AIAgent()
