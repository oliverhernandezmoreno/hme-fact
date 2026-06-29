"""
CLI script to seed mock digital certificates and CAF files for all companies.
Usage:
    python -m app.cli.seed_certs_and_caf
"""

from __future__ import annotations

import asyncio
import datetime
import logging

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models import CAFFile, Certificate, Company
from app.services.certificate_security import CertificateSecurityService

logger = logging.getLogger(__name__)


def generate_mock_pfx() -> tuple[bytes, str]:
    # 1. Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Generate self-signed certificate
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CL"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Metropolitana"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Santiago"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "HME Fact SpA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Oliver Hernandez Moreno"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1))
        .not_valid_after(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365)
        )
        .sign(private_key, hashes.SHA256())
    )

    # 3. Create PKCS12 / PFX
    password = "mockpassword123"
    pfx_data = pkcs12.serialize_key_and_certificates(
        name=b"hme_fact_cert",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8")),
    )
    return pfx_data, password


def generate_mock_caf_xml(company_rut: str, company_name: str, dte_type: int) -> tuple[str, str]:
    # Generate RSA private key for the CAF
    priv = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    # Clean RUT for comparison
    clean_rut = company_rut.replace(".", "").strip()

    xml_content = f"""<AUTORIZACION>
  <CAF version="1.0">
    <DA>
      <RE>{clean_rut}</RE>
      <RS>{company_name}</RS>
      <TD>{dte_type}</TD>
      <RNG>
        <D>1</D>
        <H>1000</H>
      </RNG>
      <FA>2024-01-01</FA>
      <RSAPK>
        <M>dummy_modulus</M>
        <E>dummy_exponent</E>
      </RSAPK>
    </DA>
    <FRMA algoritmo="SHA1withRSA">dummy_signature</FRMA>
  </CAF>
  <RSASK>{priv_pem}</RSASK>
</AUTORIZACION>"""

    return xml_content, priv_pem


async def seed_certs_and_caf() -> None:
    security_service = CertificateSecurityService()
    async with AsyncSessionLocal() as session:
        # Get all companies
        companies_res = await session.execute(select(Company))
        companies = companies_res.scalars().all()

        if not companies:
            logger.error("❌ No companies found in the database. Please seed demo data first.")
            return

        for company in companies:
            # 1. Generate and save Certificate
            pfx_bytes, password = generate_mock_pfx()
            metadata = security_service.extract_metadata(pfx_bytes, password)

            encrypted_pfx = security_service.encrypt_data(pfx_bytes)
            encrypted_password = security_service.encrypt_data(password.encode("utf-8"))

            # Check if active cert already exists
            cert_res = await session.execute(
                select(Certificate).where(
                    Certificate.company_id == company.id, Certificate.is_active == True
                )
            )
            cert = cert_res.scalar_one_or_none()

            if cert is None:
                cert = Certificate(
                    company_id=company.id,
                    common_name=metadata["common_name"],
                    serial_number=metadata["serial_number"],
                    encrypted_pfx=encrypted_pfx,
                    encrypted_password=encrypted_password,
                    valid_from=metadata["valid_from"],
                    valid_until=metadata["valid_until"],
                    is_active=True,
                )
                session.add(cert)
                logger.info(f"🔑 Created active certificate for company {company.legal_name}")
            else:
                cert.common_name = metadata["common_name"]
                cert.serial_number = metadata["serial_number"]
                cert.encrypted_pfx = encrypted_pfx
                cert.encrypted_password = encrypted_password
                cert.valid_from = metadata["valid_from"]
                cert.valid_until = metadata["valid_until"]
                logger.info(f"🔑 Updated active certificate for company {company.legal_name}")

            # 2. Generate and save CAFs (33: Factura, 39: Boleta, 61: Nota Credito)
            for dte_type in [33, 39, 61]:
                caf_xml, private_key = generate_mock_caf_xml(
                    company.rut, company.legal_name, dte_type
                )

                # Check if CAF already exists for this type and range
                caf_res = await session.execute(
                    select(CAFFile).where(
                        CAFFile.company_id == company.id,
                        CAFFile.dte_type == dte_type,
                        CAFFile.folio_from == 1,
                        CAFFile.folio_to == 1000,
                    )
                )
                caf = caf_res.scalar_one_or_none()

                if caf is None:
                    caf = CAFFile(
                        company_id=company.id,
                        dte_type=dte_type,
                        folio_from=1,
                        folio_to=1000,
                        current_folio=1,
                        authorization_date=datetime.date(2024, 1, 1),
                        xml_content=caf_xml,
                        private_key=private_key,
                    )
                    session.add(caf)
                    logger.info(
                        f"📄 Created CAF for DTE type {dte_type} on company {company.legal_name}"
                    )
                else:
                    caf.xml_content = caf_xml
                    caf.private_key = private_key
                    logger.info(
                        f"📄 Updated CAF for DTE type {dte_type} on company {company.legal_name}"
                    )

        await session.commit()
        logger.info("🎉 Certificates and CAFs seeded successfully!")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(seed_certs_and_caf())


if __name__ == "__main__":
    main()
