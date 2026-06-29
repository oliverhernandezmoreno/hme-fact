import logging

import httpx
from lxml import etree

from app.core.config import get_settings
from app.services.sii.circuit_breaker import SIICircuitBreaker
from app.services.sii.signer import SIISigner

logger = logging.getLogger(__name__)


class SIIEnvironment:
    CERTIFICATION = {
        "cr_seed": "https://maullin.sii.cl/DTEWS/CrSeed.jws",
        "get_token": "https://maullin.sii.cl/DTEWS/GetTokenFromSeed.jws",
        "envio_dte": "https://maullin.sii.cl/cgi_dte/UPL/conector.cgi",
    }
    PRODUCTION = {
        "cr_seed": "https://palena.sii.cl/DTEWS/CrSeed.jws",
        "get_token": "https://palena.sii.cl/DTEWS/GetTokenFromSeed.jws",
        "envio_dte": "https://palena.sii.cl/cgi_dte/UPL/conector.cgi",
    }


class SIIWebServicesClient:
    """
    Cliente para comunicarse con los Web Services del SII (Servicio de Impuestos Internos).
    Maneja la autenticación mediante Seed -> Token y el envío de documentos.
    """

    def __init__(self, environment: str = "certification"):
        self.env_urls = (
            SIIEnvironment.PRODUCTION
            if environment == "production"
            else SIIEnvironment.CERTIFICATION
        )
        self.signer = SIISigner()
        self.circuit_breaker = SIICircuitBreaker()
        self.settings = get_settings()

    async def _check_simulated_failure(self) -> None:
        if self.settings.SII_SIMULATE_FAILURE:
            logger.warning("Simulated SII Failure: active via Settings.")
            raise httpx.HTTPStatusError(
                "Simulated SII 500 Internal Server Error (Settings)",
                request=httpx.Request("POST", "https://api.sii.example.local"),
                response=httpx.Response(
                    500, request=httpx.Request("POST", "https://api.sii.example.local")
                ),
            )

        import redis.asyncio as redis

        redis_client = None
        try:
            redis_client = redis.from_url(str(self.settings.REDIS_URL), decode_responses=True)
            sim_active = await redis_client.get("sii:cb:simulate_failure")
            if sim_active == "true" or sim_active == "1":
                logger.warning("Simulated SII Failure: active via Redis key.")
                raise httpx.HTTPStatusError(
                    "Simulated SII 500 Internal Server Error (Redis)",
                    request=httpx.Request("POST", "https://api.sii.example.local"),
                    response=httpx.Response(
                        500, request=httpx.Request("POST", "https://api.sii.example.local")
                    ),
                )
        except httpx.HTTPStatusError:
            raise
        except Exception as e:
            logger.debug(f"Error checking simulated failure in Redis: {e}")
        finally:
            if redis_client:
                await redis_client.aclose()

    async def get_seed(self) -> str:
        """Paso 1: Solicitar la Semilla al SII"""
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:def="http://DefaultNamespace">
   <soapenv:Header/>
   <soapenv:Body>
      <def:getSeed/>
   </soapenv:Body>
