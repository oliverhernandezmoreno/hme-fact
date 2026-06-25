# ERP Connector Genérico

## Resumen
Permite a sistemas ERP robustos (ej. SAP B1, Softland, Defontana) delegar exclusivamente el motor de facturación electrónica a hmEFact.

## External ID Mapping
Un ERP tiene sus propios identificadores para Clientes (`C-0012`) y Productos (`SKU-491`).
hmEFact guarda estos cruces en la tabla `external_mappings`.

Cuando el ERP envía una orden:
```json
{
    "external_customer_id": "C-0012",
    "external_order_id": "ERP-99121",
    "lines": [
        { "external_product_id": "SKU-491", "qty": 10 }
    ]
}
```
Los Mappers de hmEFact traducirán automáticamente `C-0012` al UUID interno del `Customer` usando el `connection_id` del ERP, emitiendo el DTE con la data de facturación realizada previamente en la sincronización.
