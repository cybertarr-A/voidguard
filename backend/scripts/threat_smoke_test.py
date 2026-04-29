import base64
import json
import sys
import time
import uuid
from pathlib import Path

import httpx

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from config import settings
from core.security import encrypt_payload


API_BASE_URL = "http://localhost:8080/api/v1"
POLL_SECONDS = 120
POLL_INTERVAL_SECONDS = 3


def build_threat_sample(agent_id: str, ip_address: str) -> dict:
    headers = {
        "Accept": "*/*",
        "User-Agent": "sqlmap/1.4.11#dev",
    }
    headers.update({f"X-Forwarded-{index}": f"192.168.1.{index}" for index in range(60)})

    return {
        "timestamp": time.time(),
        "ip_address": ip_address,
        "endpoint": "/api/v1/admin?id=1 UNION SELECT * FROM users WHERE 1=1",
        "method": "POST",
        "headers": headers,
        "body_size": 15_000_000,
        "auth_token": "malformed_token_123",
        "system_cpu": 91.0,
        "system_mem": 88.0,
    }


def main() -> None:
    run_id = uuid.uuid4()
    agent_id = f"manual-threat-test-{run_id}"
    ip_address = f"10.99.{run_id.int % 250}.{(run_id.int >> 8) % 250}"
    telemetry = build_threat_sample(agent_id, ip_address)
    encrypted = encrypt_payload(json.dumps(telemetry))
    encoded_payload = base64.b64encode(encrypted).decode("utf-8")

    with httpx.Client(timeout=10.0) as client:
        ingest_response = client.post(
            f"{API_BASE_URL}/ingest/",
            json={
                "agent_id": agent_id,
                "encrypted_data": encoded_payload,
            },
        )
        ingest_response.raise_for_status()
        print(f"Ingest accepted for {agent_id}")

        login_response = client.post(
            f"{API_BASE_URL}/auth/login",
            data={
                "username": settings.ADMIN_USERNAME,
                "password": settings.ADMIN_PASSWORD,
            },
        )
        login_response.raise_for_status()
        token = login_response.json()["access_token"]

        matching_alerts = []
        deadline = time.monotonic() + POLL_SECONDS
        while time.monotonic() < deadline:
            alerts_response = client.get(
                f"{API_BASE_URL}/alerts/",
                headers={"Authorization": f"Bearer {token}"},
            )
            alerts_response.raise_for_status()

            matching_alerts = [
                alert for alert in alerts_response.json() if alert["agent_id"] == agent_id
            ]
            if matching_alerts:
                break

            print("Waiting for background detection to finish...")
            time.sleep(POLL_INTERVAL_SECONDS)

        if not matching_alerts:
            raise SystemExit(
                "No alert was recorded for the manual threat sample. Check backend logs."
            )

        alert = matching_alerts[0]
        print("Detection result:")
        print(json.dumps(alert, indent=2, default=str))

        if alert["action_taken"] != "BLOCK":
            raise SystemExit(
                f"Expected BLOCK, got {alert['action_taken']} with score {alert['risk_score']}"
            )

        print("Threat smoke test passed: sample was detected and blocked.")


if __name__ == "__main__":
    main()
