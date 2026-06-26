import io
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime

from pdf417gen import encode, render_image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class PDFGenerator:
    """
    Service for generating a standard Chilean DTE PDF visualization.
    Uses reportlab for fast PDF creation and pdf417gen for the TED barcode.
    """

    @staticmethod
    def _generate_ted_barcode(ted_xml_string: str) -> str:
        """
        Generates the PDF417 barcode image for the TED and returns it as a temporary file path.
        """
        # TED string must be ISO-8859-1 as per SII specification
        codes = encode(ted_xml_string, columns=10, security_level=5)
        # Render barcode as an image
        image = render_image(codes, scale=2, padding=10)
        
        # Save to a temporary file because ReportLab expects a file path or file-like object
        temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image.save(temp_img, format="PNG")
        temp_img.close()
        
        return temp_img.name

    @staticmethod
    def generate_dte_pdf(dte_data: dict, ted_xml_string: str) -> bytes:
        """
        Generates a PDF byte string for a given DTE.
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # --- 1. Header Information ---
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 50, dte_data.get("emisor_name", "EMPRESA DE PRUEBA"))
        
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 70, f"Giro: {dte_data.get('emisor_giro', 'Venta al por menor')}")
        c.drawString(40, height - 85, f"Dirección: {dte_data.get('emisor_address', 'Calle Falsa 123, Santiago')}")
        
        # --- 2. DTE Type & Folio (Red Box on Top Right) ---
        c.setStrokeColorRGB(1, 0, 0)
        c.setLineWidth(2)
        c.roundRect(width - 200, height - 100, 160, 60, 5, stroke=1, fill=0)
        
        c.setFillColorRGB(1, 0, 0)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width - 120, height - 60, f"R.U.T.: {dte_data.get('emisor_rut', '11111111-1')}")
        c.drawCentredString(width - 120, height - 75, "FACTURA ELECTRÓNICA" if dte_data.get("dte_type") == 33 else "DOCUMENTO ELECTRÓNICO")
        c.drawCentredString(width - 120, height - 90, f"N° {dte_data.get('folio', '123')}")
        
        c.setFillColorRGB(0, 0, 0)

        # --- 3. Customer Information ---
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 130, f"Señor(es): {dte_data.get('receptor_name', 'Cliente Ficticio')}")
        c.drawString(40, height - 145, f"R.U.T.: {dte_data.get('receptor_rut', '22222222-2')}")
        c.drawString(40, height - 160, f"Fecha Emisión: {dte_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))}")

        # --- 4. Items Table ---
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
        c.line(40, height - 180, width - 40, height - 180)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(45, height - 195, "Descripción")
        c.drawString(300, height - 195, "Cantidad")
        c.drawString(400, height - 195, "Precio Unitario")
        c.drawString(500, height - 195, "Total")
        
        c.line(40, height - 200, width - 40, height - 200)

        # Draw Items
        c.setFont("Helvetica", 9)
        y_pos = height - 215
        for item in dte_data.get("items", []):
            c.drawString(45, y_pos, str(item.get("name", "Producto")))
            c.drawString(300, y_pos, str(item.get("quantity", 1)))
            c.drawString(400, y_pos, f"${item.get('unit_price', 0):,.0f}")
            c.drawString(500, y_pos, f"${item.get('total_amount', 0):,.0f}")
            y_pos -= 15
            
        # --- 5. Totals ---
        y_pos -= 20
        c.setFont("Helvetica-Bold", 10)
        c.drawString(400, y_pos, "Monto Neto:")
        c.drawString(500, y_pos, f"${dte_data.get('net_amount', 0):,.0f}")
        
        y_pos -= 15
        c.drawString(400, y_pos, "IVA 19%:")
        c.drawString(500, y_pos, f"${dte_data.get('tax_amount', 0):,.0f}")
        
        y_pos -= 15
        c.drawString(400, y_pos, "Total:")
        c.drawString(500, y_pos, f"${dte_data.get('total_amount', 0):,.0f}")

        # --- 6. Barcode TED (Timbre Electrónico) ---
        if ted_xml_string:
            barcode_img_path = PDFGenerator._generate_ted_barcode(ted_xml_string)
            c.drawImage(barcode_img_path, (width / 2) - 100, 150, width=200, height=80, preserveAspectRatio=True)
            
            c.setFont("Helvetica", 7)
            c.drawCentredString(width / 2, 135, "Timbre Electrónico SII")
            c.drawCentredString(width / 2, 125, "Res. 80 de 2014 - Verifique documento: www.sii.cl")

        # Finish up
        c.showPage()
        c.save()

        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
