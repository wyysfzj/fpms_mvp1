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

