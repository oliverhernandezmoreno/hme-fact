import pytest
from datetime import date
from app.services.sii.caf_parser import CAFParser, CAFParserError


def test_caf_parser_success():
    valid_xml = b"""
    <AUTORIZACION>
        <CAF>
            <DA>
                <RE>76123456-7</RE>
                <RS>TechCorp Chile SpA</RS>
                <TD>33</TD>
                <RNG>
                    <D>1</D>
                    <H>100</H>
                </RNG>
                <FA>2026-06-26</FA>
            </DA>
        </CAF>
        <RSASK>
            -----BEGIN RSA PRIVATE KEY-----
            MOCK_PRIVATE_KEY_CONTENT
            -----END RSA PRIVATE KEY-----
        </RSASK>
    </AUTORIZACION>
    """
    res = CAFParser.parse(valid_xml)
    assert res["rut_emisor"] == "76123456-7"
    assert res["razon_social"] == "TechCorp Chile SpA"
    assert res["dte_type"] == 33
    assert res["folio_from"] == 1
    assert res["folio_to"] == 100
    assert res["authorization_date"] == date(2026, 6, 26)
    assert "MOCK_PRIVATE_KEY_CONTENT" in res["private_key"]
    assert "<CAF>" in res["caf_xml_content"]


def test_caf_parser_invalid_xml():
    with pytest.raises(CAFParserError, match="Archivo XML malformado"):
        CAFParser.parse(b"<invalid-xml")


def test_caf_parser_missing_da():
    xml = b"""
    <AUTORIZACION>
        <CAF>
        </CAF>
        <RSASK>KEY</RSASK>
    </AUTORIZACION>
    """
    with pytest.raises(CAFParserError, match="No se encontró el nodo <DA>"):
        CAFParser.parse(xml)


def test_caf_parser_missing_fields():
    xml = b"""
    <AUTORIZACION>
        <CAF>
            <DA>
                <RE>76123456-7</RE>
                <TD>33</TD>
            </DA>
        </CAF>
        <RSASK>KEY</RSASK>
    </AUTORIZACION>
    """
    with pytest.raises(CAFParserError, match="Faltan campos obligatorios en el nodo <DA>"):
        CAFParser.parse(xml)


def test_caf_parser_missing_rsask():
    xml = b"""
    <AUTORIZACION>
        <CAF>
            <DA>
                <RE>76123456-7</RE>
                <RS>TechCorp Chile SpA</RS>
                <TD>33</TD>
                <RNG>
                    <D>1</D>
                    <H>100</H>
                </RNG>
                <FA>2026-06-26</FA>
            </DA>
        </CAF>
    </AUTORIZACION>
    """
    with pytest.raises(CAFParserError, match="No se encontró la Llave Privada <RSASK>"):
        CAFParser.parse(xml)


def test_caf_parser_missing_caf_block():
    xml = b"""
    <AUTORIZACION>
        <DA>
            <RE>76123456-7</RE>
            <RS>TechCorp Chile SpA</RS>
            <TD>33</TD>
            <RNG>
                <D>1</D>
                <H>100</H>
            </RNG>
            <FA>2026-06-26</FA>
        </DA>
        <RSASK>KEY</RSASK>
    </AUTORIZACION>
    """
    with pytest.raises(CAFParserError, match="No se encontró el nodo <CAF>"):
        # Since DA is searched inside root, it might find DA even if CAF is missing,
        # but the check for CAF node is later.
        CAFParser.parse(xml)
