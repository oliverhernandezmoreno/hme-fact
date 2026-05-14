from __future__ import annotations

from app.modules.xml.builders.boleta_builder import BoletaXmlBuilder
from app.modules.xml.builders.credit_note_builder import CreditNoteXmlBuilder
from app.modules.xml.builders.dte_builder import DTEXmlBuilder
from app.modules.xml.builders.invoice_builder import InvoiceXmlBuilder


class DTEXmlBuilderFactory:
    def __init__(self) -> None:
        self._builders: tuple[DTEXmlBuilder, ...] = (
            InvoiceXmlBuilder(),
            BoletaXmlBuilder(),
            CreditNoteXmlBuilder(),
        )

    def for_type(self, dte_type: int) -> DTEXmlBuilder:
        for builder in self._builders:
            if builder.supports(dte_type):
                return builder
        raise ValueError(f"No XML builder registered for DTE type {dte_type}")
