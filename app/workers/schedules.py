from celery.schedules import crontab

from app.workers.celery_app import celery_app

celery_app.conf.beat_schedule = {
    # Fase 5 — DTE retry
    "retry-failed-dtes-every-hour": {
        "task": "app.workers.tasks.dte_tasks.retry_failed_dtes_task",
        "schedule": crontab(minute="0", hour="*"),
    },
    # Fase 6 — SaaS platform tasks
    "renew-expiring-subscriptions-daily": {
        "task": "app.workers.tasks.billing_tasks.renew_expiring_subscriptions",
        "schedule": crontab(minute="0", hour="0"),  # Daily at midnight UTC
    },
    "compute-saas-metrics-daily": {
        "task": "app.workers.tasks.billing_tasks.compute_saas_metrics_snapshot",
        "schedule": crontab(minute="0", hour="2"),  # Daily at 02:00 UTC
    },
    "reset-monthly-usage-counters": {
        "task": "app.workers.tasks.billing_tasks.reset_monthly_usage_counters",
        "schedule": crontab(minute="0", hour="1", day_of_month="1"),  # 1st of each month
    },
    "send-quota-warning-emails": {
        "task": "app.workers.tasks.billing_tasks.send_quota_warning_emails",
        "schedule": crontab(minute="0", hour="8"),  # Daily at 08:00 UTC
    },
    "check-expiring-certificates-daily": {
        "task": "app.workers.tasks.alert_tasks.check_expiring_certificates_task",
        "schedule": crontab(minute="0", hour="4"),  # Daily at 04:00 UTC
    },
    "check-depleted-cafs-daily": {
        "task": "app.workers.tasks.alert_tasks.check_depleted_cafs_task",
        "schedule": crontab(minute="30", hour="4"),  # Daily at 04:30 UTC
    },
}
