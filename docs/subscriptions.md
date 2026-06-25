# Suscripciones y Planes — OhmEFACT Fase 6

## Planes Disponibles

| Plan | Precio CLP/mes | DTE/mes | Usuarios | Sucursales | API | Soporte |
|---|---|---|---|---|---|---|
| **Starter** | Gratis | 50 | 2 | 1 | ❌ | Comunidad |
| **PyME** | $29.990 | 500 | 10 | 3 | ✅ | Email |
| **Business** | $79.990 | 2.000 | 50 | 10 | ✅ | Prioritario |
| **Enterprise** | Custom | ∞ | ∞ | ∞ | ✅ | Dedicado |

## Ciclo de Vida

```
[sin suscripción] → activate() → [active / trial]
[active]          → suspend()  → [suspended]
[active]          → cancel()   → [cancelled / cancel_at_period_end]
[active]          → renew()    → [active] (nuevo período)
[active]          → change_plan() → [active] (nuevo plan)
[active/trial]    → expired    → [expired] (automático via Celery)
```

## Endpoints

### Portal Cliente (JWT auth + X-Company-ID)

```
GET  /api/v1/subscriptions/plans         → Listar planes públicos
GET  /api/v1/subscriptions/my            → Suscripción activa de empresa
GET  /api/v1/subscriptions/usage         → Consumo del período actual
POST /api/v1/subscriptions/activate      → Activar plan {"plan_code": "pyme", "trial": false}
PUT  /api/v1/subscriptions/change-plan   → Cambiar plan {"plan_code": "business"}
POST /api/v1/subscriptions/cancel        → Cancelar ?at_period_end=true
GET  /api/v1/subscriptions/billing-events → Historial de eventos
```

## Control de Cuotas

El `QuotaMiddleware` intercepta **POST /api/v1/dte** y **POST /public/v1/dte** antes de que lleguen al endpoint:

```
Request → QuotaMiddleware.check_dte_quota() → [allowed] → Endpoint DTE
                                           → [exceeded] → HTTP 402 Payment Required
```

### Respuesta 402 al exceder cuota

```json
{
  "error": "quota_exceeded",
  "message": "DTE quota exceeded (500/500 used this month)",
  "detail": {
    "feature": "dte_limit",
    "used": 500,
    "limit": 500,
    "usage_pct": 100.0
  }
}
```

## Tareas Automáticas (Celery Beat)

| Task | Horario | Descripción |
|---|---|---|
| `renew_expiring_subscriptions` | 00:00 UTC diario | Renueva suscripciones que expiran en 48h |
| `compute_saas_metrics_snapshot` | 02:00 UTC diario | Persiste snapshot de métricas |
| `reset_monthly_usage_counters` | 01:00 UTC el día 1 | Prepara nuevos contadores de período |
| `send_quota_warning_emails` | 08:00 UTC diario | Alerta empresas con uso >80% |

## Seed de Planes

```bash
cd /app && python -m app.cli.seed_fase6
```
