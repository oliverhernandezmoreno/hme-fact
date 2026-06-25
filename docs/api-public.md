# API Pública — hmEFact Fase 6

## Autenticación

Todos los endpoints bajo `/public/v1/*` requieren el header `X-API-Key`:

```http
X-API-Key: prefix12.secretvalue...
```

Las API Keys se generan desde el Portal Cliente (`/api/v1/api-keys`).

## Scopes Disponibles

| Scope | Acceso |
|---|---|
| `read` | Lectura de todos los recursos |
| `write` | Escritura de todos los recursos |
| `dte` | Emisión y consulta de DTE |
| `customers` | Gestión de clientes |
| `products` | Gestión de productos |

## Endpoints

### Status
```
GET /public/v1/status          → Estado de la API y autenticación
GET /public/v1/status/usage    → Consumo del período actual
```

### Clientes
```
GET  /public/v1/customers              → Listar clientes
POST /public/v1/customers              → Crear cliente
GET  /public/v1/customers/{id}         → Obtener cliente por ID
```

### Productos
```
GET /public/v1/products                → Listar productos
GET /public/v1/products/{id}           → Obtener producto por ID
```

### DTE
```
POST /public/v1/dte                    → Emitir DTE (async, quota validada)
GET  /public/v1/dte/{folio}            → Estado del DTE por folio
GET  /public/v1/dte/{folio}/pdf        → Descargar PDF
GET  /public/v1/dte/{folio}/xml        → Descargar XML
```

## Ejemplo de Uso

```bash
# Emitir una Factura
curl -X POST https://api.ohmefact.cl/public/v1/dte \
  -H "X-API-Key: prefix12.secretvalue" \
  -H "Content-Type: application/json" \
  -d '{
    "dte_type": 33,
    "customer_rut": "76.123.456-7",
    "customer_name": "Empresa Cliente SpA",
    "items": [
      {"name": "Consultoría", "qty": 1, "unit_price": 100000, "tax_pct": 19}
    ]
  }'

# Respuesta
{
  "status": "accepted",
  "message": "DTE queued for processing",
  "company_id": "...",
  "dte_type": 33
}
```

## Rate Limiting

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1750000000
```

Si se excede: `HTTP 429 Too Many Requests`

## Gestión de API Keys (Portal)

```
GET    /api/v1/api-keys                → Listar keys activas
POST   /api/v1/api-keys                → Crear key (raw_key mostrado 1 sola vez)
DELETE /api/v1/api-keys/{id}           → Revocar
POST   /api/v1/api-keys/{id}/rotate    → Rotar (revoca + crea nueva)
```
