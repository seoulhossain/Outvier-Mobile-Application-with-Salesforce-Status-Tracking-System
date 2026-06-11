#!/bin/bash
# Outvier — One-command setup AND start
# Usage (macOS): bash start.sh
#
# First run:  installs everything, creates DB, seeds demo data, then starts app
# Later runs: skips setup, starts app directly

BASE="$( cd "$( dirname "$0" )" && pwd )"
BACKEND="$BASE/outvier_backend"
FRONTEND="$BASE/outvier_frontend"
VENV="$BACKEND/.venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"
CELERY="$VENV/bin/celery"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[OUTVIER]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── 1. Check Python 3.11+ ────────────────────────────────────────────────
log "Checking Python..."
PYTHON_BIN=""
for v in python3.12 python3.11 python3; do
  if command -v "$v" &>/dev/null; then
    MAJ=$("$v" -c "import sys; print(sys.version_info.major)")
    MIN=$("$v" -c "import sys; print(sys.version_info.minor)")
    if [ "$MAJ" -ge 3 ] && [ "$MIN" -ge 11 ]; then
      PYTHON_BIN="$v"; break
    fi
  fi
done
[ -z "$PYTHON_BIN" ] && err "Python 3.11+ not found. Install: brew install python@3.11"
log "  Python OK: $($PYTHON_BIN --version)"

# ── 2. Check Node.js 18+ ─────────────────────────────────────────────────
log "Checking Node.js..."
command -v node &>/dev/null || err "Node.js not found. Install: brew install node"
NODE_VER=$(node -e "process.stdout.write(process.versions.node.split('.')[0])")
[ "$NODE_VER" -lt 18 ] && err "Node.js 18+ required. Got: $(node --version). Run: brew upgrade node"
log "  Node OK: $(node --version)"

# ── 3. Check PostgreSQL ──────────────────────────────────────────────────
log "Checking PostgreSQL..."
command -v psql &>/dev/null || err "PostgreSQL not found. Install: brew install postgresql@15"

# ── 4. Start Redis ───────────────────────────────────────────────────────
log "Checking Redis..."
if ! redis-cli ping &>/dev/null 2>&1; then
  log "  Starting Redis..."
  if command -v brew &>/dev/null; then
    brew services start redis &>/dev/null || true
  fi
  redis-server --daemonize yes --loglevel warning 2>/dev/null || true
  sleep 1
  redis-cli ping &>/dev/null 2>&1 || err "Redis failed to start. Install: brew install redis"
fi
log "  Redis OK"

# ── 5. Start PostgreSQL ──────────────────────────────────────────────────
if ! pg_isready -q 2>/dev/null; then
  log "  Starting PostgreSQL..."
  brew services start postgresql@15 2>/dev/null || \
  brew services start postgresql@16 2>/dev/null || \
  brew services start postgresql 2>/dev/null || true
  sleep 2
fi
pg_isready -q 2>/dev/null || err "PostgreSQL failed to start. Run: brew services start postgresql@15"
log "  PostgreSQL OK"

# ── 6. Create .env if missing ────────────────────────────────────────────
if [ ! -f "$BACKEND/.env" ]; then
  log "Creating .env configuration file..."
  cat > "$BACKEND/.env" << 'ENVEOF'
SECRET_KEY=django-insecure-8f6y6y6r4k4x0d2y0h1h9d3k7c5v8n6m5b4a2s1q0w9e8r7t6y5u4i3o2p1l0z9x
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=outvier_db
DB_USER=outvier_user
DB_PASSWORD=arka
DB_HOST=127.0.0.1
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=
SALESFORCE_USERNAME=
SALESFORCE_PASSWORD=
SALESFORCE_SECURITY_TOKEN=
SALESFORCE_DOMAIN=login

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@outvier.com

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081
SALESFORCE_SYNC_INTERVAL_MINUTES=15
FCM_SERVER_KEY=
SALESFORCE_WEBHOOK_SECRET=
ENVEOF
  log "  .env created"
fi

