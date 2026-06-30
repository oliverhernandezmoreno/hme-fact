#!/bin/bash

# Aplicar migraciones de base de datos
echo "Aplicando migraciones con Alembic..."
alembic upgrade head

# Crear superusuario inicial (si no existe)
echo "Creando superusuario administrador..."
python -m app.cli.create_superuser

# Iniciar Celery Worker en segundo plano
echo "Iniciando Celery Worker..."
celery -A app.workers.celery_app worker --loglevel=info &

# Iniciar Celery Beat (Scheduler) en segundo plano
echo "Iniciando Celery Beat Scheduler..."
celery -A app.workers.celery_app beat --loglevel=info &

# Iniciar FastAPI (Uvicorn) en primer plano para mantener el contenedor activo
echo "Iniciando API FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
