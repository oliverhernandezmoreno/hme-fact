from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from app.modules.integrations.exceptions import TaxIntegrationError


async def retry_async[ResultT](
    operation: Callable[[], Awaitable[ResultT]],
    *,
    max_retries: int,
    backoff_base_seconds: float,
) -> ResultT:
    attempt = 0
    while True:
        try:
            return await operation()
        except TaxIntegrationError as exc:
            if not exc.retryable or attempt >= max_retries:
                raise
            delay = backoff_base_seconds * (2**attempt)
            attempt += 1
            await asyncio.sleep(delay)
