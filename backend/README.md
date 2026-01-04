# Backend (FastAPI)

See module docs under `app/modules/**/docs/` before coding.

## Dev
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

