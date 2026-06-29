from __future__ import annotations

import os
from typing import TypedDict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import pkcs12

from app.core.config import get_settings


class CertificateMetadata(TypedDict):
    common_name: str
    serial_number: str
    valid_from: object
    valid_until: object


class CertificateSecurityService:
    def __init__(self) -> None:
        settings = get_settings()
        key_str = settings.CERTIFICATE_ENCRYPTION_KEY
        if len(key_str) < 32:
            key_str = key_str.ljust(32, "0")
        self.key = key_str[:32].encode("utf-8")

    def encrypt_data(self, data: bytes) -> bytes:
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        aesgcm = AESGCM(self.key)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)

    def extract_metadata(self, pfx_data: bytes, password: str) -> CertificateMetadata:
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, password.encode("utf-8")
        )

        common_name = ""
        for attribute in certificate.subject:
            if attribute.oid.dotted_string == "2.5.4.3":  # CN
                common_name = str(attribute.value)
                break

        return {
            "common_name": common_name,
            "serial_number": str(certificate.serial_number),
            "valid_from": certificate.not_valid_before_utc,
            "valid_until": certificate.not_valid_after_utc,
        }
