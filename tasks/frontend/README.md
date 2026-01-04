## Atomic Task Rules
- One task = one file = one responsibility.
- Design docs are source of truth.

# Frontend tasks — execute in order

## Prerequisite (Backend)
Frontend tasks assume backend is running.

```bash
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
