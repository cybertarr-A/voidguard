import psutil
import time
import random

class TelemetryCollector:
    @staticmethod
    def get_system_metrics():
        return {
            "system_cpu": psutil.cpu_percent(interval=None),
            "system_mem": psutil.virtual_memory().percent
        }
        
    @staticmethod
    def generate_simulated_traffic():
        """
        Simulate an incoming API request that reaches the server, 
        but harvested by client-side local integration loops.
        We inject occasional anomalies.
        """
        is_attack = random.random() < 0.1 # 10% chance of being an attack
        
        methods = ["GET", "POST", "PUT", "DELETE"]
        method = "POST" if is_attack else random.choice(methods)
        
        endpoints = ["/api/v1/users", "/api/v1/products", "/api/v1/auth", "/index.html"]
        endpoint = "/api/v1/admin?id=1 UNION SELECT *" if is_attack else random.choice(endpoints)
        
        headers = {
            "User-Agent": "Mozilla/5.0" if not is_attack else "sqlmap/1.4.11#dev",
            "Accept": "*/*"
        }
        if is_attack and random.random() < 0.5:
            # Overload headers
            for i in range(60):
                headers[f"X-Forwarded-{i}"] = f"192.168.1.{i}"
                
        body_size = random.randint(100, 5000)
        if is_attack and random.random() < 0.3:
            body_size = 15_000_000 # 15MB massive payload
            
        auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI.simulated.token" 
        if is_attack and random.random() < 0.5:
            auth_token = "malformed_token_123"

        sys_metrics = TelemetryCollector.get_system_metrics()
        
        telemetry = {
            "timestamp": time.time(),
            "ip_address": f"10.0.0.{random.randint(1, 255)}",
            "endpoint": endpoint,
            "method": method,
            "headers": headers,
            "body_size": body_size,
            "auth_token": auth_token,
            "system_cpu": sys_metrics["system_cpu"],
            "system_mem": sys_metrics["system_mem"]
        }
        
        return telemetry
