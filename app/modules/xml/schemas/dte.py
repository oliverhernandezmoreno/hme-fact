from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DTEIssuerData:
    rut: str
    legal_name: str
    giro: str
    address: str
    comuna: str
    city: str


@dataclass(frozen=True, slots=True)
class DTEReceiverData:
    rut: str
    legal_name: str
    giro: str
    address: str
    comuna: str
    city: str


@dataclass(frozen=True, slots=True)
class DTETotalsData:
    net_amount: Decimal
    exempt_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    iva_rate: Decimal = Decimal("19.00")


@dataclass(frozen=True, slots=True)
class DTEDetailData:
    line_number: int
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    discount_amount: Decimal
    net_amount: Decimal
    tax_exempt: bool


@dataclass(frozen=True, slots=True)
class DTEReferenceData:
    line_number: int
    referenced_dte_type: int
    referenced_folio: int
    referenced_date: date
    correction_code: int
    reason: str


@dataclass(frozen=True, slots=True)
class DTEDocumentData:
    id: str
    dte_type: int
    folio: int
    issue_date: date
    issuer: DTEIssuerData
    receiver: DTEReceiverData
    totals: DTETotalsData
    details: list[DTEDetailData]
    references: list[DTEReferenceData]
