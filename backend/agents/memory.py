import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import TelemetryData
from core.vector_db import get_chroma_collection

class MemoryAgent:
    """
    Memory Agent uses a Vector Database to cross-reference request features
    against known historical attack patterns.
    """
    
    @staticmethod
    def analyze(telemetry: TelemetryData) -> float:
        collection = get_chroma_collection()
        if collection is None:
            return 0.0  # Vector DB not available
            
        risk_score = 0.0
        
        # Serialize parts of telemetry to string and create a mock embedding 
        # In a real deployed app, you'd use a small NLP model like all-MiniLM-L6-v2 
        # to generate embeddings for the text. ChromaDB handles embeddings automatically
        # if a default embedding function is used, so we can just pass the document text.
        text_payload = f"endpoint: {telemetry.endpoint} method: {telemetry.method} body_size: {telemetry.body_size}"
        
        # Query ChromaDB (Using text document directly, relying on default sentence-transformers model inside Chroma)
        try:
            results = collection.query(
                query_texts=[text_payload],
                n_results=1
            )
            
            # If distance is small (meaning highly similar to past attack)
            distances = results.get("distances") or []
            if distances and distances[0]:
                dist = distances[0][0]
                if dist < 0.3: # Close match
                    risk_score += 65.0
                elif dist < 0.5: # Partial match
                    risk_score += 30.0
        except Exception as e:
            print(f"[Memory] Query failed: {e}")
            
        return risk_score
        
    @staticmethod
    def store_pattern(telemetry: TelemetryData):
        collection = get_chroma_collection()
        if collection is None:
            return
            
        text_payload = f"endpoint: {telemetry.endpoint} method: {telemetry.method} body_size: {telemetry.body_size}"
        doc_id = str(uuid.uuid4())
        
        try:
            collection.add(
                documents=[text_payload],
                metadatas=[{"agent": telemetry.ip_address, "type": "attack_pattern"}],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"[Memory] Store failed: {e}")
