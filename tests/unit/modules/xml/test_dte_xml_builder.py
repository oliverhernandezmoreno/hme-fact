from __future__ import annotations

import pytest
from lxml import etree

from app.modules.xml.builders.factory import DTEXmlBuilderFactory
from app.modules.xml.services.dte_mapper import DTEDataMapper
from tests.unit.modules.xml.factories import make_dte

pytestmark = [pytest.mark.unit, pytest.mark.xml]


def test_invoice_xml_builder_generates_sii_ordered_structure() -> None:
    dte = make_dte(33)
    document = DTEDataMapper().to_document_data(dte)
    tree = DTEXmlBuilderFactory().for_type(33).build(document)
    root = tree.getroot()
    ns = {"sii": "http://www.sii.cl/SiiDte"}

    assert root.tag.endswith("DTE")
    assert (
        root.xpath(
            "string(/sii:DTE/sii:Documento/sii:Encabezado/sii:IdDoc/sii:TipoDTE)",
            namespaces=ns,
        )
        == "33"
    )
    assert (
        root.xpath(
            "string(/sii:DTE/sii:Documento/sii:Encabezado/sii:IdDoc/sii:Folio)",
            namespaces=ns,
        )
        == "123"
    )
    assert (
        root.xpath(
            "string(/sii:DTE/sii:Documento/sii:Encabezado/sii:Totales/sii:MntTotal)",
            namespaces=ns,
        )
        == "11900"
    )
    assert root.xpath("/sii:DTE/sii:Documento/sii:TED", namespaces=ns)

    documento_children = [etree.QName(child).localname for child in root[0]]
    assert documento_children == ["Encabezado", "Detalle", "TED", "TmstFirma"]


def test_credit_note_xml_includes_referencia_before_ted() -> None:
    dte = make_dte(61)
    document = DTEDataMapper().to_document_data(dte)
    tree = DTEXmlBuilderFactory().for_type(61).build(document)
    root = tree.getroot()
    ns = {"sii": "http://www.sii.cl/SiiDte"}

    assert (
        root.xpath(
            "string(/sii:DTE/sii:Documento/sii:Referencia/sii:TpoDocRef)",
            namespaces=ns,
        )
        == "33"
    )
    assert (
        root.xpath(
            "string(/sii:DTE/sii:Documento/sii:Referencia/sii:CodRef)",
            namespaces=ns,
        )
        == "1"
    )

    documento_children = [etree.QName(child).localname for child in root[0]]
    assert documento_children == ["Encabezado", "Detalle", "Referencia", "TED", "TmstFirma"]
