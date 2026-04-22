"""Encryption and masking services for sensitive data."""
from cryptography.fernet import Fernet
from src.utils.config import config
import re


# Initialize cipher with key from environment
cipher = Fernet(config.ENCRYPTION_KEY.encode())


def encrypt_field(plaintext: str) -> str:
    """Encrypt sensitive field (PAN or account number)."""
    return cipher.encrypt(plaintext.encode()).decode()


def decrypt_field(ciphertext: str) -> str:
    """Decrypt encrypted field."""
    return cipher.decrypt(ciphertext.encode()).decode()


def mask_aadhaar(aadhaar_number: str) -> str:
    """Mask Aadhaar number - keep only last 4 digits."""
    clean = re.sub(r'\s', '', aadhaar_number)
    if len(clean) != 12:
        raise ValueError(f"Invalid Aadhaar number: expected 12 digits, got {len(clean)}")
    return clean[-4:]
