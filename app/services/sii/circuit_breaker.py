import time
import logging
from httpx import HTTPStatusError, RequestError
import redis.asyncio as redis
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SIICircuitBreakerOpenException(Exception):
    """Raised when the SII Web Services circuit is OPEN."""
    pass


class SIICircuitBreaker:
    """
    Redis-backed distributed Circuit Breaker to prevent cascading failures 
    and overload of the SII when they experience 5xx errors or timeouts.
    """
    def __init__(self, failure_threshold: int | None = None, recovery_timeout: int | None = None):
        self.settings = get_settings()
        self.failure_threshold = (
            failure_threshold 
            if failure_threshold is not None 
            else self.settings.SII_CB_FAILURE_THRESHOLD
        )
        self.recovery_timeout = (
            recovery_timeout 
            if recovery_timeout is not None 
            else self.settings.SII_CB_RECOVERY_TIMEOUT
        )
        self.state_key = "sii:cb:state"
        self.failure_count_key = "sii:cb:failures"
        self.last_state_change_key = "sii:cb:last_state_change"

    async def _get_redis(self):
        return redis.from_url(str(self.settings.REDIS_URL), decode_responses=True)

    async def get_state(self) -> str:
        r = await self._get_redis()
        try:
            state = await r.get(self.state_key) or "CLOSED"
            if state == "OPEN":
                last_change = await r.get(self.last_state_change_key)
                if last_change:
                    elapsed = time.time() - float(last_change)
                    if elapsed >= self.recovery_timeout:
                        logger.info("Circuit breaker recovery timeout reached. Transitioning to HALF_OPEN.")
                        await r.set(self.state_key, "HALF_OPEN")
                        state = "HALF_OPEN"
            return state
        except Exception as e:
            logger.error(f"Failed to get Circuit Breaker state from Redis: {e}")
            return "CLOSED"  # Fallback to CLOSED on Redis failure
        finally:
            await r.aclose()

    async def record_success(self) -> None:
        r = await self._get_redis()
        try:
            state = await r.get(self.state_key) or "CLOSED"
            if state == "HALF_OPEN":
                logger.info("Circuit Breaker call succeeded in HALF_OPEN. Closing circuit.")
                await r.set(self.state_key, "CLOSED")
            await r.set(self.failure_count_key, 0)
        except Exception as e:
            logger.error(f"Failed to record success to Redis: {e}")
        finally:
            await r.aclose()

    async def record_failure(self) -> None:
        r = await self._get_redis()
        try:
            state = await r.get(self.state_key) or "CLOSED"
            failures = await r.incr(self.failure_count_key)
            if state == "HALF_OPEN" or failures >= self.failure_threshold:
                logger.warning(f"Circuit Breaker threshold reached or failure in HALF_OPEN. Opening circuit. Failures: {failures}")
                await r.set(self.state_key, "OPEN")
                await r.set(self.last_state_change_key, time.time())
        except Exception as e:
            logger.error(f"Failed to record failure to Redis: {e}")
        finally:
            await r.aclose()

    async def call(self, func, *args, **kwargs):
        state = await self.get_state()
        if state == "OPEN":
            raise SIICircuitBreakerOpenException("SII Web Services circuit is currently OPEN due to consecutive failures.")
        
        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except (HTTPStatusError, RequestError) as exc:
            # We ONLY count 5xx status codes and network errors as circuit-breaker tripping failures
            is_5xx = False
            if isinstance(exc, HTTPStatusError):
                is_5xx = exc.response.status_code >= 500
            
            if is_5xx or isinstance(exc, RequestError):
                await self.record_failure()
            raise exc
        except Exception as exc:
            # Other errors (e.g. invalid credentials, 4xx, bad schema, etc.)
            # Do NOT trip circuit breaker, just re-raise.
            raise exc

    async def reset(self) -> None:
        r = await self._get_redis()
        try:
            await r.set(self.state_key, "CLOSED")
            await r.set(self.failure_count_key, 0)
            await r.delete(self.last_state_change_key)
            logger.info("Circuit Breaker has been manually reset to CLOSED.")
        except Exception as e:
            logger.error(f"Failed to reset Circuit Breaker: {e}")
        finally:
            await r.aclose()

    async def get_status_details(self) -> dict:
        r = await self._get_redis()
        try:
            state = await r.get(self.state_key) or "CLOSED"
            failures = int(await r.get(self.failure_count_key) or 0)
            last_change = await r.get(self.last_state_change_key)
            
            elapsed = 0.0
            remaining_lock_time = 0.0
            
            if last_change:
                elapsed = time.time() - float(last_change)
                if state == "OPEN":
                    remaining_lock_time = max(0.0, self.recovery_timeout - elapsed)
                    if elapsed >= self.recovery_timeout:
                        state = "HALF_OPEN"
            
            return {
                "state": state,
                "failures": failures,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout_seconds": self.recovery_timeout,
                "last_state_change_timestamp": float(last_change) if last_change else None,
                "elapsed_seconds_since_change": elapsed if last_change else 0.0,
                "remaining_lock_seconds": remaining_lock_time,
            }
        except Exception as e:
            logger.error(f"Failed to get Circuit Breaker details: {e}")
            return {
                "state": "CLOSED",
                "failures": 0,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout_seconds": self.recovery_timeout,
                "error": str(e)
            }
        finally:
            await r.aclose()

