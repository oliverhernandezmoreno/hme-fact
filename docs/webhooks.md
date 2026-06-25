# Webhooks (Outbound)

## Resumen
hmEFact notificará a tus sistemas cuando cambien estados críticos. Por ejemplo, cuando un DTE es "Aceptado" o "Rechazado" por el SII.

## Configuración
1. Define un Target URL (ej. `https://api.tu-ecommerce.com/ohmefact/webhook`)
2. Selecciona eventos (`dte.issued`, `dte.accepted`, `dte.rejected`).
3. hmEFact te proveerá un `secret`.

## Formato del Payload
```json
{
  "event_id": "evt_909182312",
  "event_type": "dte.accepted",
  "timestamp": "2026-06-24T19:48:00Z",
  "data": {
    "dte_id": "1111-2222-...",
    "folio": 149,
    "sii_track_id": "1002931238",
    "external_reference": "820982911946154508"
  }
}
```

## Validación HMAC
Valida la autenticidad en tu backend leyendo la cabecera `X-hmEFact-Signature`:
```python
import hmac, hashlib
signature = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
if signature == headers["X-hmEFact-Signature"]:
    # Válido
```
