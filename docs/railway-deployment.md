# Guía de Despliegue en Railway para hmEfact (Backend)

Este documento detalla el paso a paso para desplegar el backend (API FastAPI, Celery Worker, y Celery Beat) en **Railway**, utilizando **Supabase** como base de datos y **Redis** proveído por Railway, manteniendo la premisa de **cero cambios en el código**.

---

## 1. El Reto del Almacenamiento Local compartido

En una arquitectura de contenedores distribuida tradicional:
* La **API** recibe las peticiones y sirve los archivos PDF/XML.
* El **Worker de Celery** genera los archivos PDF/XML de forma asíncrona.

Si se despliegan en servicios de Railway separados, cada contenedor tiene su propio sistema de archivos y no pueden compartir un volumen de disco local. 

### Solución "Sin Cambios de Código": Monolito en Contenedor (Recomendado)
Para resolver esto sin escribir drivers de almacenamiento en la nube, configuraremos un script de inicio (`entrypoint.sh`) que ejecutará la API, el Worker y el Scheduler (Celery Beat) **dentro del mismo contenedor**. De este modo:
1. Comparten el mismo volumen persistente de Railway en `/tmp/hme_fact_storage`.
2. Ahorras costos en Railway al correr un único servicio activo.
3. Se mantiene el stack 100% intacto.

---

## 2. Preparación del Proyecto en Railway

### Paso 1: Crear el proyecto y agregar Redis
1. Inicia sesión en [Railway.app](https://railway.app/).
2. Haz clic en **New Project** -> **Empty Project**.
3. Haz clic en **+ Add** -> **Database** -> **Add Redis**.
   * Esto creará un contenedor de Redis. Copia la variable de entorno `REDIS_URL` generada por Railway (e.g., `redis://default:password@host:port`).

### Paso 2: Crear el script de inicio (`entrypoint.sh`)
Para correr la API y Celery juntos en el mismo contenedor, necesitamos un pequeño script en la raíz del proyecto backend. 

Crearemos el archivo `scripts/entrypoint_railway.sh`:
```bash
#!/bin/bash

# Aplicar migraciones de base de datos
echo "Aplicando migraciones con Alembic..."
alembic upgrade head

# Iniciar Celery Worker en segundo plano
echo "Iniciando Celery Worker..."
celery -A app.workers.celery_app worker --loglevel=info &

# Iniciar Celery Beat (Scheduler) en segundo plano
echo "Iniciando Celery Beat Scheduler..."
celery -A app.workers.celery_app beat --loglevel=info &

# Iniciar FastAPI (Uvicorn) en primer plano para mantener el contenedor activo
echo "Iniciando API FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

> [!NOTE]
> Debemos asegurarnos de que el archivo tenga permisos de ejecución (`chmod +x scripts/entrypoint_railway.sh`) antes de subirlo a tu repositorio Git.

### Paso 3: Configurar el Dockerfile
El archivo `Dockerfile` en la raíz ya está listo, pero debemos indicarle a Railway que ejecute nuestro script de inicio.

---

## 3. Despliegue del Backend en Railway

1. En tu proyecto de Railway, haz clic en **+ Add** -> **GitHub Repo** y selecciona el repositorio de `hme-fact`.
2. Ve a la pestaña **Variables** del servicio de backend y agrega las siguientes variables de entorno:

| Variable | Valor / Origen | Descripción |
|---|---|---|
| `PORT` | `8000` ( Railway lo inyecta automáticamente) | Puerto de la API |
| `ENVIRONMENT` | `production` | Modo de producción |
| `DEBUG` | `False` | Desactiva modo debug |
| `POSTGRES_HOST` | *Copiar de Supabase* | Host de Supabase |
| `POSTGRES_PORT` | `6543` (Recomendado Pooler) | Puerto de base de datos |
| `POSTGRES_DB` | `postgres` | Base de datos Supabase |
| `POSTGRES_USER` | `postgres` | Usuario administrador |
| `POSTGRES_PASSWORD` | *Tu contraseña en Supabase* | Contraseña de base de datos |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Referencia al Redis de Railway |
| `CELERY_BROKER_URL` | `${{Redis.REDIS_URL}}` | Cola de tareas de Celery |
| `CELERY_RESULT_BACKEND` | `${{Redis.REDIS_URL}}` | Resultados de Celery |
| `JWT_SECRET_KEY` | *Generar string aleatorio seguro* | Firma de tokens JWT |
| `CERTIFICATE_ENCRYPTION_KEY` | *Generar string de 32 bytes* | Encriptación AES de PFX |

3. Ve a la pestaña **Settings** del servicio de backend:
   * **Build Command:** Déjalo en blanco (Railway leerá el Dockerfile).
   * **Start Command:** Configúralo como:
     ```bash
     bash scripts/entrypoint_railway.sh
     ```
   * **Volumes:** Agrega un volumen nuevo:
     * **Mount Path:** `/tmp/hme_fact_storage`
     * **Size:** 5GB - 10GB (suficiente para iniciar).
     > [!WARNING]
     > El Dockerfile de producción corre bajo el usuario no privilegiado `appuser`. Si Railway monta el volumen con permisos exclusivos de `root`, podrías ver errores de "Permission Denied" al generar PDFs. Si esto ocurre, puedes modificar temporalmente tu Dockerfile comentando la línea `USER appuser` para correr como root, o bien asegurar que los permisos del volumen heredan el UID `1000`.
4. Railway comenzará a construir la imagen de Docker, aplicará las migraciones a Supabase automáticamente en el inicio y levantará la API junto con los workers de Celery.

---

## 4. Verificación de Funcionamiento

Una vez completado el despliegue, podrás ver las URLs públicas autogeneradas por Railway (e.g. `https://hme-fact-production.up.railway.app`).

* Accede a la URL pública `/health` y deberías obtener:
  ```json
  {
    "status": "ok",
    "version": "6.0.0"
  }
  ```
* Accede a `/docs` para ver la interfaz Swagger interactiva conectada a tu base de datos de Supabase.
