from __future__ import annotations

from decimal import Decimal

from app.models import DTE
from app.modules.xml.validators.exceptions import XmlValidationError

SUPPORTED_DTE_TYPES = {33, 39, 61}


class DTEXmlDataValidator:
    def validate(self, dte: DTE) -> None:
        errors: list[str] = []

        if dte.dte_type not in SUPPORTED_DTE_TYPES:
            errors.append(f"Unsupported DTE type for XML generation: {dte.dte_type}")
        if not dte.folio or dte.folio <= 0:
            errors.append("Folio is required and must be greater than zero")
        if dte.issue_date is None:
            errors.append("Issue date is required")
        if dte.company is None:
            errors.append("Issuer company is required")
        if dte.customer is None:
            errors.append("Receiver customer is required")
        if not dte.items:
            errors.append("At least one DTE detail line is required")
        if dte.dte_type == 61:
            self._validate_credit_note_reference(dte, errors)

        self._validate_amount("net_amount", dte.net_amount, errors)
        self._validate_amount("exempt_amount", dte.exempt_amount, errors)
        self._validate_amount("tax_amount", dte.tax_amount, errors)
        self._validate_amount("total_amount", dte.total_amount, errors)

        for item in dte.items:
            if item.line_number <= 0:
                errors.append("Detail line number must be greater than zero")
            if not item.description:
                errors.append(f"Detail line {item.line_number} description is required")
            if len(item.description) > 80:
                errors.append(f"Detail line {item.line_number} description exceeds 80 chars")
            self._validate_amount(f"line {item.line_number} quantity", item.quantity, errors)
            self._validate_amount(f"line {item.line_number} unit_price", item.unit_price, errors)
            self._validate_amount(f"line {item.line_number} net_amount", item.net_amount, errors)
            self._validate_amount(
                f"line {item.line_number} discount_amount",
                item.discount_amount,
                errors,
            )

        if dte.company is not None:
            self._validate_length("RUTEmisor", dte.company.rut, 10, errors)
            self._validate_length("RznSoc", dte.company.legal_name, 100, errors)
            self._validate_length("GiroEmis", dte.company.giro, 80, errors)
        if dte.customer is not None:
            self._validate_length("RUTRecep", dte.customer.rut, 10, errors)
            self._validate_length("RznSocRecep", dte.customer.legal_name, 100, errors)
            self._validate_length("GiroRecep", dte.customer.giro, 40, errors)

        if errors:
            raise XmlValidationError(errors)

    def _validate_amount(
        self,
        field_name: str,
        value: Decimal | int | None,
        errors: list[str],
    ) -> None:
        if value is None:
            errors.append(f"{field_name} is required")
        elif Decimal(value) < 0:
            errors.append(f"{field_name} cannot be negative")

    def _validate_length(
        self,
        field_name: str,
        value: str | None,
        max_length: int,
        errors: list[str],
    ) -> None:
        if not value:
            errors.append(f"{field_name} is required")
        elif len(value) > max_length:
            errors.append(f"{field_name} exceeds {max_length} chars")

    def _validate_credit_note_reference(self, dte: DTE, errors: list[str]) -> None:
        if dte.reference_dte_type is None:
            errors.append("Credit note reference_dte_type is required")
        if dte.reference_folio is None:
            errors.append("Credit note reference_folio is required")
        if dte.reference_date is None:
            errors.append("Credit note reference_date is required")
        if dte.reference_code not in {1, 2, 3}:
            errors.append("Credit note reference_code must be 1, 2 or 3")
        if not dte.reference_reason:
            errors.append("Credit note reference_reason is required")
