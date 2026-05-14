from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal


def format_date(value: date) -> str:
    return value.isoformat()


def format_timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(UTC)
    return current.isoformat(timespec="seconds")


def format_sii_amount(value: Decimal | int) -> str:
    decimal_value = Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return str(int(decimal_value))


def format_sii_decimal(value: Decimal, places: str = "0.######") -> str:
    normalized = value.normalize()
    return format(normalized, "f")


def sanitize_xml_text(value: str | None, *, fallback: str = "") -> str:
    return (value or fallback).strip()
