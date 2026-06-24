from __future__ import annotations

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.models import DTE
from app.modules.pdf.renderers.base import BasePdfRenderer


class ReportLabRenderer(BasePdfRenderer):
    def render(self, dte: DTE, template_data: dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"Documento Tributario Electrónico - {dte.folio}", styles["Title"]))
        elements.append(Spacer(1, 12))
        
        issuer = template_data.get("issuer", {})
        elements.append(Paragraph(f"Emisor: {issuer.get('legal_name')}", styles["Normal"]))
        elements.append(Paragraph(f"RUT: {issuer.get('rut')}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        receiver = template_data.get("receiver", {})
        elements.append(Paragraph(f"Receptor: {receiver.get('legal_name')}", styles["Normal"]))
        elements.append(Paragraph(f"RUT: {receiver.get('rut')}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        data = [["Descripción", "Cantidad", "Precio Unitario", "Total"]]
        for item in template_data.get("items", []):
            data.append([
                str(item.get("description", "")),
                str(item.get("quantity", "")),
                f"${item.get('unit_price', 0)}",
                f"${item.get('net_amount', 0)}"
            ])

        table = Table(data, colWidths=[200, 80, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        totals = template_data.get("totals", {})
        elements.append(Paragraph(f"Neto: ${totals.get('net_amount', 0)}", styles["Normal"]))
        elements.append(Paragraph(f"IVA: ${totals.get('tax_amount', 0)}", styles["Normal"]))
        elements.append(Paragraph(f"Total: ${totals.get('total_amount', 0)}", styles["Heading3"]))

        doc.build(elements)
        return buffer.getvalue()
