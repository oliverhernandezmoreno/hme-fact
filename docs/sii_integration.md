# Integración WebServices SII (Resiliencia, Contingencia y Sandbox)

## Arquitectura del Wrapper SII
La integración con el SII en Chile requiere interactuar con tres servicios web principales utilizando el certificado digital del representante legal de la empresa.

### Archivo Base: `app/services/sii/client.py`

### 1. Obtención de la Semilla (CrSeed)
* **Endpoint (Certificación):** `https://maullin.sii.cl/DTEWS/CrSeed.jws`
* **Endpoint (Producción):** `https://palena.sii.cl/DTEWS/CrSeed.jws`
* Operación sin autenticación. Devuelve un XML SOAP con un nodo `<SEMILLA>`.

### 2. Obtención del Token (GetTokenFromSeed)
* **Endpoint (Certificación):** `https://maullin.sii.cl/DTEWS/GetTokenFromSeed.jws`
* **Endpoint (Producción):** `https://palena.sii.cl/DTEWS/GetTokenFromSeed.jws`
* **Caché en Redis:** El token se almacena en caché en Redis (`sii:token:<hash>`) con un TTL de 105 minutos y un bloqueo distribuido (Redlock) para evitar peticiones simultáneas del mismo RUT.
* Requiere firmar digitalmente la semilla con XML-DSig usando el Certificado Digital (`.pfx`). Devuelve un `<TOKEN>` SOAP de sesión.

### 3. Envío de Documentos (EnvioDTE)
* **Endpoint (Certificación/Producción):** `https://maullin.sii.cl/cgi_dte/UPL/conector.cgi`
* Subida HTTP `multipart/form-data` pasando:
  * `rutSender` / `dvSender`: RUT de la firma digital autorizada.
  * `rutCompany` / `dvCompany`: RUT de la empresa emisora.
  * `archivo`: Archivo XML firmado del DTE.
  * **Headers:** Se envía el token de sesión en la cookie `TOKEN=token_value`.
* **Respuesta exitosa:** XML de respuesta que contiene el identificador de envío o `TRACKID` para consultar el estado del procesamiento fiscal en el SII.

---

## Capa de Resiliencia: Circuit Breaker (`SIICircuitBreaker`)

Para evitar la saturación de peticiones y cascadas de fallas ante caídas persistentes del SII, las llamadas externas al SII están envueltas por un **Circuit Breaker** con estado compartido en Redis (`app/services/sii/circuit_breaker.py`).

### Estados del Circuit Breaker:
* **`CLOSED` (Cerrado):** Estado normal. Las peticiones pasan directo al SII. Si ocurren fallas consecutivas iguales al umbral, el circuito se abre.
* **`OPEN` (Abierto):** El SII está caído. Todas las peticiones fallan inmediatamente levantando una excepción `SIICircuitBreakerOpenException` sin sobrecargar al SII. Las DTEs pasan al estado de **`contingencia`**.
* **`HALF_OPEN` (Semi-Abierto):** Tras expirar el tiempo de recuperación (`recovery_timeout`), se permite una petición de prueba. Si tiene éxito, el circuito vuelve a `CLOSED`; si falla, vuelve inmediatamente a `OPEN`.

### Configuración Dinámica de Variables de Entorno:
* `SII_CB_FAILURE_THRESHOLD`: Umbral de fallos consecutivos antes de abrir el circuito (por defecto `5`).
* `SII_CB_RECOVERY_TIMEOUT`: Tiempo en segundos antes de pasar de `OPEN` a `HALF_OPEN` (por defecto `60`).
* `SII_SIMULATE_FAILURE`: Activa de forma global el Sandbox/Simulación de caída del SII (por defecto `False`).

---

## Flujo de Contingencia

Cuando el Circuit Breaker del SII está `OPEN` o se detecta una caída temporal (como errores SOAP 5xx), los documentos no se rechazan. En su lugar, el sistema entra en **Modo Contingencia**:
1. El DTE se firma digitalmente de manera local con la clave privada de la empresa y se guarda el XML/PDF.
2. El estado del DTE se establece en `"contingency"` (Contingencia).
3. Un worker asíncrono (Celery periodic task) reintenta periódicamente enviar los documentos en contingencia una vez que el Circuit Breaker regresa al estado `CLOSED`.
4. El Frontend ofrece un banner especial de advertencia y un botón manual de **Reintentar** en el dashboard de DTEs para gatillar el reenvío inmediato.

---

## Endpoints de Monitoreo Administrativo (SuperAdmin)

Ubicados en el prefijo `/api/v1/admin/sii/` y protegidos por el middleware `SuperAdminRequired`:

1. **`GET /api/v1/admin/sii/status`**
   * Retorna el estado actual del circuito (`CLOSED`, `OPEN`, `HALF_OPEN`), contador de errores consecutivos, y el tiempo de bloqueo restante (si está abierto).
2. **`POST /api/v1/admin/sii/reset`**
   * Fuerza el restablecimiento manual del circuito al estado `CLOSED`, limpiando los contadores de errores en Redis.
3. **`POST /api/v1/admin/sii/simulate-failure`**
   * Sandbox/Simulación: Activa el flag de falla simulada del SII en caliente usando Redis sin reiniciar los workers.
4. **`POST /api/v1/admin/sii/clear-failure-simulation`**
   * Sandbox/Simulación: Desactiva la simulación de fallas del SII en caliente.

