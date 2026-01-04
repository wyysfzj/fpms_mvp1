# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-MD-0006-02 — ORM model for `t_client_contact` (from Phase 0-EXT migrations)

## Purpose
Create ONE SQLAlchemy ORM model mapped to table `t_client_contact`, derived **exactly** from the Alembic migration created in Phase 0-EXT.

## Preconditions
1) The Alembic migration that creates `t_client_contact` exists under `backend/alembic/versions/` and has been applied (`alembic upgrade head` succeeds).
2) The project has a canonical SQLAlchemy Base and model-registration pattern. Follow it.

## Output
Create exactly ONE file:
- `backend/app/models/client_contact.py`

And register the model in the project’s model import aggregator (e.g., `backend/app/models/__init__.py` or `backend/app/db/base.py`).

## Steps
1) Open the migration that creates `t_client_contact` and treat it as authoritative.
2) Implement `ClientContact` with:
   - `__tablename__ = "t_client_contact"`
   - Columns, types, nullability, defaults, and FK behavior matching the migration exactly.
3) Do not add business logic or API code.
4) Ensure the model is imported/registered so `t_client_contact` appears in `Base.metadata.tables`.

## Verification
- `python -c "from backend.app.models import *; print('OK models import')"`

## Done Criteria
1) File exists: `backend/app/models/client_contact.py`
2) Import succeeds with no circular imports.
3) `t_client_contact` is present in `Base.metadata.tables`.
