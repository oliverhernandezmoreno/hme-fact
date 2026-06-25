# 🚀 Guía de Levantamiento Local — hmEFact

Guía completa para levantar el sistema hmEFact en modo desarrollo local, sin depender
de Docker para ejecutar el backend y el frontend.

---

## Requisitos Previos

| Componente | Versión Mínima | Verificar con |
|---|---|---|
| Python | 3.12 | `python3 --version` |
| Node.js | 22 LTS | `node --version` |
| PostgreSQL | 16 | `pg_isready` |
| Redis | 7+ | `redis-cli ping` |
| Docker *(opcional)* | 24+ | `docker --version` |

---

## Arquitectura Local

```text
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Frontend   │────▶│    Backend API   │────▶│  PostgreSQL   │
│  Next.js     │     │  FastAPI/Uvicorn │     │  Puerto 5432  │
│  Puerto 3000 │     │  Puerto 8000    │     └──────────────┘
└──────────────┘     │                 │     ┌──────────────┐
                     │                 │────▶│    Redis      │
                     │                 │     │  Puerto 6379  │
                     └────────┬────────┘     └──────────────┘
                              │
                     ┌────────▼────────┐     ┌──────────────┐
                     │  Celery Worker   │────▶│   MailHog     │
                     │  (opcional)      │     │  Puerto 8025  │
                     └─────────────────┘     └──────────────┘
```

---

## Paso 1 — Setup de Infraestructura

### Opción A: Script Automatizado (Recomendado)

```bash
cd /home/ohm/Documentos/hme-fact
sudo bash scripts/setup_local.sh
```

El script realiza automáticamente:
- Crea el usuario PostgreSQL `hme_fact` con contraseña `hme_fact`
- Crea la base de datos `hme_fact`
- Configura `pg_hba.conf` para autenticación por contraseña en localhost
- Instala Redis si no está presente
- Agrega tu usuario al grupo `docker` (para uso futuro)

### Opción B: Manual

```bash
# 1. Crear usuario y BD en PostgreSQL
sudo -u postgres psql -c "CREATE USER hme_fact WITH PASSWORD 'hme_fact' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE hme_fact OWNER hme_fact;"

# 2. Instalar Redis
sudo apt-get update && sudo apt-get install -y redis-server
sudo systemctl enable --now redis-server

# 3. Verificar conexiones
psql "postgresql://hme_fact:hme_fact@127.0.0.1:5432/hme_fact" -c "SELECT 1;"
redis-cli ping   # Debe responder PONG
```

---

## Paso 2 — Variables de Entorno

### Backend (`.env`)

```bash
cp .env.example .env
```

Modifica las siguientes variables para modo local (sin Docker networking):

```ini
POSTGRES_HOST="127.0.0.1"
POSTGRES_PORT=5432
REDIS_URL="redis://127.0.0.1:6379/0"
CELERY_BROKER_URL="redis://127.0.0.1:6379/2"
CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/2"
SMTP_HOST="127.0.0.1"
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
DEBUG=true
LOG_LEVEL="DEBUG"
```

> **Nota:** Las hostnames `postgres`, `redis`, `mailhog` del `.env.example` son nombres de
> servicio Docker. Para ejecución local, se reemplazan por `127.0.0.1`.

### Frontend (`frontend/.env.local`)

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_USE_MOCKS=false
NEXT_PUBLIC_APP_NAME=HME Fact
```

Poner `NEXT_PUBLIC_USE_MOCKS=false` desactiva el sistema de mocks y conecta al backend real.

---

## Paso 3 — Migraciones de Base de Datos

```bash
source .venv/bin/activate
alembic upgrade head
```

### Migraciones Disponibles

| Migración | Descripción |
|---|---|
| `0001_initial_schema` | Users, companies, customers, products |
| `0002_add_dte_xml` | Campos XML para DTE |
| `0003_add_dte_reference_fields` | Campos de referencia DTE (notas de crédito/débito) |
| `0004_add_tax_integrations` | Integración tributaria, CAF, certificados |
| `0005_phase5_updates` | PDF, audit trail, almacenamiento de archivos |
| `0006_fase6_saas_platform` | Billing, suscripciones, RBAC, onboarding, API keys |
| `0007_phase7_integrations` | Webhooks, integraciones ERP, conectores eCommerce |

### Comandos Útiles

```bash
alembic current            # Ver migración actual
alembic history            # Historial completo
alembic downgrade -1       # Revertir última migración
alembic downgrade base     # Revertir todas
```

---

## Paso 4 — Datos Iniciales (Seed)

### Crear Superusuario

```bash
python -m app.cli.create_superuser
```

| Campo | Valor |
|---|---|
| Email | Definido en `FIRST_SUPERUSER_EMAIL` (.env) |
| Password | Definido en `FIRST_SUPERUSER_PASSWORD` (.env) |

Valores por defecto: `admin@hmefact.cl` / `Admin123!`

### Seed de Planes y Roles (Fase 6)

```bash
python -m app.cli.seed_fase6
```

Crea:

| Tipo | Datos |
|---|---|
| **Planes** | Starter (gratis), PyME ($29.990), Business ($79.990), Enterprise (custom) |
| **Roles** | SuperAdmin, CompanyOwner, Accountant, Seller, Viewer, APIUser |
| **Permisos** | CRUD granular por recurso (companies, dte, customers, products, etc.) |

---

## Paso 5 — Levantar Servicios

### Terminal 1: Backend API

```bash
cd /home/ohm/Documentos/hme-fact
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verificar:
- **Health:** http://localhost:8000/health → `{"status":"ok","version":"6.0.0"}`
- **Swagger UI:** http://localhost:8000/docs
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

