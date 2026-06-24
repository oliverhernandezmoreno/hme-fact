from __future__ import annotations

import io
import logging
from typing import Any

from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

from app.models import DTE
from app.modules.pdf.renderers.base import BasePdfRenderer

logger = logging.getLogger(__name__)


class Xhtml2PdfRenderer(BasePdfRenderer):
    def __init__(self, template_dir: str) -> None:
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render(self, dte: DTE, template_data: dict[str, Any]) -> bytes:
        template = self.env.get_template("invoice.html")
        html_content = template.render(**template_data)
        
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.StringIO(html_content), result)
        if pdf.err:
            logger.error("Error rendering PDF with xhtml2pdf")
            raise RuntimeError("Failed to generate PDF")
        
        return result.getvalue()
