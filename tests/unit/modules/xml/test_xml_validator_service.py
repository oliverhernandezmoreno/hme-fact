from __future__ import annotations

import pytest
from lxml import etree

from app.modules.xml.builders.factory import DTEXmlBuilderFactory
from app.modules.xml.services.dte_mapper import DTEDataMapper
from app.modules.xml.validators.xml_validator import XmlValidatorService
from tests.unit.modules.xml.factories import make_dte

pytestmark = [pytest.mark.unit, pytest.mark.xml]


def test_xml_validator_accepts_generated_xml() -> None:
    dte = make_dte(39)
    document = DTEDataMapper().to_document_data(dte)
    tree = DTEXmlBuilderFactory().for_type(39).build(document)
    xml_content = etree.tostring(tree, encoding="UTF-8", xml_declaration=True).decode("utf-8")

    validator = XmlValidatorService()
    validator.validate_well_formed(xml_content)
    validator.validate_required_nodes(xml_content)
