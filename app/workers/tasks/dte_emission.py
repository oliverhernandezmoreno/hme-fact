import asyncio
import logging
from uuid import UUID

from asgiref.sync import async_to_sync
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.workers.celery_app import celery_app
from app.db.session import async_session_maker
from app.models.dte import DTE
from app.models.company import Company
from app.models.caf_file import CAFFile
from app.models.certificate import Certificate
from app.models.enums import DTEStatus, DTEType
from app.services.sii.builder import DTEBuilder
from app.services.sii.signer import SIISigner
from app.services.sii.client import SIIWebServicesClient
from app.services.pdf_generator import PDFGenerator
from app.services.certificate_security import CertificateSecurityService

logger = logging.getLogger(__name__)

async def process_dte_emission_async(dte_id: UUID) -> str:
    """Core asynchronous logic to emit a DTE to the SII."""
    
    async with async_session_maker() as db:
        # 1. Fetch DTE with all relationships
        dte_result = await db.execute(
            select(DTE)
            .where(DTE.id == dte_id)
            .options(
                selectinload(DTE.items),
                selectinload(DTE.customer),
                selectinload(DTE.company),
                selectinload(DTE.caf_file)
            )
        )
        dte = dte_result.scalars().first()
        
        if not dte:
            raise ValueError(f"DTE {dte_id} not found.")
            
        if dte.status != DTEStatus.DRAFT:
            raise ValueError(f"DTE {dte_id} is not in DRAFT status.")

        company = dte.company
        
        try:
            # 2. Fetch Active Digital Certificate
            cert_result = await db.execute(
                select(Certificate).where(
                    Certificate.company_id == company.id,
                    Certificate.is_active == True
                )
            )
            certificate = cert_result.scalars().first()
            if not certificate:
                raise ValueError("No active digital certificate found for company.")
                
            pfx_data, pfx_password = CertificateSecurityService.decrypt_certificate(
                certificate.encrypted_data, 
                certificate.encrypted_password
            )

            # 3. Build the XML Structure using the CAF
            if not dte.caf_file:
                raise ValueError("DTE does not have an assigned CAF file.")
                
            # Prepare dictionary data for the builder
            dte_data = {
                "dte_type": dte.dte_type.value,
                "folio": dte.folio,
                "issue_date": dte.issue_date.isoformat(),
                "rut_emisor": company.rut,
                "razon_social_emisor": company.legal_name,
                "giro_emisor": company.business_activity,
                "direccion_emisor": company.address,
                "comuna_emisor": company.commune,
                "rut_receptor": dte.customer.rut if dte.customer else "1-9",
                "razon_social_receptor": dte.customer.legal_name if dte.customer else "Sin Cliente",
                "monto_neto": dte.net_amount,
                "tasa_iva": dte.vat_rate,
                "monto_iva": dte.vat_amount,
                "monto_total": dte.total_amount,
                "items": [
                    {
                        "nombre": item.name,
                        "cantidad": float(item.quantity),
                        "precio_unitario": float(item.unit_price),
                        "monto_item": float(item.total_amount)
                    } for item in dte.items
                ],
                "caf_xml": dte.caf_file.xml_content,
                "caf_private_key": dte.caf_file.private_key
            }

            # Generate basic XML with TED
            xml_tree = DTEBuilder.build_dte_xml(dte_data)
            
            # 4. Sign the entire document
            signer = SIISigner()
            signed_xml_bytes = signer.sign_dte(xml_tree, pfx_data, pfx_password, f"DOC_{dte.folio}")

            # 5. Send to SII using Client
            sii_client = SIIWebServicesClient(environment="certification")
            token = await sii_client.get_token(pfx_data, pfx_password)
            
            # Assuming certificate owner RUT is needed (usually extracted from Cert, hardcoded for now)
            # In a real scenario, the RUT owner is stored when uploading the cert
            cert_owner_rut = company.rut 
            
            track_id = await sii_client.enviar_dte(signed_xml_bytes, token, cert_owner_rut, company.rut)

            # 6. Generate PDF for the Client
            pdf_bytes = PDFGenerator.generate_invoice_pdf(dte_data, f"DOC_{dte.folio}")
            
            # 7. Update DB states
            dte.status = DTEStatus.SENT
            dte.sii_track_id = track_id
            
            # Persist the signed XML and PDF in storage (mocked here, we would use S3/Local storage)
            # Example: storage_service.save_pdf(pdf_bytes)
            
            await db.commit()
            
            logger.info(f"Successfully emitted DTE {dte.folio}. Track ID: {track_id}")
            return track_id

        except Exception as e:
            logger.error(f"Error emitting DTE {dte_id}: {str(e)}")
            dte.status = DTEStatus.FAILED
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
        return track_id
    except Exception as exc:
        logger.error(f"Failed to emit DTE {dte_id}. Retrying... Error: {exc}")
        self.retry(exc=exc, countdown=60) # Retry in 60s
