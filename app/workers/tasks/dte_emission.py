import logging
from datetime import UTC
from uuid import UUID

import httpx
from asgiref.sync import async_to_sync
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.certificate import Certificate
from app.models.dte import DTE
from app.models.enums import DTEStatus
from app.services.certificate_security import CertificateSecurityService
from app.services.pdf_generator import PDFGenerator
from app.services.sii.builder import DTEBuilder
from app.services.sii.circuit_breaker import SIICircuitBreakerOpenException
from app.services.sii.client import SIIWebServicesClient
from app.services.sii.signer import SIISigner
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def process_dte_emission_async(dte_id: UUID) -> str:
    """Core asynchronous logic to emit a DTE to the SII."""

    async with AsyncSessionLocal() as db:
        # 1. Fetch DTE with all relationships
        dte_result = await db.execute(
            select(DTE)
            .where(DTE.id == dte_id)
            .options(
                selectinload(DTE.items),
                selectinload(DTE.customer),
                selectinload(DTE.company),
                selectinload(DTE.caf_file),
            )
        )
        dte = dte_result.scalars().first()

        if not dte:
            raise ValueError(f"DTE {dte_id} not found.")

        if dte.status not in (DTEStatus.DRAFT, DTEStatus.QUEUED, DTEStatus.CONTINGENCY):
            raise ValueError(
                f"DTE {dte_id} is not in DRAFT, QUEUED or CONTINGENCY status. Current: {dte.status}"
            )

        company = dte.company

        try:
            # 2. Fetch Active Digital Certificate
            cert_result = await db.execute(
                select(Certificate).where(
                    Certificate.company_id == company.id, Certificate.is_active
                )
            )
            certificate = cert_result.scalars().first()
            if not certificate:
                raise ValueError("No active digital certificate found for company.")

            security_service = CertificateSecurityService()
            pfx_data = security_service.decrypt_data(certificate.encrypted_pfx)
            pfx_password = security_service.decrypt_data(certificate.encrypted_password).decode(
                "utf-8"
            )

            # 3. Build the XML Structure using the CAF
            if not dte.caf_file:
                raise ValueError("DTE does not have an assigned CAF file.")

            # Prepare dictionary data for the builder
            dte_type_val = dte.dte_type.value if hasattr(dte.dte_type, "value") else dte.dte_type
            dte_data = {
                "dte_type": dte_type_val,
                "folio": dte.folio,
                "issue_date": dte.issue_date.isoformat(),
                "emisor": {
                    "rut": company.rut,
                    "legal_name": company.legal_name,
                    "giro": company.giro or "Giro Emisor",
                    "acteco": "620100",
                    "address": company.address or "Direccion Emisor",
                    "comuna": company.comuna or "Santiago",
                },
                "receptor": {
                    "rut": dte.customer.rut if dte.customer else "1-9",
                    "legal_name": dte.customer.legal_name if dte.customer else "Sin Cliente",
                    "giro": dte.customer.giro
                    if (dte.customer and dte.customer.giro)
                    else "Giro Receptor",
                    "address": dte.customer.address
                    if (dte.customer and dte.customer.address)
                    else "Direccion Receptor",
                    "comuna": dte.customer.comuna
                    if (dte.customer and dte.customer.comuna)
                    else "Santiago",
                },
                "totales": {
                    "neto": int(dte.net_amount),
                    "exento": int(dte.exempt_amount) if dte.exempt_amount > 0 else None,
                    "iva": int(dte.tax_amount),
                    "total": int(dte.total_amount),
                },
                "items": [
                    {
                        "tax_exempt": item.tax_exempt,
                        "name": item.description,
                        "quantity": float(item.quantity),
                        "unit_price": float(item.unit_price),
                        "total_amount": float(item.total_amount),
                    }
                    for item in dte.items
                ],
                "caf_xml": dte.caf_file.xml_content,
                "caf_private_key": dte.caf_file.private_key,
            }

            if dte.reference_dte_type:
                dte_data["referencias"] = [
                    {
                        "dte_type": dte.reference_dte_type,
                        "folio": dte.reference_folio,
                        "date": dte.reference_date.isoformat()
                        if dte.reference_date
                        else dte.issue_date.isoformat(),
                        "code": dte.reference_code,
                        "reason": dte.reference_reason or "Referencia",
                    }
                ]

            from lxml import etree

            # Generate XML with a placeholder for the TED signature
            xml_tree = DTEBuilder.build_dte_xml(dte_data, timbre_firma="PLACEHOLDER")

            # Extract and sign the DD element for the TED (Timbre Electrónico DTE)
            dd_node = xml_tree.xpath("//*[local-name()='DD']")[0]
            clean_dd = etree.Element("DD")
            for k, v in dd_node.attrib.items():
                clean_dd.set(k, v)

            def copy_clean(parent, node):
                tag = etree.QName(node).localname
                new_node = etree.SubElement(parent, tag)
                new_node.text = node.text
                for k, v in node.attrib.items():
                    new_node.set(k, v)
                for child in node:
                    copy_clean(new_node, child)

            for child in dd_node:
                copy_clean(clean_dd, child)

            dd_str = etree.tostring(clean_dd, xml_declaration=False, encoding="ISO-8859-1").decode(
                "ISO-8859-1"
            )

            caf_private_key_pem = dte.caf_file.private_key.encode("utf-8")
            timbre_firma = SIISigner.sign_ted(dd_str, caf_private_key_pem)

            # Replace the placeholder in the FRMA tag
            frma_node = xml_tree.xpath("//*[local-name()='TED']/*[local-name()='FRMA']")[0]
            frma_node.text = timbre_firma

            # Build a clean TED string for the PDF generation (without namespaces)
            ted_node = xml_tree.xpath("//*[local-name()='TED']")[0]
            clean_ted = etree.Element("TED", version="1.0")
            for child in ted_node:
                if etree.QName(child).localname == "DD":
                    clean_ted.append(clean_dd)
                else:
                    new_child = etree.SubElement(clean_ted, etree.QName(child).localname)
                    new_child.text = child.text
                    for k, v in child.attrib.items():
                        new_child.set(k, v)
            ted_xml_string = etree.tostring(
                clean_ted, xml_declaration=False, encoding="ISO-8859-1"
            ).decode("ISO-8859-1")

            # 4. Sign the entire document using XML-DSig
            signer = SIISigner()
            signed_xml_bytes = signer.sign_dte(xml_tree, pfx_data, pfx_password, f"DOC_{dte.folio}")

            # 5. Send to SII using Client
            sii_client = SIIWebServicesClient(environment="certification")
            token = await sii_client.get_token(pfx_data, pfx_password)

            # Assuming certificate owner RUT is needed (usually extracted from Cert,
            # hardcoded for now)
            # In a real scenario, the RUT owner is stored when uploading the cert
            cert_owner_rut = company.rut

            track_id = await sii_client.enviar_dte(
                signed_xml_bytes, token, cert_owner_rut, company.rut
            )

            # 6. Generate PDF for the Client
            pdf_dte_data = {
                "emisor_name": company.legal_name,
                "emisor_giro": company.giro or "Giro Emisor",
                "emisor_address": company.address or "Direccion Emisor",
                "emisor_rut": company.rut,
                "receptor_name": dte.customer.legal_name if dte.customer else "Sin Cliente",
                "receptor_rut": dte.customer.rut if dte.customer else "1-9",
                "issue_date": dte.issue_date.isoformat(),
                "dte_type": dte_type_val,
                "folio": dte.folio,
                "items": dte_data["items"],
                "net_amount": float(dte.net_amount),
                "tax_amount": float(dte.tax_amount),
                "total_amount": float(dte.total_amount),
            }
            pdf_bytes = PDFGenerator.generate_dte_pdf(pdf_dte_data, ted_xml_string)

            # 7. Update DB states
            dte.status = DTEStatus.SENT
            dte.sii_track_id = track_id
            dte.sii_xml = signed_xml_bytes.decode("ISO-8859-1")
            from datetime import datetime

            dte.sent_at = datetime.now(UTC)

            # Persist the signed XML and PDF in storage (mocked here, we would use S3/Local storage)
            # Example: storage_service.save_pdf(pdf_bytes)

            await db.commit()

            logger.info(f"Successfully emitted DTE {dte.folio}. Track ID: {track_id}")
            return track_id

        except (SIICircuitBreakerOpenException, httpx.HTTPStatusError, httpx.RequestError) as e:
            is_5xx = False
            if isinstance(e, httpx.HTTPStatusError):
                is_5xx = e.response.status_code >= 500

            if (
                isinstance(e, SIICircuitBreakerOpenException)
                or is_5xx
                or isinstance(e, httpx.RequestError)
            ):
                logger.warning(
                    f"SII Web Service failure or circuit open. Moving DTE {dte_id} "
                    f"to contingency state. Error: {e}"
                )
                dte.status = DTEStatus.CONTINGENCY
                if "signed_xml_bytes" in locals():
                    dte.sii_xml = signed_xml_bytes.decode("ISO-8859-1")
                await db.commit()
                # Return string to indicate contingency state in task
                return "contingency"
            else:
                logger.error(f"Error emitting DTE {dte_id}: {str(e)}")
                dte.status = DTEStatus.ERROR
                await db.commit()
                raise e
        except Exception as e:
            logger.error(f"Error emitting DTE {dte_id}: {str(e)}")
            dte.status = DTEStatus.ERROR
            await db.commit()
            raise e


@celery_app.task(name="tasks.emit_dte", bind=True, max_retries=3)
def emit_dte_task(self, dte_id: str):
    """
    Celery task that acts as a wrapper around the async emission process.
    Handles retries if the SII is down or unresponsive.
    """
    logger.info(f"Starting emission job for DTE {dte_id}")
    try:
        # Run async logic in the sync Celery worker context
        track_id = async_to_sync(process_dte_emission_async)(UUID(dte_id))
        if track_id == "contingency":
            logger.info(
                f"DTE {dte_id} was successfully moved to CONTINGENCY status "
                f"due to SII service outage."
            )
        return track_id
    except Exception as exc:
        logger.error(f"Failed to emit DTE {dte_id}. Retrying... Error: {exc}")
        self.retry(exc=exc, countdown=60)  # Retry in 60s
