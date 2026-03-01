# FPMS MVP1 Deployment Runbook

## Deployment prerequisites
- Python: 3.11+
- Database: SQLite for MVP1 dev; production DB depends on your environment.
- Required environment variables: see `docs/environment_variables.md`

## Build / Install
This repo uses a `pyproject.toml` with PEP 621 metadata. Install from the `backend/` directory:

```bash
cd backend
python3 -m pip install -e .
```

Optional dev tools:

```bash
cd backend
python3 -m pip install -e ".[dev]"
```

## Database migration
Run migrations from the backend directory:

```bash
cd backend
alembic upgrade head
```

Verify the migration version:

```bash
cd backend
sqlite3 fpms_dev.db "select * from alembic_version;"
```

Rollback guidance (use with caution):

```bash
cd backend
alembic downgrade -1
```

⚠️ Some MVP1 migrations are forward-only by design; downgrade may not be supported in all cases.

## Seed data
Seed roles/permissions and create the admin user:

```bash
cd backend
python3 scripts/seed_dev.py
```

If permissions drift is suspected, rescan and reseed:

```bash
cd backend
python3 scripts/scan_perms.py
python3 scripts/seed_dev.py
```

## Start the service
Run the FastAPI app with Uvicorn:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Note: For production, place a reverse proxy (e.g., Nginx) in front of Uvicorn; MVP1 keeps this minimal.

## Post-deploy smoke checks
Basic health and docs:

```bash
curl -s -i http://localhost:8000/healthz
curl -s -i http://localhost:8000/docs
```

Authenticate and call a protected endpoint:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

curl -s -i "http://localhost:8000/api/v1/clients?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
```

Permission sync verification (run if 403s occur):

```bash
cd backend
python3 scripts/scan_perms.py
python3 scripts/seed_dev.py
```

## Backup / Restore (MVP1 pragmatic)
- SQLite (dev): copy the database file (e.g., `fpms_dev.db`) while the app is stopped.
- Production DB: use your database’s standard backup/restore tooling (vendor-specific).

## Troubleshooting
- Import path issues: ensure commands run from `backend/` and `PYTHONPATH=backend` when needed.
- Missing env vars: validate `.env` values and defaults in `docs/environment_variables.md`.
- 401/403 after deploy: re-run `scripts/scan_perms.py` + `scripts/seed_dev.py`, then re-login for a new token.
