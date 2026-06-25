# Shopify Connector

## Resumen
El conector de Shopify permite automatizar la emisión de Boletas (DTE 39) y Facturas (DTE 33) en Chile cada vez que se crea una orden en tu tienda de Shopify.

## Flujo de Trabajo
1. El cliente compra en Shopify.
2. Shopify dispara un Webhook HTTP (`orders/create`) hacia hmEFact (`/api/v1/webhooks/inbound/shopify/{connection_id}`).
3. hmEFact valida la cabecera `X-Shopify-Hmac-SHA256` utilizando el `secret` guardado en la conexión.
4. El worker asíncrono mapea el RUT desde los atributos del carrito (`note_attributes`) y extrae los `line_items`.
5. Se emite un DTE asíncronamente y se asocia al ID de orden de Shopify para asegurar la idempotencia.

## Instalación
Desde el panel de hmEFact:
1. Ve a "Integrations Hub".
2. Haz click en "Conectar Shopify".
3. hmEFact generará un webhook URL y te pedirá el Webhook Secret proporcionado por Shopify.
4. En Shopify (Settings > Notifications > Webhooks), crea un webhook para "Order creation" apuntando a la URL generada.

## Campos Requeridos
- Para que una Factura (33) pueda ser emitida, el carrito de Shopify DEBE recolectar el RUT, Razón Social, Giro y Dirección Comercial. El conector mapeará estos atributos si los provees bajo `note_attributes` en Shopify.
