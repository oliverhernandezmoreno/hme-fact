from __future__ import annotations

from lxml import etree

from app.modules.xml.schemas.types import SiiXmlNamespaces


def sii_tag(name: str) -> str:
    return f"{{{SiiXmlNamespaces.DTE}}}{name}"


def append_text(parent: etree._Element, name: str, value: object | None) -> etree._Element:
    child = etree.SubElement(parent, sii_tag(name))
    child.text = "" if value is None else str(value)
    return child
