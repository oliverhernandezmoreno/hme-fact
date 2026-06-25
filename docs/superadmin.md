# SuperAdmin Platform — hmEFact Fase 6

## Acceso

Solo usuarios con rol `SuperAdmin` (scope `platform`). El rol se asigna manualmente en DB o via CLI de seed.

## Dashboard Global

### Endpoints

```
GET  /api/v1/superadmin/companies                          → Todas las empresas (paginado)
PUT  /api/v1/superadmin/companies/{id}/suspend             → Suspender empresa
PUT  /api/v1/superadmin/companies/{id}/activate            → Reactivar empresa
GET  /api/v1/superadmin/subscriptions                      → Todas las suscripciones
POST /api/v1/superadmin/subscriptions                      → Asignar plan manual
GET  /api/v1/superadmin/metrics                            → Snapshot de métricas global
POST /api/v1/superadmin/metrics/refresh                    → Forzar recompute de métricas
GET  /api/v1/superadmin/users                              → Todos los usuarios
```

## Métricas Globales

```json
{
  "snapshot_date": "2026-06-24",
  "mrr": 1499500,
  "arr": 17994000,
  "active_companies": 42,
  "trial_companies": 8,
  "suspended_companies": 2,
  "total_users": 215,
  "dtes_this_month": 4820,
  "api_calls_this_month": 38200,
  "churn_rate_pct": 0.0238,
  "plan_distribution": {
    "starter": 15,
    "pyme": 20,
    "business": 7
  },
  "history": [...]
}
```

## Asignar Plan Manual

```bash
POST /api/v1/superadmin/subscriptions
Authorization: Bearer <superadmin_token>

{
  "company_id": "uuid-empresa",
  "plan_code": "enterprise"
}
```

## Suspender Empresa

```bash
PUT /api/v1/superadmin/companies/{id}/suspend
{
  "reason": "Pago vencido 30 días"
}
```

Suspende la suscripción Y desactiva la empresa en la DB.
