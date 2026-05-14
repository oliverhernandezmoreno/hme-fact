from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from lxml import etree

from app.modules.xml.schemas.dte import DTEDetailData, DTEDocumentData
from app.modules.xml.schemas.types import SiiXmlNamespaces
from app.modules.xml.utils.elements import append_text, sii_tag
from app.modules.xml.utils.formatters import (
    format_date,
    format_sii_amount,
    format_sii_decimal,
    format_timestamp,
)


class DTEXmlBuilder(ABC):
    document_type: int

    def build(self, document: DTEDocumentData) -> etree._ElementTree:
        root = etree.Element(
            sii_tag("DTE"),
            nsmap={None: SiiXmlNamespaces.DTE, "ds": SiiXmlNamespaces.DSIG},
            version="1.0",
        )
        documento = etree.SubElement(root, sii_tag("Documento"), ID=document.id)
        self._append_header(documento, document)
        for detail in document.details:
            self._append_detail(documento, detail)
        self._append_references(documento, document)
        self._append_ted_placeholder(documento, document)
        append_text(documento, "TmstFirma", format_timestamp())
        return etree.ElementTree(root)

    def _append_header(self, parent: etree._Element, document: DTEDocumentData) -> None:
        encabezado = etree.SubElement(parent, sii_tag("Encabezado"))
        self._append_id_doc(encabezado, document)
        self._append_issuer(encabezado, document)
        self._append_receiver(encabezado, document)
        self._append_totals(encabezado, document)

    def _append_id_doc(self, encabezado: etree._Element, document: DTEDocumentData) -> None:
        id_doc = etree.SubElement(encabezado, sii_tag("IdDoc"))
        append_text(id_doc, "TipoDTE", document.dte_type)
        append_text(id_doc, "Folio", document.folio)
        append_text(id_doc, "FchEmis", format_date(document.issue_date))
        self._append_type_specific_id_doc(id_doc, document)

    def _append_issuer(self, encabezado: etree._Element, document: DTEDocumentData) -> None:
        emisor = etree.SubElement(encabezado, sii_tag("Emisor"))
        append_text(emisor, "RUTEmisor", document.issuer.rut)
        append_text(emisor, "RznSoc", document.issuer.legal_name)
        append_text(emisor, "GiroEmis", document.issuer.giro)
        append_text(emisor, "DirOrigen", document.issuer.address)
        append_text(emisor, "CmnaOrigen", document.issuer.comuna)
        append_text(emisor, "CiudadOrigen", document.issuer.city)

    def _append_receiver(self, encabezado: etree._Element, document: DTEDocumentData) -> None:
        receptor = etree.SubElement(encabezado, sii_tag("Receptor"))
        append_text(receptor, "RUTRecep", document.receiver.rut)
        append_text(receptor, "RznSocRecep", document.receiver.legal_name)
        append_text(receptor, "GiroRecep", document.receiver.giro)
        append_text(receptor, "DirRecep", document.receiver.address)
        append_text(receptor, "CmnaRecep", document.receiver.comuna)
        append_text(receptor, "CiudadRecep", document.receiver.city)

    def _append_totals(self, encabezado: etree._Element, document: DTEDocumentData) -> None:
        totals = etree.SubElement(encabezado, sii_tag("Totales"))
        if document.totals.net_amount > 0:
            append_text(totals, "MntNeto", format_sii_amount(document.totals.net_amount))
        if document.totals.exempt_amount > 0:
            append_text(totals, "MntExe", format_sii_amount(document.totals.exempt_amount))
        if self._requires_iva(document):
            append_text(totals, "TasaIVA", format_sii_decimal(document.totals.iva_rate))
            append_text(totals, "IVA", format_sii_amount(document.totals.tax_amount))
        append_text(totals, "MntTotal", format_sii_amount(document.totals.total_amount))

    def _append_detail(self, parent: etree._Element, detail: DTEDetailData) -> None:
        detalle = etree.SubElement(parent, sii_tag("Detalle"))
        append_text(detalle, "NroLinDet", detail.line_number)
        if detail.tax_exempt:
            append_text(detalle, "IndExe", 1)
        append_text(detalle, "NmbItem", detail.description[:80])
        append_text(detalle, "QtyItem", format_sii_decimal(detail.quantity))
        append_text(detalle, "UnmdItem", detail.unit)
        append_text(detalle, "PrcItem", format_sii_decimal(detail.unit_price))
        if detail.discount_amount > Decimal("0"):
            append_text(detalle, "DescuentoMonto", format_sii_amount(detail.discount_amount))
        append_text(detalle, "MontoItem", format_sii_amount(detail.net_amount))

    def _append_ted_placeholder(self, parent: etree._Element, document: DTEDocumentData) -> None:
        ted = etree.SubElement(parent, sii_tag("TED"), version="1.0")
        dd = etree.SubElement(ted, sii_tag("DD"))
        append_text(dd, "RE", document.issuer.rut)
        append_text(dd, "TD", document.dte_type)
        append_text(dd, "F", document.folio)
        append_text(dd, "FE", format_date(document.issue_date))
        append_text(dd, "RR", document.receiver.rut)
        append_text(dd, "RSR", document.receiver.legal_name[:40])
        append_text(dd, "MNT", format_sii_amount(document.totals.total_amount))
        append_text(dd, "IT1", document.details[0].description[:40])
        append_text(dd, "CAF", "CAF_PLACEHOLDER")
        append_text(dd, "TSTED", format_timestamp())
        frmt = etree.SubElement(ted, sii_tag("FRMT"), algoritmo="SHA1withRSA")
        frmt.text = "TED_SIGNATURE_PLACEHOLDER"

    def _append_references(self, parent: etree._Element, document: DTEDocumentData) -> None:
        for reference in document.references:
            referencia = etree.SubElement(parent, sii_tag("Referencia"))
            append_text(referencia, "NroLinRef", reference.line_number)
            append_text(referencia, "TpoDocRef", reference.referenced_dte_type)
            append_text(referencia, "FolioRef", reference.referenced_folio)
            append_text(referencia, "FchRef", format_date(reference.referenced_date))
            append_text(referencia, "CodRef", reference.correction_code)
            append_text(referencia, "RazonRef", reference.reason[:90])

    def _requires_iva(self, document: DTEDocumentData) -> bool:
        return document.totals.tax_amount > 0

    def _append_type_specific_id_doc(
        self,
        id_doc: etree._Element,
        document: DTEDocumentData,
    ) -> None:
        return None

    @abstractmethod
    def supports(self, dte_type: int) -> bool:
        raise NotImplementedError
