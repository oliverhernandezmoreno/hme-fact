from __future__ import annotations

from app.modules.xml.builders.dte_builder import DTEXmlBuilder


class CreditNoteXmlBuilder(DTEXmlBuilder):
    document_type = 61

    def supports(self, dte_type: int) -> bool:
        return dte_type == self.document_type
