
import pytest

from app.services.certificate_security import CertificateSecurityService


def test_certificate_encryption_decryption(monkeypatch: pytest.MonkeyPatch) -> None:
    # Use monkeypatch to set environment variable for testing
    monkeypatch.setenv("CERTIFICATE_ENCRYPTION_KEY", "test-key-12345678901234567890123")

    # Reload settings or mock get_settings if necessary, but we can also just initialize
    service = CertificateSecurityService()

    original_data = b"my_super_secret_pfx_binary_blob_content"

    encrypted = service.encrypt_data(original_data)
    assert encrypted != original_data

    decrypted = service.decrypt_data(encrypted)
    assert decrypted == original_data
