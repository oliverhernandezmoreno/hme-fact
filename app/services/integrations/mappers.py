import uuid
from typing import Any, Dict
from datetime import date

from app.schemas.integration import ExternalOrderPayload
from app.schemas.dte import DTECreate, DTEItemCreate


class OrderToDTEMapper:
    @staticmethod
    def map_shopify_order(payload: Dict[str, Any]) -> ExternalOrderPayload:
        return ExternalOrderPayload(
            idempotency_key=str(payload.get("id")),
            source="shopify",
            external_order_id=str(payload.get("id")),
            customer={
                "name": payload.get("customer", {}).get("first_name", "Cliente"),
                "email": payload.get("customer", {}).get("email", ""),
                "rut": payload.get("note_attributes", [{"name": "rut", "value": "11111111-1"}])[0]["value"]
            },
            items=[{
                "name": item.get("title"),
                "quantity": item.get("quantity"),
                "unit_price": float(item.get("price"))
            } for item in payload.get("line_items", [])],
            total_amount=float(payload.get("total_price", 0)),
            tax_amount=float(payload.get("total_tax", 0)),
            net_amount=float(payload.get("total_price", 0)) - float(payload.get("total_tax", 0)),
        )

    @staticmethod
    def to_dte_payload(order: ExternalOrderPayload) -> DTECreate:
        return DTECreate(
            dte_type=39, # Boleta by default for B2C
            customer_id=uuid.uuid4(), # Should map to internal ID
            items=[
                DTEItemCreate(
                    description=item["name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"]
                ) for item in order.items
            ],
            issue_date=date.today(),
        )
