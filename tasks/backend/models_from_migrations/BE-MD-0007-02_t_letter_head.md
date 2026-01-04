# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-MD-0007-02 — ORM model for `t_letter_head` (from Phase 0-EXT migrations)

## Purpose
Create ONE SQLAlchemy ORM model mapped to table `t_letter_head`, derived **exactly** from the Alembic migration created in Phase 0-EXT.

## Preconditions
1) The Alembic migration that creates `t_letter_head` exists under `backend/alembic/versions/` and has been applied (`alembic upgrade head` succeeds).
2) The project has a canonical SQLAlchemy Base and model-registration pattern. Follow it.

## Output
Create exactly ONE file:
- `backend/app/models/letter_head.py`

And register the model in the project’s model import aggregator (e.g., `backend/app/models/__init__.py` or `backend/app/db/base.py`).

## Steps
1) Open the migration that creates `t_letter_head` and treat it as authoritative.
2) Implement `LetterHead` with:
   - `__tablename__ = "t_letter_head"`
   - Columns, types, nullability, defaults, and FK behavior matching the migration exactly.
3) Do not add business logic or API code.
4) Ensure the model is imported/registered so `t_letter_head` appears in `Base.metadata.tables`.

## Verification
- `python -c "from backend.app.models import *; print('OK models import')"`

## Done Criteria
1) File exists: `backend/app/models/letter_head.py`
2) Import succeeds with no circular imports.
3) `t_letter_head` is present in `Base.metadata.tables`.
