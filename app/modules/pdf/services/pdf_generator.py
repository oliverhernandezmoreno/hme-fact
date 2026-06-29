from __future__ import annotations

import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import DTE, DTEXmlType
from app.modules.pdf.renderers.reportlab_renderer import ReportLabRenderer
from app.modules.pdf.renderers.xhtml2pdf_renderer import Xhtml2PdfRenderer
from app.modules.pdf.utils.barcode import extract_ted_from_xml, generate_pdf417_base64
from app.services.storage import get_file_storage_service

logger = logging.getLogger(__name__)

DTE_TYPE_NAMES = {
    33: "Factura Electrónica",
    34: "Factura No Afecta o Exenta Electrónica",
    39: "Boleta Electrónica",
    41: "Boleta No Afecta o Exenta Electrónica",
    56: "Nota de Débito Electrónica",
    61: "Nota de Crédito Electrónica",
}


class PdfGeneratorService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.storage = get_file_storage_service()

        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
        )

        if self.settings.PDF_RENDERER == "xhtml2pdf":
            self.renderer = Xhtml2PdfRenderer(self.template_dir)
        else:
            self.renderer = ReportLabRenderer()

    async def generate_pdf(self, dte: DTE) -> bytes:
        # Build template data
        await self.session.refresh(dte, ["company", "customer", "items", "xml_documents"])

        sii_xml_content = None
        for doc in dte.xml_documents:
            if doc.xml_type == DTEXmlType.SIGNED_DTE:
                sii_xml_content = doc.xml_content
                break

        ted_base64 = None
        if sii_xml_content:
            ted_str = extract_ted_from_xml(sii_xml_content)
            if ted_str:
                ted_base64 = generate_pdf417_base64(ted_str)

        template_data = {
            "dte_type_name": DTE_TYPE_NAMES.get(dte.dte_type, f"DTE {dte.dte_type}"),
            "folio": dte.folio,
            "issue_date": dte.issue_date.strftime("%d-%m-%Y") if dte.issue_date else "",
            "issuer": {
                "rut": dte.company.rut if dte.company else "",
                "legal_name": dte.company.legal_name if dte.company else "",
                "giro": getattr(dte.company, "activity_description", "Servicios"),
                "address": getattr(dte.company, "address", ""),
                "comuna": getattr(dte.company, "commune", ""),
                "city": getattr(dte.company, "city", ""),
                "resolution_number": getattr(dte.company, "resolution_number", "0"),
                "resolution_date": getattr(dte.company, "resolution_date", "2014-01-01"),
            },
            "receiver": {
                "rut": dte.customer.rut if dte.customer else "",
                "legal_name": dte.customer.legal_name if dte.customer else "",
                "giro": dte.customer.activity_description if dte.customer else "",
                "address": dte.customer.address if dte.customer else "",
                "comuna": dte.customer.commune if dte.customer else "",
                "city": dte.customer.city if dte.customer else "",
            },
            "items": [
                {
                    "description": item.name,
                    "quantity": item.quantity,
                    "unit": getattr(item, "unit", "UN"),
                    "unit_price": item.price,
                    "discount_amount": getattr(item, "discount", 0),
                    "net_amount": getattr(item, "total", item.price * item.quantity),
                }
                for item in dte.items
            ],
            "totals": {
                "net_amount": dte.net_amount,
                "exempt_amount": dte.exempt_amount,
                "tax_amount": dte.tax_amount,
                "total_amount": dte.total_amount,
            },
            "ted_base64": ted_base64,
            "logo_url": None,  # Could be fetched from storage if needed
        }

        pdf_bytes = self.renderer.render(dte, template_data)

        # Save to storage
        path = f"companies/{dte.company_id}/dtes/{dte.id}/dte_{dte.folio}.pdf"
        await self.storage.save_file(path, pdf_bytes)

        return pdf_bytes
