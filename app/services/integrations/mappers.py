import re
import uuid
from datetime import date
from typing import Any

from app.schemas.dte import DTECreate, DTEItemCreate
from app.schemas.integration import ExternalOrderPayload


def clean_rut(rut_str: str) -> str:
    if not rut_str:
        return ""
    # Remove dots, dashes, spaces and convert to uppercase
    cleaned = re.sub(r"[^0-9kK]", "", str(rut_str)).upper()
    if len(cleaned) < 2:
        return ""
    # Put dash before the last character (verifier digit)
    return f"{cleaned[:-1]}-{cleaned[-1]}"


def validate_rut(rut_str: str) -> bool:
    cleaned = clean_rut(rut_str)
    if not cleaned:
        return False
    # Regex check: 7 or 8 digits followed by dash and a digit or 'K'
    if not re.match(r"^\d{7,8}-[0-9K]$", cleaned):
        return False

    # Check verifier digit (modulo 11)
    num_part, dv = cleaned.split("-")
    try:
        reversed_digits = map(int, reversed(num_part))
        factors = [2, 3, 4, 5, 6, 7]
        total = 0
        for i, d in enumerate(reversed_digits):
            total += d * factors[i % len(factors)]

        expected_dv = 11 - (total % 11)
        if expected_dv == 11:
            expected_dv_char = "0"
        elif expected_dv == 10:
            expected_dv_char = "K"
        else:
            expected_dv_char = str(expected_dv)

        return dv == expected_dv_char
    except ValueError:
        return False


def is_business_rut(rut_str: str) -> bool:
    cleaned = clean_rut(rut_str)
    if not cleaned or not validate_rut(cleaned):
        return False
    num_part = cleaned.split("-")[0]
    try:
        num = int(num_part)
        # Business RUTs (personas jurídicas) in Chile are typically between 50,000,000 and 99,999,999
        return 50000000 <= num <= 99999999
    except ValueError:
        return False


class OrderToDTEMapper:
    @staticmethod
    def map_shopify_order(payload: dict[str, Any]) -> ExternalOrderPayload:
        note_attributes = payload.get("note_attributes", [])

        # Helper to retrieve case-insensitive attribute value
        def get_attr(name: str, default: Any = None) -> Any:
            for attr in note_attributes:
                if isinstance(attr, dict) and attr.get("name", "").lower() == name.lower():
                    return attr.get("value", default)
            return default

        # Extract RUT and Document Type
        raw_rut = get_attr("rut")
        requested_doc_type = get_attr("document_type", "boleta").lower()

        # Sanitize and validate
        original_rut = raw_rut
        fallback_applied = False
        fallback_reason = None

        cleaned = clean_rut(raw_rut)
        is_valid = validate_rut(cleaned)
        is_business = is_business_rut(cleaned) if is_valid else False

        # Determine target DTE type and final RUT
        if requested_doc_type == "factura":
            if is_valid and is_business:
                # Valid company: issue Factura
                final_rut = cleaned
                dte_type = 33
            else:
                # Invalid/missing or personal RUT: fallback to Boleta (39) with generic/personal RUT
                dte_type = 39
                fallback_applied = True
                if is_valid:
                    final_rut = cleaned
                    fallback_reason = "requested_factura_with_personal_rut"
                else:
                    final_rut = "66666666-6"
                    fallback_reason = "requested_factura_with_invalid_or_missing_rut"
        else:  # Default to boleta
            dte_type = 39
            if is_valid:
                final_rut = cleaned
            else:
                final_rut = "66666666-6"
                fallback_applied = True
                fallback_reason = "missing_or_invalid_rut_for_boleta"

        return ExternalOrderPayload(
            idempotency_key=str(payload.get("id")),
            source="shopify",
            external_order_id=str(payload.get("id")),
            customer={
                "name": payload.get("customer", {}).get("first_name", "Cliente"),
                "email": payload.get("customer", {}).get("email", ""),
                "rut": final_rut,
            },
            items=[
                {
                    "name": item.get("title"),
                    "quantity": item.get("quantity"),
                    "unit_price": float(item.get("price")),
                }
                for item in payload.get("line_items", [])
            ],
            total_amount=float(payload.get("total_price", 0)),
            tax_amount=float(payload.get("total_tax", 0)),
            net_amount=float(payload.get("total_price", 0)) - float(payload.get("total_tax", 0)),
            metadata={
                "dte_type": dte_type,
                "original_document_type": requested_doc_type,
                "original_rut": original_rut,
                "fallback_applied": fallback_applied,
                "fallback_reason": fallback_reason,
            },
        )

    @staticmethod
    def to_dte_payload(order: ExternalOrderPayload) -> DTECreate:
        dte_type = order.metadata.get("dte_type", 39)
        return DTECreate(
            dte_type=dte_type,
            customer_id=uuid.uuid4(),  # Mock or dynamically lookup customer
            items=[
                DTEItemCreate(
                    description=item["name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                )
                for item in order.items
            ],
            issue_date=date.today(),
        )
