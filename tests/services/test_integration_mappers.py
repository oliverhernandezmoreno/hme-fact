import pytest
import uuid
from decimal import Decimal
from app.services.integrations.mappers import OrderToDTEMapper

def test_shopify_mapper_b2c_valid_personal_rut():
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
    assert order.metadata["dte_type"] == 39
    assert order.metadata["fallback_applied"] is False
    
    dte_payload = OrderToDTEMapper.to_dte_payload(order)
    assert dte_payload.dte_type == 39
    assert isinstance(dte_payload.customer_id, uuid.UUID)
    assert len(dte_payload.items) == 2
    assert dte_payload.items[0].quantity == Decimal('1')
    assert dte_payload.items[0].unit_price == Decimal('199.99')


def test_shopify_mapper_b2b_success():
    payload = {
        "id": 820982911946154509,
        "email": "contacto@techcorp.cl",
        "total_price": "1190.00",
        "total_tax": "190.00",
        "customer": {"first_name": "Tech", "last_name": "Corp", "email": "contacto@techcorp.cl"},
        "note_attributes": [
            {"name": "rut", "value": "76123456-0"},
            {"name": "document_type", "value": "factura"}
        ],
        "line_items": [
            {"title": "Suscripción Anual", "quantity": 1, "price": "1000.00"},
            {"title": "Soporte", "quantity": 1, "price": "190.00"}
        ]
    }
    
    order = OrderToDTEMapper.map_shopify_order(payload)
    assert order.customer["rut"] == "76123456-0"
    assert order.metadata["dte_type"] == 33
    assert order.metadata["fallback_applied"] is False
    
    dte_payload = OrderToDTEMapper.to_dte_payload(order)
    assert dte_payload.dte_type == 33


def test_shopify_mapper_fallback_personal_rut():
    # Customer requests Factura but gives a valid Personal RUT (not a business one)
    payload = {
        "id": 820982911946154510,
        "email": "persona@gmail.com",
        "total_price": "119.00",
        "total_tax": "19.00",
        "customer": {"first_name": "Juan", "last_name": "Perez", "email": "persona@gmail.com"},
        "note_attributes": [
            {"name": "rut", "value": "12345678-5"},
            {"name": "document_type", "value": "factura"}
        ],
        "line_items": [
            {"title": "Licuadora", "quantity": 1, "price": "100.00"},
            {"title": "Envio", "quantity": 1, "price": "19.00"}
        ]
    }
    
    order = OrderToDTEMapper.map_shopify_order(payload)
    # Sanitized personal RUT is preserved, but DTE type is downgraded to Boleta (39)
    assert order.customer["rut"] == "12345678-5"
    assert order.metadata["dte_type"] == 39
    assert order.metadata["fallback_applied"] is True
    assert order.metadata["fallback_reason"] == "requested_factura_with_personal_rut"


def test_shopify_mapper_fallback_invalid_rut():
    # Customer requests Factura but provides an invalid RUT
    payload = {
        "id": 820982911946154511,
        "email": "invalid@gmail.com",
        "total_price": "119.00",
        "total_tax": "19.00",
        "customer": {"first_name": "Pedro", "last_name": "Picapiedra", "email": "invalid@gmail.com"},
        "note_attributes": [
            {"name": "rut", "value": "999-invalid"},
            {"name": "document_type", "value": "factura"}
        ],
        "line_items": [
            {"title": "Piedra", "quantity": 1, "price": "100.00"}
        ]
    }
    
    order = OrderToDTEMapper.map_shopify_order(payload)
    # Downgrades to Boleta (39) with generic RUT (66666666-6)
    assert order.customer["rut"] == "66666666-6"
    assert order.metadata["dte_type"] == 39
    assert order.metadata["fallback_applied"] is True
    assert order.metadata["fallback_reason"] == "requested_factura_with_invalid_or_missing_rut"


def test_shopify_mapper_missing_attributes():
    # No note attributes provided at all
    payload = {
        "id": 820982911946154512,
        "email": "anonymous@gmail.com",
        "total_price": "50.00",
        "total_tax": "0.00",
        "customer": {"first_name": "Anon", "last_name": "User"},
        "line_items": [
            {"title": "Servicio", "quantity": 1, "price": "50.00"}
        ]
    }
    
    order = OrderToDTEMapper.map_shopify_order(payload)
    # Defaults to Boleta (39) with generic RUT (66666666-6)
    assert order.customer["rut"] == "66666666-6"
    assert order.metadata["dte_type"] == 39
    assert order.metadata["fallback_applied"] is True

