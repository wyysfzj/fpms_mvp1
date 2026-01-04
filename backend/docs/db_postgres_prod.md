# Postgres Production

Config:
- DATABASE_URL=postgresql+psycopg://user:pass@host:5432/fpms

Migrate:
```bash
cd backend
alembic upgrade head
```
