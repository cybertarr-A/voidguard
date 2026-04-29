import time
import json
import requests
import os
import uuid
from dotenv import load_dotenv

from crypto import CryptoModule
from collector import TelemetryCollector

# Load configuration normally via env
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080/api/v1/ingest/")
AES_KEY = os.getenv("AES_KEY", "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
AGENT_ID = os.getenv("AGENT_ID", str(uuid.uuid4()))

def run_agent():
    print(f"[*] Starting VOIDGUARD Client Agent ({AGENT_ID})")
    print(f"[*] Backend URL: {BACKEND_URL}")
    
    crypto = CryptoModule(AES_KEY)
    
    while True:
        try:
            # 1. Harvest Telemetry
            data = TelemetryCollector.generate_simulated_traffic()
            data_json = json.dumps(data)
            
            # 2. Encrypt Payload
            encrypted_payload = crypto.encrypt(data_json)
            
            # 3. Transmit
            req_data = {
                "agent_id": AGENT_ID,
                "encrypted_data": encrypted_payload
            }
            response = requests.post(BACKEND_URL, json=req_data, timeout=5)
            
            if response.status_code == 200:
                print(f"[+] Successfully sent payload ({len(encrypted_payload)} bytes)")
            elif response.status_code == 429:
                print("[-] Rate limited by backend")
            else:
                print(f"[-] Backend returned status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("[-] Connection to backend failed. Retrying in 5 seconds...")
        except Exception as e:
            print(f"[-] Agent encountered an error: {e}")
            
        time.sleep(2) # Send data every 2 seconds

if __name__ == "__main__":
    run_agent()
