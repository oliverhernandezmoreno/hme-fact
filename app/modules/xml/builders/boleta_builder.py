from __future__ import annotations

from lxml import etree

from app.modules.xml.builders.dte_builder import DTEXmlBuilder
from app.modules.xml.schemas.dte import DTEDocumentData
from app.modules.xml.utils.elements import append_text


class BoletaXmlBuilder(DTEXmlBuilder):
    document_type = 39

    def supports(self, dte_type: int) -> bool:
        return dte_type == self.document_type

    def _append_type_specific_id_doc(
        self,
        id_doc: etree._Element,
        document: DTEDocumentData,
    ) -> None:
        append_text(id_doc, "IndServicio", 3)
