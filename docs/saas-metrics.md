# Métricas SaaS — hmEFact Fase 6

## KPIs Implementados

| KPI | Fuente | Frecuencia |
|---|---|---|
| MRR (Monthly Recurring Revenue) | Suma precios planes activos | Diario |
| ARR (Annual Recurring Revenue) | MRR × 12 | Diario |
| Active Companies | Suscripciones status=active | Diario |
| Trial Companies | Suscripciones status=trial | Diario |
| Churn Rate % | Cancelaciones / activos del mes | Diario |
| DTE del mes | Suma usage_metrics del período | Diario |
| API Calls del mes | Suma usage_metrics del período | Diario |
| Plan Distribution | Group by subscription.plan | Diario |

## Tabla de Snapshots

```sql
-- saas_metrics_snapshots
snapshot_date     DATE    UNIQUE NOT NULL
period_label      TEXT    -- "2026-06"
mrr               NUMERIC
arr               NUMERIC
active_companies  INT
trial_companies   INT
dtes_this_month   INT
churn_rate_pct    NUMERIC(6,4)
plan_distribution JSONB   -- {"pyme": 20, "business": 7}
```

## Consultar Histórico

```bash
GET /api/v1/superadmin/metrics
```

Devuelve el snapshot más reciente + historial de 30 días.

## Forzar Recompute

```bash
POST /api/v1/superadmin/metrics/refresh
```

## Celery Task

El snapshot se computa automáticamente a las **02:00 UTC** diariamente:

```python
# app/workers/tasks/billing_tasks.py
@celery_app.task(name="...compute_saas_metrics_snapshot")
def compute_saas_metrics_snapshot(self):
    ...
```

## Fórmulas

```
MRR = SUM(plan.price) WHERE subscription.status = 'active'
ARR = MRR * 12
Churn Rate = churned_this_month / active_companies * 100
Growth Rate = (new_companies - churned) / previous_active * 100  [TODO Fase 7]
```
