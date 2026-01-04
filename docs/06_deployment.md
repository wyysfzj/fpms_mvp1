# Deployment & Environment Strategy

## Environments
- Dev/PoC: SQLite, local run (uvicorn + vite)
- Prod: Postgres, docker compose

## Container model
- `api` container: FastAPI app
- `web` container: Nginx serving SPA build
- `db` container: Postgres

## Configuration
- Backend config via environment variables:
  - `DATABASE_URL`
  - `CORS_ORIGINS`
  - `JWT_SECRET`
  - `FPMS_ENV`
- Frontend config via `VITE_API_BASE_URL`

## Migrations
- Always run `alembic upgrade head` as part of deployment.
- Provide `scripts/migrate.sh` in production pipelines (future).

