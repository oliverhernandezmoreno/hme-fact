# hmEFact Integration Hub (Fase 7)

## Descripción General
El Integration Hub es el ecosistema de hmEFact diseñado para conectar fuentes externas (Ecommerce, POS, ERPs) a la emisión automatizada de DTEs, y proveer notificaciones salientes a estos sistemas externos a través de Webhooks.

## Arquitectura
- **Mappers (`app/services/integrations/mappers.py`)**: Traducen el lenguaje de Shopify/WooCommerce/POS hacia `ExternalOrderPayload` y posteriormente a `DTEIssuePayload`.
- **Workers (`app/workers/integration_worker.py`)**: Procesamiento asíncrono para no bloquear la respuesta rápida requerida por los webhooks externos (ej. Shopify espera un 200 OK en menos de 5 segundos). Celery se encarga del reintento (`retries`) si falla la emisión de DTE o la base de datos externa.
- **Seguridad**: Los inbound webhooks verifican la firma HMAC para garantizar la autenticidad del emisor. Los outbound webhooks adjuntan una firma para que el cliente receptor pueda validar a hmEFact.
- **Modelos de DB**: `IntegrationConnection`, `IntegrationEvent`, `ExternalMapping`, `WebhookSubscription`, `WebhookDelivery` e `IdempotencyKey`. Todo opera de forma multi-empresa (`company_id`).

## Connectors Disponibles (Base)
1. **Shopify**: Recibe el payload del evento `orders/create`, mapea el `note_attributes` (rut) o el customer base a un cliente en hmEFact, y genera una boleta (39) por defecto.
2. **WooCommerce**: Sigue el mismo principio.
3. **POS genérico**: Una API para recibir tickets que asegura la idempotencia en caso de que la red del POS falle y envíe la venta duplicada.

## Despliegue
Los workers de integración corren en el contenedor Celery configurado. Las migraciones de Alembic se aplican con la revisión `20260624_0007_phase7_integrations.py`.
