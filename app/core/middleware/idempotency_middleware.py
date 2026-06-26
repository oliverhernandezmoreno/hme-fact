from __future__ import annotations

import json
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.concurrency import iterate_in_threadpool
from app.core.config import get_settings
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware de Idempotencia para la API pública usando el encabezado Idempotency-Key.
    Garantiza que las solicitudes con la misma clave e inquilino devuelvan la misma respuesta.
    El estado se almacena en Redis con un TTL de 24 horas.
    """
    IDEMPOTENCY_HEADER = "idempotency-key"
    PUBLIC_PREFIX = "/public/"

    async def dispatch(self, request: Request, call_next):
        # Solo aplicar a la API pública para solicitudes que modifiquen estado (POST, PUT, PATCH, DELETE)
        # y que tengan el encabezado de idempotencia.
        if not request.url.path.startswith(self.PUBLIC_PREFIX):
            return await call_next(request)

        idempotency_key = request.headers.get(self.IDEMPOTENCY_HEADER)
        if not idempotency_key:
            return await call_next(request)

        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)

        # Determinar inquilino a partir de api_key_id
        api_key_id = getattr(request.state, "api_key_id", "global")
        redis_key = f"idempotency:{api_key_id}:{idempotency_key}"

        redis_client = None
        try:
            settings = get_settings()
            redis_client = aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)

            # Intentar establecer estado "processing"
            # Si retorna True, somos la primera petición
            set_success = await redis_client.set(redis_key, "processing", nx=True, ex=30)
            
            if not set_success:
                # La clave ya existe en Redis (duplicada o ya procesada)
                val = await redis_client.get(redis_key)
                
                if val == "processing":
                    # Petición concurrente en proceso
                    await redis_client.aclose()
                    return JSONResponse(
                        status_code=409,
                        content={
                            "error": "conflict",
                            "message": "A request with this idempotency key is already in progress.",
                        }
                    )
                
                # Ya fue procesada, retornar respuesta cacheada
                if val:
                    cached_data = json.loads(val)
                    await redis_client.aclose()
                    
                    headers = cached_data.get("headers", {})
                    headers["X-Cache-Idempotency"] = "HIT"
                    
                    # Content-Length no debe ser forzado incorrectamente
                    headers.pop("content-length", None)
                    
                    return Response(
                        content=cached_data["content"].encode("utf-8"),
                        status_code=cached_data["status_code"],
                        media_type=headers.get("content-type", "application/json"),
                        headers=headers
                    )
            
            # Si somos la primera petición, procedemos a ejecutarla
            try:
                response = await call_next(request)
            except Exception:
                # Si falla con excepción, eliminar la clave para permitir reintento
                await redis_client.delete(redis_key)
                raise
            finally:
                pass

            # Si es un error del servidor (>= 500), no cachear y permitir reintentos
            if response.status_code >= 500:
                await redis_client.delete(redis_key)
                await redis_client.aclose()
                return response

            # Consumir el body de la respuesta sin romper el stream
            response_body = [section async for section in response.body_iterator]
            body = b"".join(response_body)
            response.body_iterator = iterate_in_threadpool(iter(response_body))

            # Cachear la respuesta exitosa o error de cliente (< 500)
            cached_data = {
                "status_code": response.status_code,
                "content": body.decode("utf-8", errors="replace"),
                "headers": dict(response.headers)
            }
            
            # Guardar en Redis con TTL de 24 horas (86400 segundos)
            await redis_client.set(redis_key, json.dumps(cached_data), ex=86400)
            await redis_client.aclose()

            response.headers["X-Cache-Idempotency"] = "MISS"
            return response

        except Exception as e:
            logger.warning(f"Error en middleware de idempotencia (fail-open): {e}")
            if redis_client:
                try:
                    await redis_client.aclose()
                except Exception:
                    pass
            # En caso de error de Redis, continuar con la petición normal (fail-open)
            return await call_next(request)
