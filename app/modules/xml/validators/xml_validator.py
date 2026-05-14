from __future__ import annotations

from lxml import etree

from app.modules.xml.validators.exceptions import XmlValidationError


class XmlValidatorService:
    def validate_well_formed(self, xml_content: str) -> None:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        try:
            etree.fromstring(xml_content.encode("utf-8"), parser=parser)
        except etree.XMLSyntaxError as exc:
            raise XmlValidationError([f"Generated XML is not well formed: {exc}"]) from exc

    def validate_required_nodes(self, xml_content: str) -> None:
        root = etree.fromstring(xml_content.encode("utf-8"))
        ns = {"sii": "http://www.sii.cl/SiiDte"}
        required_xpaths = [
            "/sii:DTE/sii:Documento/sii:Encabezado/sii:IdDoc/sii:TipoDTE",
            "/sii:DTE/sii:Documento/sii:Encabezado/sii:IdDoc/sii:Folio",
            "/sii:DTE/sii:Documento/sii:Encabezado/sii:Emisor/sii:RUTEmisor",
            "/sii:DTE/sii:Documento/sii:Encabezado/sii:Receptor/sii:RUTRecep",
            "/sii:DTE/sii:Documento/sii:Encabezado/sii:Totales/sii:MntTotal",
            "/sii:DTE/sii:Documento/sii:Detalle",
            "/sii:DTE/sii:Documento/sii:TED",
            "/sii:DTE/sii:Documento/sii:TmstFirma",
        ]
        missing = [xpath for xpath in required_xpaths if not root.xpath(xpath, namespaces=ns)]
        if missing:
            raise XmlValidationError([f"Missing required XML node: {xpath}" for xpath in missing])
