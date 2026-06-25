# HME Fact Backend

Backend inicial para un SaaS multiempresa de facturacion electronica chilena orientado al SII.

## Stack

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0 async
- Alembic
- Pydantic v2
- JWT
- Redis
- Docker Compose

## Estructura

```text
app/
  api/              Routers versionados y dependencias HTTP
  core/             Settings, seguridad, logging y errores
  db/               Base declarativa y sesiones AsyncSession
  models/           Modelos SQLAlchemy por dominio
  repositories/     Acceso a datos
  schemas/          DTOs Pydantic v2
  services/         Casos de uso y reglas de aplicacion
alembic/            Migraciones
```

## Levantar localmente

### Opción A — Docker Compose (todo containerizado)

```bash
cp .env.example .env
docker-compose up --build -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.cli.create_superuser
docker-compose exec backend python -m app.cli.seed_fase6
```

### Opción B — Desarrollo local (sin Docker para backend/frontend)

```bash
sudo bash scripts/setup_local.sh   # PostgreSQL + Redis + grupo docker
cp .env.example .env                # Ajustar hosts a 127.0.0.1
source .venv/bin/activate
alembic upgrade head
python -m app.cli.create_superuser
python -m app.cli.seed_fase6
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# En otra terminal:
cd frontend && npm run dev
```

> 📘 **Guía completa con troubleshooting:** [docs/local-setup.md](docs/local-setup.md)

### Endpoints principales

- **Health:** http://localhost:8000/health
- **Swagger UI:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000

## Autenticacion

Haz login en `POST /api/v1/auth/login` con formulario OAuth2 usando `username` como email y `password` con la clave configurada en `.env`.
Los endpoints de `customers` y `products` requieren:

- `Authorization: Bearer <token>`
- `X-Company-ID: <uuid_empresa>`

Primero crea una empresa con `POST /api/v1/companies`; el usuario autenticado queda asociado como `owner`.

## Migraciones

Crear una nueva migracion:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
```

Aplicar migraciones:

```bash
docker compose exec backend alembic upgrade head
```

## Motor XML Tributario

La Fase 2 agrega `app/modules/xml`, separado por responsabilidades:

```text
app/modules/xml/
  builders/     Construccion lxml por tipo DTE
  schemas/      DTOs tributarios internos
  validators/   Validaciones de datos y estructura XML
  services/     Render, mapeo ORM -> XML y puertos de firma
  templates/    Ejemplos XML de referencia
  utils/        Helpers de nodos, fechas y montos SII
```

Flujo tributario actual:

1. `POST /api/v1/dte/{id}/generate-xml` recibe el DTE.
2. El repositorio carga DTE, empresa, receptor, items, CAF y certificado.
3. `XmlRenderService` valida reglas tributarias basicas.
4. `DTEXmlBuilderFactory` selecciona builder para tipo 33, 39 o 61.
5. El builder genera XML con `lxml.etree`, namespace SII y orden estricto:
   `Encabezado`, `Detalle`, `Referencia` cuando aplica, `TED`, `TmstFirma`.
6. El XML se valida como well-formed y se persiste en `dte_xml`.
7. El endpoint retorna `application/xml`.

El TED, CAF y firma XML quedan como puntos de extension. El placeholder actual permite validar estructura y preparar el siguiente paso, pero para envio real al SII debe reemplazarse por CAF real y firma criptografica con `xmlsec`.

Para extender a otros DTE:

1. Agrega el tipo al enum/check constraint si corresponde.
2. Crea un builder en `app/modules/xml/builders`.
3. Registralo en `DTEXmlBuilderFactory`.
4. Agrega validaciones especificas en `DTEXmlDataValidator`.
5. Cubre el orden de nodos con tests unitarios.

## Testing

El proyecto tiene una arquitectura de testing separada por alcance:

```text
tests/
  unit/          Pruebas rapidas sin servicios externos
  integration/   FastAPI + SQLAlchemy async + PostgreSQL test
  e2e/           Flujos completos listos para crecer
  factories/     Factory Boy para entidades de dominio
  fixtures/      Fixtures compartidas
  mocks/         Mocks HTTP de SII, SimpleAPI y proveedores externos
  utils/         Utilidades de testing
```

Instalar dependencias de desarrollo:

```bash
make install-dev
```

Ejecutar tests localmente requiere PostgreSQL de testing escuchando en `localhost:5433`.
Puedes levantarlo con Docker Compose:

```bash
docker-compose --profile test up -d postgres-test redis
```

Luego:

```bash
make test
make test-unit
make test-integration
make coverage
```

Ejecutar todo dentro de Docker:

```bash
make docker-test
```

Comandos directos equivalentes:

```bash
scripts/test-local.sh
scripts/test-docker.sh
scripts/coverage.sh
```

Coverage esta configurado con minimo 80%, reporte en terminal y reporte HTML en `htmlcov/`.

Troubleshooting comun:

- `pytest: command not found`: ejecuta `make install-dev`.
- Error de conexion PostgreSQL local: levanta `postgres-test` o revisa `.env.test`.
- Error instalando `xmlsec`: instala `libxml2-dev`, `libxmlsec1-dev`, `libxmlsec1-openssl` y `pkg-config`.
- Tests de integracion fallan por datos previos: la fixture limpia todas las tablas antes y despues de cada test contra la DB `hme_fact_test`.
