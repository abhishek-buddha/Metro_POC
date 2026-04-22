import pytest
from src.services.encryption import encrypt_field, decrypt_field, mask_aadhaar


def test_encrypt_decrypt_roundtrip():
    plaintext = "ABCDE1234F"
    encrypted = encrypt_field(plaintext)
    assert encrypted != plaintext
    assert decrypt_field(encrypted) == plaintext


def test_mask_aadhaar():
    aadhaar = "123456789012"
    masked = mask_aadhaar(aadhaar)
    assert masked == "9012"


def test_mask_aadhaar_with_spaces():
    aadhaar = "1234 5678 9012"
    masked = mask_aadhaar(aadhaar)
    assert masked == "9012"


def test_mask_aadhaar_invalid_length():
    with pytest.raises(ValueError):
        mask_aadhaar("12345")
