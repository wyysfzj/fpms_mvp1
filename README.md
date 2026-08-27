# FPMS MVP1 Blueprint (Copilot/Codex-ready)

This repository is an **architecture blueprint + scaffolding skeleton** for building **FPMS Web (MVP1)**.

- Backend: Python + FastAPI + SQLAlchemy (2.x) + Pydantic (2.x)
- DB: SQLite for dev/PoC; PostgreSQL for prod (same migrations)
- Frontend: Vue 3 + TypeScript + Pinia + Element Plus + Vite
- Office: docxtpl + python-docx (server-side `.docx` template rendering)
- Deploy: Docker (API + SPA), single-law-firm single instance

> Generated: 2025-12-13

## Quick start (Dev / PoC with SQLite)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm i
cp .env.example .env
npm run dev
```

- Frontend: http://localhost:5173
- Backend OpenAPI: http://localhost:8000/docs

## Customer Demo V6 handoff

For the verified V6 lifecycle and dual-track fee rehearsal, start with
`docs/postdemo/demo-v6-clone-deploy-handoff.md`. It contains the exact fresh-clone install,
build, Playwright acceptance, and alternate-Codex-account workflow.

The frozen `fpms.demo-v6-ui-parity/v1` path supports A technical regression plus B-HUMAN and
B-CODEX setup-only, normal-UI sessions. Its bundle remains `SYNTHETIC_TEST_ONLY`: it may be shown
to a customer only as a transparent synthetic technical demonstration, never as production data,
formal pricing, official submission, or official-payment proof. Do not use the generic Docker demo
as a substitute for the V6 handoff path.

## Docker demo (SQLite)

Use this path when the team needs a single-container demo on a laptop or a simple cloud container host while still using SQLite.

```bash
docker compose -f docker-compose.demo.yml up --build
```

- App URL: http://localhost:8080
- Default seeded login: `admin` / `admin123`
- Detailed guide: `docs/docker_demo_guide.md`

Docker demo file index:

- `Dockerfile.demo` - builds the Vue frontend, FastAPI backend runtime, and nginx into one demo image.
- `docker-compose.demo.yml` - runs the SQLite demo container and persists `/data` in the `fpms_demo_data` volume.
- `.dockerignore` - excludes local dependencies, build outputs, local env files, and SQLite files from the image build context.
- `deploy/docker/demo/entrypoint.sh` - runs migrations, optional seed, backend API, and nginx at container startup.
- `deploy/docker/demo/nginx.conf` - serves the SPA and proxies `/api/*`, `/healthz`, `/docs`, `/redoc`, and `/openapi.json`.
- `docs/docker_demo_guide.md` - laptop and cloud deployment guide, including persistence, backup, reset, and troubleshooting.

## Production (Docker + Postgres)
```bash
cp .env.prod.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

## How to use this blueprint with Copilot/Codex
- Read the design docs under:
  - `docs/` (global)
  - `backend/app/modules/**/docs/` (backend module constraints)
  - `frontend/src/modules/**/docs/` (frontend module constraints)
- Then execute tasks under `tasks/` in order. Each task contains a ready-to-paste prompt.

## Non-MVP
Each module includes a `*_future.md` to park non-MVP requirements and avoid scope creep.
