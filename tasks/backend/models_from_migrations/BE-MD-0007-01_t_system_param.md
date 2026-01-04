# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-MD-0007-01 — ORM model for `t_system_param` (from Phase 0-EXT migrations)

## Purpose
Create ONE SQLAlchemy ORM model mapped to table `t_system_param`, derived **exactly** from the Alembic migration created in Phase 0-EXT.

## Preconditions
1) The Alembic migration that creates `t_system_param` exists under `backend/alembic/versions/` and has been applied (`alembic upgrade head` succeeds).
2) The project has a canonical SQLAlchemy Base and model-registration pattern. Follow it.

## Output
Create exactly ONE file:
- `backend/app/models/system_param.py`

And register the model in the project’s model import aggregator (e.g., `backend/app/models/__init__.py` or `backend/app/db/base.py`).

## Steps
1) Open the migration that creates `t_system_param` and treat it as authoritative.
2) Implement `SystemParam` with:
   - `__tablename__ = "t_system_param"`
   - Columns, types, nullability, defaults, and FK behavior matching the migration exactly.
3) Do not add business logic or API code.
4) Ensure the model is imported/registered so `t_system_param` appears in `Base.metadata.tables`.

## Verification
- `python -c "from backend.app.models import *; print('OK models import')"`

## Done Criteria
1) File exists: `backend/app/models/system_param.py`
2) Import succeeds with no circular imports.
3) `t_system_param` is present in `Base.metadata.tables`.
