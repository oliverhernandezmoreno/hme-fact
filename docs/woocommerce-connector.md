# WooCommerce Connector

## Resumen
El conector de WooCommerce permite a los comercios automatizar la facturación chilena usando el estándar de REST API Webhooks de WordPress.

## Arquitectura
1. hmEFact provee una URL de entrega.
2. WooCommerce despacha un webhook al crearse un pedido (`order.created`).
3. El payload es autenticado usando el Secret de WooCommerce (enviado en el header `X-WC-Webhook-Signature`).
4. hmEFact mapea los campos de facturación de WooCommerce (requiere plugin de RUT chileno) hacia el cliente interno.
5. Se emite el documento automáticamente.

## Idempotencia
Los ID de orden de WooCommerce se almacenan como llaves de idempotencia en hmEFact. Si WooCommerce reintenta un Webhook debido a un timeout temporal, hmEFact detecta la orden ya procesada y devuelve la misma respuesta (ej. el folio generado) sin emitir un duplicado en el SII.
