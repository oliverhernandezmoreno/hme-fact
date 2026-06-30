import json

from celery import shared_task

from app.services.integrations.mappers import OrderToDTEMapper


@shared_task(bind=True, max_retries=3)
def process_inbound_webhook(self, connection_id: str, provider: str, raw_payload: str):
    """
    Process inbound webhooks from Shopify, WooCommerce, POS, etc.
    """
    payload = json.loads(raw_payload)
    try:
        if provider == "shopify":
            OrderToDTEMapper.map_shopify_order(payload)
        elif provider == "woocommerce":
            pass  # map woocommerce

        # Then we create DTE using standard DTE services
        # mapped_dte = OrderToDTEMapper.to_dte_payload(order)
        # issue_dte(mapped_dte)
        return {"status": "success", "order_id": payload.get("id")}
    except Exception as exc:
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_outbound_webhook(self, subscription_id: str, event_type: str, payload: dict):
    """
    Send webhooks to subscribers (e.g., when a DTE is issued, cert expiring, or CAF depleted).
    """
    import asyncio
    import hashlib
    import hmac
    import json
    import uuid

    import requests
    from sqlalchemy import select

    from app.db.session import AsyncSessionLocal
    from app.models.integration import WebhookDelivery, WebhookSubscription

    def _run_async(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _send():
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(WebhookSubscription).where(
                    WebhookSubscription.id == uuid.UUID(subscription_id),
                    WebhookSubscription.is_active,
                )
            )
            sub = result.scalar_one_or_none()
            if not sub:
                return {"status": "skipped", "reason": "subscription_not_found_or_inactive"}

            payload_str = json.dumps(payload)
            signature = hmac.new(
                sub.secret.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            headers = {
                "Content-Type": "application/json",
                "X-HMEFact-Signature": signature,
                "X-HMEFact-Event": event_type,
            }

            status = "failed"
            status_code = None
            response_body = None

            try:
                response = requests.post(sub.target_url, json=payload, headers=headers, timeout=10)
                status_code = response.status_code
                response_body = response.text[:2000]
                if 200 <= response.status_code < 300:
                    status = "success"
                else:
                    status = "failed"
            except Exception as e:
                response_body = str(e)
                status = "failed"

            delivery = WebhookDelivery(
                subscription_id=sub.id,
                event_type=event_type,
                payload=payload,
                status=status,
                status_code=status_code,
                response_body=response_body,
                attempt=self.request.retries + 1,
            )
            session.add(delivery)
            await session.commit()

            if status == "failed":
                if status_code is None or status_code >= 500:
                    raise RuntimeError(
                        f"Webhook delivery failed with status {status_code} or network error"
                    )

            return {"status": status, "status_code": status_code}

    try:
        return _run_async(_send())
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