</soapenv:Envelope>"""

        async def _request():
            await self._check_simulated_failure()
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.env_urls["cr_seed"],
                    content=body,
                    headers={"Content-Type": "text/xml;charset=UTF-8"},
                )
                resp.raise_for_status()
                return resp.content

        resp_content = await self.circuit_breaker.call(_request)

        # The response is a SOAP Envelope where the body contains an XML string as text
        # Inside that string is <SII:RESPUESTA><SII:RESP_BODY><SEMILLA>xxxx</SEMILLA>
        root = etree.fromstring(resp_content)
        # Find the getSeedReturn node which contains the nested XML string
        seed_return_node = root.find(".//getSeedReturn")
        if seed_return_node is None:
            raise ValueError("No se pudo obtener la semilla del SII.")

        inner_xml = etree.fromstring(seed_return_node.text.encode("utf-8"))
        seed_node = inner_xml.find(".//SEMILLA")
        if seed_node is None:
            raise ValueError("Respuesta del SII no contiene el nodo <SEMILLA>.")

        return seed_node.text

    async def get_token(self, pfx_data: bytes, pfx_password: str) -> str:
        """
        Paso 2: Obtener Semilla, Firmarla con el Certificado PFX, y solicitar Token.
        Maneja caché en Redis con TTL de 105 minutos y bloqueo distribuido.
        """
        import hashlib

        import redis.asyncio as redis

        from app.core.config import get_settings

        settings = get_settings()
        pfx_hash = hashlib.sha256(pfx_data).hexdigest()
        token_key = f"sii:token:{pfx_hash}"
        lock_key = f"lock:sii:token:{pfx_hash}"

        redis_client = None
        try:
            redis_client = redis.from_url(str(settings.REDIS_URL), decode_responses=True)
            token = await redis_client.get(token_key)
            if token:
                logger.info("SII token retrieved from Redis cache.")
                await redis_client.aclose()
                return token

            # Lock to prevent concurrent requests
            lock = redis_client.lock(lock_key, timeout=30, sleep=0.1)
            async with lock:
                # Double-check inside lock
                token = await redis_client.get(token_key)
                if token:
                    logger.info("SII token retrieved from Redis cache (after lock).")
                    await redis_client.aclose()
                    return token

                # Fetch new token
                token = await self._fetch_token_from_sii(pfx_data, pfx_password)

                # Cache token for 105 minutes (6300 seconds)
                await redis_client.set(token_key, token, ex=6300)
                logger.info("Successfully fetched new SII token and cached it in Redis.")
                await redis_client.aclose()
                return token

        except Exception as e:
            logger.warning(f"Redis cache error in get_token, falling back to direct SII call: {e}")
            if redis_client:
                try:
                    await redis_client.aclose()
                except Exception:
                    pass
            # Fallback to direct SII call
            return await self._fetch_token_from_sii(pfx_data, pfx_password)

    async def _fetch_token_from_sii(self, pfx_data: bytes, pfx_password: str) -> str:
        """
        Realiza la llamada SOAP al SII para obtener un nuevo token a partir de una semilla firmada.
        """
        seed = await self.get_seed()

        # Build the XML to be signed
        xml_to_sign = f"""<getToken><item><Semilla>{seed}</Semilla></item></getToken>"""

        # Sign it using the SIISigner we built in Phase 8
        signed_seed_xml = self.signer.sign_token_seed(xml_to_sign, pfx_data, pfx_password)

        body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:def="http://DefaultNamespace">
   <soapenv:Header/>
   <soapenv:Body>
      <def:getToken>
         <pszXml>{signed_seed_xml}</pszXml>
      </def:getToken>
   </soapenv:Body>
</soapenv:Envelope>"""

        async def _request():
            await self._check_simulated_failure()
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.env_urls["get_token"],
                    content=body,
                    headers={"Content-Type": "text/xml;charset=UTF-8"},
                )
                resp.raise_for_status()
                return resp.content

        resp_content = await self.circuit_breaker.call(_request)

        root = etree.fromstring(resp_content)
        token_return_node = root.find(".//getTokenReturn")
        if token_return_node is None:
            raise ValueError("Error al obtener token del SII.")

        inner_xml = etree.fromstring(token_return_node.text.encode("utf-8"))
        token_node = inner_xml.find(".//TOKEN")
        if token_node is None:
            raise ValueError("Respuesta del SII no contiene el nodo <TOKEN>.")

        return token_node.text

    async def enviar_dte(
        self, signed_dte_xml: bytes, token: str, rut_emisor: str, rut_empresa: str
    ) -> str:
        """
        Paso 3: Subir el XML del DTE firmado al portal UPL del SII.
        Requiere el TOKEN en el header Cookie o Token.
        rut_emisor: RUT del certificado digital (Persona Natural que envía)
        rut_empresa: RUT de la empresa emisora del documento
        """
        # Limpiar RUTs (11111111-1 -> 111111111) para el multipart form
        rut_emisor_clean = rut_emisor.replace(".", "").replace("-", "")
        rut_empresa_clean = rut_empresa.replace(".", "").replace("-", "")

        # The SII CGI expects a multipart/form-data request with specific fields
        data = {
            "rutSender": rut_emisor_clean[:-1],
            "dvSender": rut_emisor_clean[-1],
            "rutCompany": rut_empresa_clean[:-1],
            "dvCompany": rut_empresa_clean[-1],
            "archivo": ("envio.xml", signed_dte_xml, "text/xml"),
        }

        headers = {"Cookie": f"TOKEN={token}", "User-Agent": "hmEFACT/1.0"}

        async def _request():
            await self._check_simulated_failure()
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.env_urls["envio_dte"],
                    files={"archivo": data.pop("archivo")},
                    data=data,
                    headers=headers,
                )
                resp.raise_for_status()
                return resp.content

        resp_content = await self.circuit_breaker.call(_request)

        # The response is an XML with a <STATUS> and a <TRACKID>
        root = etree.fromstring(resp_content)
        status_node = root.find(".//STATUS")
        if status_node is not None and status_node.text != "0":
            raise ValueError(f"El SII rechazó el envío. Status: {status_node.text}")

        track_id_node = root.find(".//TRACKID")
        if track_id_node is None:
            raise ValueError("El SII no devolvió un TRACKID válido.")

        return track_id_node.text
