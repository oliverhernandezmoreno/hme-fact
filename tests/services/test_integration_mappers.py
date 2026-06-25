import pytest
from app.services.integrations.mappers import OrderToDTEMapper

def test_shopify_mapper_b2c():
    payload = {
        "id": 820982911946154508,
        "email": "jon@doe.ca",
        "total_price": "239.94",
        "total_tax": "38.31",
        "customer": {"first_name": "Jon", "last_name": "Doe", "email": "jon@doe.ca"},
        "note_attributes": [{"name": "rut", "value": "12345678-5"}],
        "line_items": [
            {"title": "Zapatos", "quantity": 1, "price": "199.99"},
            {"title": "Envío", "quantity": 1, "price": "39.95"}
        ]
    }
    
    order = OrderToDTEMapper.map_shopify_order(payload)
    
    assert order.source == "shopify"
    assert order.idempotency_key == "820982911946154508"
    assert order.total_amount == 239.94
    assert order.tax_amount == 38.31
    assert order.net_amount == 201.63
    assert order.customer["rut"] == "12345678-5"
    assert len(order.items) == 2
    assert order.items[0]["name"] == "Zapatos"
    
    dte_payload = OrderToDTEMapper.to_dte_payload(order)
    assert dte_payload.dte_type == "39"
    assert dte_payload.customer_id == "12345678-5"
    assert len(dte_payload.items) == 2
    assert dte_payload.items[0].quantity == 1
    assert dte_payload.items[0].unit_price == 199.99
