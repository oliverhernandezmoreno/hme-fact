from celery.schedules import crontab

from app.workers.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "retry-failed-dtes-every-hour": {
        "task": "app.workers.tasks.dte_tasks.retry_failed_dtes_task",
        "schedule": crontab(minute="0", hour="*"),
    },
}
