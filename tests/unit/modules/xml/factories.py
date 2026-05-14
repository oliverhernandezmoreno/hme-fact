from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4


def make_dte(dte_type: int = 33) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        dte_type=dte_type,
        folio=123,
        issue_date=date(2026, 5, 14),
        net_amount=Decimal("10000"),
        exempt_amount=Decimal("0"),
        tax_amount=Decimal("1900"),
        total_amount=Decimal("11900"),
        reference_dte_type=33 if dte_type == 61 else None,
        reference_folio=111 if dte_type == 61 else None,
        reference_date=date(2026, 5, 1) if dte_type == 61 else None,
        reference_code=1 if dte_type == 61 else None,
        reference_reason="Anula documento de referencia" if dte_type == 61 else None,
        company=SimpleNamespace(
            rut="76123456-7",
            legal_name="HME Fact SpA",
            giro="Servicios informaticos",
            address="Av Providencia 123",
            comuna="Providencia",
            city="Santiago",
        ),
        customer=SimpleNamespace(
            rut="76876543-2",
            legal_name="Cliente Demo SpA",
            giro="Comercio",
            address="Alameda 456",
            comuna="Santiago",
            city="Santiago",
        ),
        items=[
            SimpleNamespace(
                line_number=1,
                description="Servicio de facturacion electronica",
                quantity=Decimal("1"),
                unit="UN",
                unit_price=Decimal("10000"),
                discount_amount=Decimal("0"),
                net_amount=Decimal("10000"),
                tax_exempt=False,
            )
        ],
    )
