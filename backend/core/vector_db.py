import chromadb
from chromadb.config import Settings as ChromaSettings
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

# Initialize ChromaDB client to connect to the external docker container
chroma_client = chromadb.HttpClient(
    host=settings.CHROMA_HOST,
    port=settings.CHROMA_PORT
)

# Collection for attack patterns
try:
    patterns_collection = chroma_client.get_or_create_collection(
        name="threat_patterns",
        metadata={"hnsw:space": "cosine"}
    )
except Exception as e:
    print(f"Failed to connect to ChromaDB: {e}")
    patterns_collection = None

def get_chroma_collection():
    return patterns_collection

