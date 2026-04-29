import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Needs to match backend AES_KEY exactly.
# In a real deployed app, this would be obfuscated, or fetched via secure initial handshake.
class CryptoModule:
    def __init__(self, key_hex: str):
        try:
            self._key = bytes.fromhex(key_hex)
            self._aesgcm = AESGCM(self._key)
        except Exception as e:
            print(f"Failed to initialize CryptoModule: {e}")
            raise

    def encrypt(self, plaintext: str) -> str:
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        encrypted_payload = nonce + ciphertext
        return base64.b64encode(encrypted_payload).decode('utf-8')
