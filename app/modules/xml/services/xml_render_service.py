from __future__ import annotations

import logging

from lxml import etree
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DTE, DTEXmlType
from app.modules.xml.builders.factory import DTEXmlBuilderFactory
from app.modules.xml.services.dte_mapper import DTEDataMapper
from app.modules.xml.validators.dte_validator import DTEXmlDataValidator
from app.modules.xml.validators.xml_validator import XmlValidatorService
from app.repositories.dte_xml import DTEXmlRepository

logger = logging.getLogger(__name__)


class XmlRenderService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        builder_factory: DTEXmlBuilderFactory | None = None,
        data_validator: DTEXmlDataValidator | None = None,
        xml_validator: XmlValidatorService | None = None,
        mapper: DTEDataMapper | None = None,
    ) -> None:
        self.session = session
        self.builder_factory = builder_factory or DTEXmlBuilderFactory()
        self.data_validator = data_validator or DTEXmlDataValidator()
        self.xml_validator = xml_validator or XmlValidatorService()
        self.mapper = mapper or DTEDataMapper()
        self.xml_repository = DTEXmlRepository(session)

    async def generate_and_store_dte_xml(self, dte: DTE) -> str:
        logger.info("Starting DTE XML generation", extra={"dte_id": str(dte.id)})
        self.data_validator.validate(dte)
        document_data = self.mapper.to_document_data(dte)
        builder = self.builder_factory.for_type(dte.dte_type)
        tree = builder.build(document_data)
        xml_content = self._serialize(tree)
        self.xml_validator.validate_well_formed(xml_content)
        self.xml_validator.validate_required_nodes(xml_content)

        await self.xml_repository.create(
            {
                "dte_id": dte.id,
                "xml_content": xml_content,
                "xml_type": DTEXmlType.UNSIGNED_DTE,
            }
        )
        logger.info("Stored DTE XML", extra={"dte_id": str(dte.id), "dte_type": dte.dte_type})
        return xml_content

    def _serialize(self, tree: etree._ElementTree) -> str:
        return etree.tostring(
            tree,
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        ).decode("utf-8")
