from celery import shared_task
import json
from app.services.integrations.mappers import OrderToDTEMapper

@shared_task(bind=True, max_retries=3)
def process_inbound_webhook(self, connection_id: str, provider: str, raw_payload: str):
    """
    Process inbound webhooks from Shopify, WooCommerce, POS, etc.
    """
    payload = json.loads(raw_payload)
    try:
        if provider == "shopify":
            order = OrderToDTEMapper.map_shopify_order(payload)
        elif provider == "woocommerce":
            pass # map woocommerce
        
        # Then we create DTE using standard DTE services
        # mapped_dte = OrderToDTEMapper.to_dte_payload(order)
        # issue_dte(mapped_dte)
        return {"status": "success", "order_id": payload.get("id")}
    except Exception as exc:
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_outbound_webhook(self, subscription_id: str, event_type: str, payload: dict):
    """
    Send webhooks to subscribers (e.g., when a DTE is issued).
    """
    import requests
    import hmac
    import hashlib
    # fetch subscription details
    # signature = hmac.new(secret.encode(), json.dumps(payload).encode(), hashlib.sha256).hexdigest()
    # requests.post(url, json=payload, headers={"X-Signature": signature})
    pass
