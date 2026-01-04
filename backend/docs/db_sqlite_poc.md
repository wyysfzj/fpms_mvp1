# SQLite PoC (Dev)

Config (backend/.env):
- DATABASE_URL=sqlite:///./fpms_dev.db

Bootstrap:
```bash
cd backend
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Notes:
- SQLite used for PoC/dev only.
- Avoid PG-only types in migrations for compatibility.