### Terminal 2: Frontend

```bash
cd /home/ohm/Documentos/hme-fact/frontend
npm run dev
```

Acceder: http://localhost:3000

### Terminal 3: Celery Worker (Opcional)

Necesario solo si vas a probar emisión de DTEs, procesamiento de CAF, o tareas asíncronas.

```bash
cd /home/ohm/Documentos/hme-fact
source .venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

### Terminal 4: Celery Beat Scheduler (Opcional)

Para tareas periódicas (limpieza de tokens expirados, etc.):

```bash
celery -A app.workers.celery_app beat --loglevel=info
```

---

## Paso 6 — Pruebas Manuales

### 6.1 Health Check

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

```json
{
    "status": "ok",
    "version": "6.0.0"
}
```

### 6.2 Login — Obtener JWT

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@hmefact.cl&password=Admin123!" | python3 -m json.tool
```

Guardar el `access_token` devuelto:

```bash
export TOKEN="<access_token_from_response>"
```

### 6.3 Crear una Empresa

```bash
curl -s -X POST http://localhost:8000/api/v1/companies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "76.000.000-0",
    "razon_social": "Empresa Demo SpA",
    "giro": "Servicios de Software",
    "direccion": "Av. Providencia 1234",
    "comuna": "Providencia",
    "ciudad": "Santiago",
    "actividad_economica": 620200
  }' | python3 -m json.tool
```

### 6.4 Listar Planes de Suscripción

```bash
curl -s http://localhost:8000/api/v1/subscriptions/plans \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 6.5 Probar Frontend

1. Navegar a http://localhost:3000
2. Login con `admin@hmefact.cl` / `Admin123!`
3. Secciones para verificar:
   - **Dashboard** — Métricas y resumen
   - **Empresas** — CRUD de empresas
   - **Clientes** — Gestión de receptores
   - **Productos** — Catálogo
   - **DTEs** — Emisión de documentos
   - **Onboarding** — Wizard de configuración inicial

---

## Alternativa: Levantar con Docker Compose

Si prefieres usar Docker Compose (levanta todo containerizado):

```bash
# Asegúrate de estar en el grupo docker
sudo usermod -aG docker $USER
# Cierra sesión y vuelve a entrar, luego:

docker-compose up --build -d

# Migraciones
docker-compose exec backend alembic upgrade head

# Seed
docker-compose exec backend python -m app.cli.create_superuser
docker-compose exec backend python -m app.cli.seed_fase6
```

> **Nota:** Si PostgreSQL local ocupa el puerto 5432, el `docker-compose.yml` expone
> el PostgreSQL de Docker en el puerto **5434** para evitar conflictos. Los servicios
> internos se comunican por nombre de servicio, no por puerto expuesto.

### Puertos Docker Compose

| Servicio | Puerto Externo | Puerto Interno |
|---|---|---|
| Frontend | 3000 | 3000 |
| Backend | 8000 | 8000 |
| PostgreSQL | 5434 | 5432 |
| Redis | 6379 | 6379 |
| MailHog SMTP | 1025 | 1025 |
| MailHog Web UI | 8025 | 8025 |

---

## Troubleshooting

### PostgreSQL

| Problema | Solución |
|---|---|
| `Connection refused` | Verificar: `pg_isready` |
| `password authentication failed` | Recrear usuario: `sudo -u postgres psql -c "ALTER USER hme_fact PASSWORD 'hme_fact';"` |
| `role "hme_fact" does not exist` | Ejecutar setup: `sudo bash scripts/setup_local.sh` |
| Puerto 5432 en conflicto (Docker) | El docker-compose usa puerto **5434** externo |

### Redis

| Problema | Solución |
|---|---|
| `Connection refused` | `sudo systemctl start redis-server` |
| `redis-server: command not found` | `sudo apt-get install -y redis-server` |

### Alembic

| Problema | Solución |
|---|---|
| `Target database is not up to date` | `alembic upgrade head` |
| Conflicto de migración | `alembic downgrade base && alembic upgrade head` |
| `ModuleNotFoundError` | Activar venv: `source .venv/bin/activate` |

### Frontend

| Problema | Solución |
|---|---|
| No conecta al backend | Verificar `frontend/.env.local`: `NEXT_PUBLIC_USE_MOCKS=false` |
| CORS errors | Verificar `BACKEND_CORS_ORIGINS=["http://localhost:3000"]` en `.env` |
| `MODULE_NOT_FOUND` | `cd frontend && npm install` |

### Dependencias del Sistema (xmlsec)

Si `pip install` falla al compilar `xmlsec`:

```bash
sudo apt-get install -y libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config
```
