from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
import jwt
from jwt.exceptions import PyJWTError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

# Helper for passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT helpers
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if not isinstance(payload, dict):
            return None
        subject = payload.get("sub")
        if not subject:
            return None
        return str(subject)
    except PyJWTError:
        return None

# AES-256 for Agent payload encryption
# The key must be exactly 32 bytes.
_aes_key = bytes.fromhex(settings.AES_KEY)
_aesgcm = AESGCM(_aes_key)

def encrypt_payload(data: str) -> bytes:
    """Encrypt payload string and prepend with nonce."""
    nonce = os.urandom(12)
    ciphertext = _aesgcm.encrypt(nonce, data.encode('utf-8'), None)
    return nonce + ciphertext

def decrypt_payload(encrypted_data: bytes) -> str:
    """Decrypt payload assuming first 12 bytes are the nonce."""
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    plaintext = _aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')
