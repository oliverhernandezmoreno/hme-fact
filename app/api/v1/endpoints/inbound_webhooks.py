import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.workers.integration_worker import process_inbound_webhook

router = APIRouter()


async def verify_hmac(payload: bytes, secret: str, signature: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/shopify/{connection_id}")
async def shopify_webhook(
    connection_id: str,
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    db: AsyncSession = Depends(get_db_session),
):
    body = await request.body()
    # verify signature (mocked secret check, normally fetch connection from DB)
    # trigger async worker
    process_inbound_webhook.delay(str(connection_id), "shopify", body.decode("utf-8"))
    return {"status": "accepted"}


@router.post("/woocommerce/{connection_id}")
async def woocommerce_webhook(
    connection_id: str,
    request: Request,
    x_wc_webhook_signature: str = Header(None),
    db: AsyncSession = Depends(get_db_session),
):
    body = await request.body()
    process_inbound_webhook.delay(str(connection_id), "woocommerce", body.decode("utf-8"))
    return {"status": "accepted"}