# ── 7. Create DB and user (safe — skips if already exists) ───────────────
if ! psql -U outvier_user -d outvier_db -c "SELECT 1" &>/dev/null 2>&1; then
  log "Setting up database..."
  # Try connecting as 'postgres' superuser, fall back to current macOS user
  PSQL_CMD="psql"
  psql -U postgres -c "SELECT 1" &>/dev/null 2>&1 && PSQL_CMD="psql -U postgres"

  $PSQL_CMD -c "CREATE USER outvier_user WITH PASSWORD 'arka';" 2>/dev/null || true
  $PSQL_CMD -c "CREATE DATABASE outvier_db OWNER outvier_user;" 2>/dev/null || true
  $PSQL_CMD -c "GRANT ALL PRIVILEGES ON DATABASE outvier_db TO outvier_user;" 2>/dev/null || true
  log "  Database ready"
else
  log "  Database already exists"
fi

# ── 8. Create Python virtual environment ─────────────────────────────────
if [ ! -f "$PYTHON" ]; then
  log "Creating Python virtual environment..."
  "$PYTHON_BIN" -m venv "$VENV"
  log "  Virtual environment created"
fi

# ── 9. Install Python packages ───────────────────────────────────────────
MARKER="$VENV/.packages_installed"
REQ_HASH=$(md5 -q "$BACKEND/requirements.txt" 2>/dev/null || md5sum "$BACKEND/requirements.txt" 2>/dev/null | cut -d' ' -f1)
if [ ! -f "$MARKER" ] || [ "$(cat "$MARKER" 2>/dev/null)" != "$REQ_HASH" ]; then
  log "Installing Python packages (first time ~1 min)..."
  "$PIP" install --upgrade pip -q
  "$PIP" install -r "$BACKEND/requirements.txt" -q
  echo "$REQ_HASH" > "$MARKER"
  log "  Python packages installed"
else
  log "  Python packages up to date"
fi

# ── 10. Run migrations ───────────────────────────────────────────────────
log "Running database migrations..."
cd "$BACKEND"
"$PYTHON" manage.py migrate --run-syncdb 2>&1 | grep -E "Applying|No migrations to apply" || true
log "  Migrations complete"

# ── 11. Seed demo data (once only) ───────────────────────────────────────
SEED_MARKER="$BACKEND/.demo_seeded"
if [ ! -f "$SEED_MARKER" ]; then
  log "Seeding demo accounts and data..."
  "$PYTHON" manage.py seed_demo 2>&1 | tail -5
  touch "$SEED_MARKER"
  log "  Demo data seeded"
else
  log "  Demo data already seeded"
fi

# ── 12. Install Node packages ────────────────────────────────────────────
if [ ! -d "$FRONTEND/node_modules" ]; then
  log "Installing Node packages (first time ~30 sec)..."
  npm --prefix "$FRONTEND" install --silent
  log "  Node packages installed"
else
  log "  Node packages up to date"
fi

# ── 13. Open 4 Terminal windows and start services ───────────────────────
log "Launching all services..."
sleep 1

osascript -e "tell app \"Terminal\" to do script \"echo '=== Django API Server ===' && $PYTHON $BACKEND/manage.py runserver 0.0.0.0:8000\""
sleep 1
osascript -e "tell app \"Terminal\" to do script \"echo '=== Celery Worker ===' && cd $BACKEND && $CELERY -A outvier_backend worker --loglevel=info\""
sleep 1
osascript -e "tell app \"Terminal\" to do script \"echo '=== Celery Beat (scheduler) ===' && cd $BACKEND && $CELERY -A outvier_backend beat --loglevel=info\""
sleep 1
osascript -e "tell app \"Terminal\" to do script \"echo '=== React Frontend ===' && npm --prefix $FRONTEND run dev\""

echo ""
echo "========================================================"
echo "  Outvier is starting!"
echo "  Browser: http://localhost:3000"
echo ""
echo "  Admin login:   admin / arka"
echo "  Student login: alex  / alex1234"
echo "========================================================"
echo ""
echo "  Tip: Re-running this script later skips all setup"
echo "       steps and just starts the services."
echo "========================================================"
