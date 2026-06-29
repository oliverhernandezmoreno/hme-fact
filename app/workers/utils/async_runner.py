from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from app.db.session import AsyncSessionLocal


def async_task(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Any]:
    """Decorator to run async functions inside synchronous Celery tasks."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        async def run_with_session() -> Any:
            async with AsyncSessionLocal() as session:
                kwargs["session"] = session
                return await func(*args, **kwargs)

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(run_with_session())

    return wrapper
