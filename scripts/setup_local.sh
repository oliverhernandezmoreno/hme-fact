#!/bin/bash
# ============================================================================
# hmEFact — Local Development Setup Script
# Run with: sudo bash scripts/setup_local.sh
# ============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     hmEFact — Configuración de Desarrollo Local     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo

# ── 1. Add user to docker group ──────────────────────────────────────────────
echo -e "${YELLOW}[1/4] Agregando usuario al grupo docker...${NC}"
if id -nG ohm | grep -qw docker; then
    echo -e "${GREEN}  ✓ Usuario 'ohm' ya está en el grupo docker${NC}"
else
    usermod -aG docker ohm
    echo -e "${GREEN}  ✓ Usuario 'ohm' agregado al grupo docker${NC}"
    echo -e "${YELLOW}  ⚠ Necesitarás cerrar sesión y volver a entrar para que surta efecto${NC}"
fi

# ── 2. Create PostgreSQL user and database ───────────────────────────────────
echo -e "${YELLOW}[2/4] Configurando PostgreSQL...${NC}"

# Check if user exists
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='hme_fact'" 2>/dev/null | grep -q 1; then
    echo -e "${GREEN}  ✓ Usuario PostgreSQL 'hme_fact' ya existe${NC}"
else
    sudo -u postgres psql -c "CREATE USER hme_fact WITH PASSWORD 'hme_fact' CREATEDB;" 2>/dev/null
    echo -e "${GREEN}  ✓ Usuario PostgreSQL 'hme_fact' creado${NC}"
fi

# Check if database exists
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='hme_fact'" 2>/dev/null | grep -q 1; then
    echo -e "${GREEN}  ✓ Base de datos 'hme_fact' ya existe${NC}"
else
    sudo -u postgres psql -c "CREATE DATABASE hme_fact OWNER hme_fact;" 2>/dev/null
    echo -e "${GREEN}  ✓ Base de datos 'hme_fact' creada${NC}"
fi

# Ensure pg_hba.conf allows password auth for hme_fact on localhost
PG_HBA="/etc/postgresql/16/main/pg_hba.conf"
if [ -f "$PG_HBA" ]; then
    if grep -q "hme_fact" "$PG_HBA"; then
        echo -e "${GREEN}  ✓ pg_hba.conf ya tiene configuración para hme_fact${NC}"
    else
        # Add md5 auth for hme_fact user before the default entries
        sed -i '/^# IPv4 local connections:/a host    hme_fact        hme_fact        127.0.0.1/32            md5' "$PG_HBA"
        sed -i '/^# IPv6 local connections:/a host    hme_fact        hme_fact        ::1/128                 md5' "$PG_HBA"
        systemctl reload postgresql
        echo -e "${GREEN}  ✓ pg_hba.conf actualizado y PostgreSQL recargado${NC}"
    fi
fi

# ── 3. Install Redis if not present ─────────────────────────────────────────
echo -e "${YELLOW}[3/4] Verificando Redis...${NC}"
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}  ✓ Redis ya está instalado${NC}"
else
    apt-get update -qq && apt-get install -y -qq redis-server
    echo -e "${GREEN}  ✓ Redis instalado${NC}"
fi

# Start Redis if not running
if systemctl is-active --quiet redis-server 2>/dev/null || redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "${GREEN}  ✓ Redis está corriendo${NC}"
else
    systemctl start redis-server 2>/dev/null || redis-server --daemonize yes
    echo -e "${GREEN}  ✓ Redis iniciado${NC}"
fi

# ── 4. Summary ───────────────────────────────────────────────────────────────
echo -e "${YELLOW}[4/4] Verificación final...${NC}"

echo -e "\n${BLUE}Estado de servicios:${NC}"
echo -n "  PostgreSQL: "
if pg_isready -q; then echo -e "${GREEN}✓ activo${NC}"; else echo -e "${RED}✗ inactivo${NC}"; fi

echo -n "  Redis:      "
if redis-cli ping 2>/dev/null | grep -q PONG; then echo -e "${GREEN}✓ activo${NC}"; else echo -e "${RED}✗ inactivo${NC}"; fi

echo -e "\n${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         ¡Configuración completada!                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo
echo -e "Próximos pasos (ejecutar SIN sudo, como usuario ohm):"
echo -e "  ${BLUE}1.${NC} cd /home/ohm/Documentos/hme-fact"
echo -e "  ${BLUE}2.${NC} source .venv/bin/activate"
echo -e "  ${BLUE}3.${NC} alembic upgrade head"
echo -e "  ${BLUE}4.${NC} python -m app.cli.create_superuser"
echo -e "  ${BLUE}5.${NC} python -m app.cli.seed_fase6"
echo -e "  ${BLUE}6.${NC} uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo -e "  ${BLUE}7.${NC} cd frontend && npm run dev  (en otra terminal)"
echo
