# RBAC — Control de Acceso Basado en Roles

## Roles del Sistema

| Rol | Scope | Descripción |
|---|---|---|
| `SuperAdmin` | `platform` | Control total de la plataforma — bypassa todos los checks |
| `CompanyOwner` | `company` | Propietario — acceso total a su empresa |
| `Accountant` | `company` | DTE, clientes, productos, billing (solo lectura) |
| `Seller` | `company` | Solo emisión de DTE y lectura de clientes/productos |
| `Viewer` | `company` | Solo lectura en toda la empresa |
| `APIUser` | `company` | Autenticación por API Key — DTE y clientes |

## Arquitectura

RBAC **desacoplado de JWT**: los roles y permisos se resuelven por consulta a DB en cada request. El JWT solo contiene `user_id`.

```
Request → JWT decode (user_id) → RBACService.has_permission(user_id, company_id, module, action) → DB query
```

## Uso en Endpoints

```python
from app.core.deps.rbac import require_permission, SuperAdminRequired

# Proteger por permiso específico
@router.post("/dte")
async def emit_dte(
    _: None = require_permission("dte", "write"),
    ...
):
    ...

# Proteger por rol SuperAdmin
@router.get("/superadmin/metrics", dependencies=[SuperAdminRequired])
async def global_metrics():
    ...
```

## Matriz de Permisos

| Módulo | Acción | SuperAdmin | CompanyOwner | Accountant | Seller | Viewer |
|---|---|---|---|---|---|---|
| dte | write | ✅ | ✅ | ✅ | ✅ | ❌ |
| dte | read | ✅ | ✅ | ✅ | ✅ | ✅ |
| billing | write | ✅ | ✅ | ❌ | ❌ | ❌ |
| billing | read | ✅ | ✅ | ✅ | ❌ | ✅ |
| api_keys | write | ✅ | ✅ | ❌ | ❌ | ❌ |
| users | write | ✅ | ✅ | ❌ | ❌ | ❌ |

## Endpoints

```
GET    /api/v1/rbac/roles                         → Roles disponibles
GET    /api/v1/rbac/my-permissions                → Mis permisos actuales
POST   /api/v1/rbac/users/{id}/roles              → Asignar rol a usuario
DELETE /api/v1/rbac/users/{id}/roles/{role_name}  → Quitar rol
```

## Seed

Los roles se crean automáticamente al ejecutar:
```bash
python -m app.cli.seed_fase6
```
