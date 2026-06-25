# Integración WebServices SII (Fase 8B)

## Arquitectura del Wrapper SII
La integración con el SII en Chile requiere interactuar con tres servicios web principales, usando el certificado digital de la persona que representa a la empresa.

### Archivo: `app/services/sii/client.py`

### 1. Obtención de la Semilla (CrSeed)
Endpoint: `https://palena.sii.cl/DTEWS/CrSeed.jws`
Operación sin autenticación. Devuelve un XML anidado con un nodo `<SEMILLA>`.

### 2. Obtención del Token (GetTokenFromSeed)
Endpoint: `https://palena.sii.cl/DTEWS/GetTokenFromSeed.jws`
Requiere que la Semilla obtenida en el paso 1 se envuelva en un nodo `<getToken><item><Semilla>...</Semilla></item></getToken>` y se le aplique una **Firma XML-DSig** utilizando el Certificado Digital (`.pfx`). 
Si el SII valida la firma contra el certificado, devuelve un `<TOKEN>` que dura aproximadamente 120 minutos.

### 3. Envío de Documentos (EnvioDTE)
Endpoint: `https://palena.sii.cl/cgi_dte/UPL/conector.cgi`
No es SOAP. Es una subida HTTP `multipart/form-data`.
Se pasan:
- `rutSender` / `dvSender`: El RUT de la persona (dueña del certificado).
- `rutCompany` / `dvCompany`: El RUT de la empresa (Emisor del DTE).
- `archivo`: El XML del DTE (que a su vez está firmado y lleva un CAF).
- **Headers:** Se envía el `TOKEN` inyectado en el header `Cookie`.

Respuesta exitosa: Devuelve un XML con el `TRACKID`. Este número se usa luego para consultar el estado del envío (Aceptado o Rechazado).

### Dependencias Inyectadas
El cliente de WebServices delega la responsabilidad de firmar la semilla a la clase `SIISigner` que construimos en la Fase 8A.

### Manejo de Ambientes
El cliente soporta inicialización con `environment="certification"` (Maullín) o `environment="production"` (Palena) para facilitar pruebas sin validez legal.
