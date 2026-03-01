# FPMS Environment Variables

## How configuration is loaded
Configuration is defined in `app/core/config.py` via the `Settings` class (Pydantic `BaseSettings`).
It loads values from:
1) OS environment variables
2) `.env` file (see `model_config = SettingsConfigDict(env_file=".env", ...)`)
3) Code defaults in `Settings`

## Variables (table)

| Variable | Required | Default | Example | Description |
| --- | --- | --- | --- | --- |
| FPMS_ENV | No | `dev` | `dev` | Environment name (e.g., dev/prod). |
| DATABASE_URL | No | `sqlite:///./fpms_dev.db` | `sqlite:///./fpms_dev.db` | SQLAlchemy database URL. |
| CORS_ORIGINS | No | `["http://localhost:5173"]` | `["http://localhost:5173"]` | Allowed CORS origins (JSON array string). |
| JWT_SECRET | No | `dev-secret-change-me` | `change-me-in-prod` | JWT signing secret (do NOT commit real secrets). |
| JWT_EXPIRE_MINUTES | No | `60` | `60` | JWT expiration time in minutes. |
| STORAGE_DIR | No | `./storage` | `./storage` | Local storage path for uploaded files. |

## Minimal dev .env example

```bash
FPMS_ENV=dev
DATABASE_URL=sqlite:///./fpms_dev.db
CORS_ORIGINS=["http://localhost:5173"]
JWT_SECRET=dev-secret-change-me
JWT_EXPIRE_MINUTES=60
STORAGE_DIR=./storage
```

## Troubleshooting
- DB URL format: ensure `DATABASE_URL` uses a valid SQLAlchemy URL (e.g., `sqlite:///./fpms_dev.db`).
- JWT secret missing/invalid: set `JWT_SECRET` to a non-empty value; re-login to refresh tokens.
- Storage path permissions: ensure `STORAGE_DIR` exists and is writable by the app process.
