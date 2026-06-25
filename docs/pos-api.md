# Generic POS API

## Resumen
La API para Punto de Venta (POS) permite a sistemas de caja externos emitir boletas electrónicas en tiempo real de forma ultra rápida (Boleta 39) y segura.

## Arquitectura Offline-First
Los sistemas POS sufren frecuentemente de inestabilidad de red. Por lo tanto, la integración POS requiere el uso obligatorio del header `Idempotency-Key` (generalmente un UUID o el ID de ticket local del POS).

### Emisión de Ticket
```http
POST /api/v1/integrations/pos/ticket
Authorization: Bearer <API_KEY_POS>
Idempotency-Key: f47ac10b-58cc-4372-a567-0e02b2c3d479
Content-Type: application/json

{
    "cashier_id": "caja_01",
    "ticket_id": "TK-100293",
    "items": [
        { "name": "Coca Cola 3L", "quantity": 1, "unit_price": 2500 }
    ]
}
```

## Respuesta
El endpoint responde en milisegundos con el estado `draft` (o `accepted`) del DTE. Si el POS pierde conexión y reenvía el mismo Ticket, recibirá el DTE ya emitido previamente, evitando una doble facturación.
