from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "VOIDGUARD"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    AES_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # DB
    DATABASE_URL: str
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str = ""
    
    # ChromaDB
    CHROMA_HOST: str
    CHROMA_PORT: int
    
    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'

settings = Settings()
