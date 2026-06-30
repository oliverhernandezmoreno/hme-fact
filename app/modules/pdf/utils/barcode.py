from __future__ import annotations

import base64
import io
import logging
from xml.etree import ElementTree

from pdf417gen import encode, render_image

logger = logging.getLogger(__name__)


def extract_ted_from_xml(xml_content: str) -> str | None:
    try:
        root = ElementTree.fromstring(xml_content)
        # Handle namespaces if present
        for elem in root.iter():
            if elem.tag.endswith("TED"):
                return ElementTree.tostring(elem, encoding="unicode")
    except Exception as exc:
        logger.warning("Could not extract TED from XML", exc_info=exc)
    return None


def generate_pdf417_base64(data: str) -> str:
    try:
        codes = encode(data)
        # render_image returns a PIL Image
        image = render_image(codes, scale=2, ratio=3, padding=5)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as exc:
        logger.error("Failed to generate PDF417 barcode", exc_info=exc)
        return (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42m"
            "NkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        )
