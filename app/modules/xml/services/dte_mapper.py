from __future__ import annotations

from app.models import DTE
from app.modules.xml.schemas.dte import (
    DTEDetailData,
    DTEDocumentData,
    DTEIssuerData,
    DTEReceiverData,
    DTEReferenceData,
    DTETotalsData,
)
from app.modules.xml.utils.formatters import sanitize_xml_text


class DTEDataMapper:
    def to_document_data(self, dte: DTE) -> DTEDocumentData:
        company = dte.company
        customer = dte.customer
        if company is None or customer is None:
            raise ValueError("DTE must include company and customer relationships")

        return DTEDocumentData(
            id=f"F{dte.folio}T{dte.dte_type}",
            dte_type=dte.dte_type,
            folio=dte.folio,
            issue_date=dte.issue_date,
            issuer=DTEIssuerData(
                rut=sanitize_xml_text(company.rut),
                legal_name=sanitize_xml_text(company.legal_name),
                giro=sanitize_xml_text(company.giro),
                address=sanitize_xml_text(company.address),
                comuna=sanitize_xml_text(company.comuna),
                city=sanitize_xml_text(company.city),
            ),
            receiver=DTEReceiverData(
                rut=sanitize_xml_text(customer.rut),
                legal_name=sanitize_xml_text(customer.legal_name),
                giro=sanitize_xml_text(customer.giro, fallback="Particular"),
                address=sanitize_xml_text(customer.address),
                comuna=sanitize_xml_text(customer.comuna),
                city=sanitize_xml_text(customer.city),
            ),
            totals=DTETotalsData(
                net_amount=dte.net_amount,
                exempt_amount=dte.exempt_amount,
                tax_amount=dte.tax_amount,
                total_amount=dte.total_amount,
            ),
            details=[
                DTEDetailData(
                    line_number=item.line_number,
                    description=sanitize_xml_text(item.description),
                    quantity=item.quantity,
                    unit=sanitize_xml_text(item.unit, fallback="UN"),
                    unit_price=item.unit_price,
                    discount_amount=item.discount_amount,
                    net_amount=item.net_amount,
                    tax_exempt=item.tax_exempt,
                )
                for item in sorted(dte.items, key=lambda detail: detail.line_number)
            ],
            references=self._map_references(dte),
        )

    def _map_references(self, dte: DTE) -> list[DTEReferenceData]:
        if (
            dte.reference_dte_type is None
            or dte.reference_folio is None
            or dte.reference_date is None
            or dte.reference_code is None
        ):
            return []
        return [
            DTEReferenceData(
                line_number=1,
                referenced_dte_type=dte.reference_dte_type,
                referenced_folio=dte.reference_folio,
                referenced_date=dte.reference_date,
                correction_code=dte.reference_code,
                reason=sanitize_xml_text(dte.reference_reason, fallback="Corrige documento"),
            )
        ]
