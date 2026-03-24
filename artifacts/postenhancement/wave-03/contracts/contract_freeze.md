# Wave 03 Contract Freeze

## Task
- Task ID: `PE-BE-DB-01`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for backend executor; no product code changes in this step.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/alembic/versions/<new>_create_t_expense.py`
  - `backend/app/modules/expenses/models.py`
- In-scope non-product evidence/artifacts:
  - `artifacts/PE-BE-DB-01/**` (results, summary, diff during implementation/test phases)
- Out of scope:
  - Any other migration/model/router/service/API/test files not explicitly listed above.
  - Any schema edits unrelated to `T_Expense`.

## Schema/Migration Constraints (SQLite)
- SQLite compatibility is mandatory for MVP1.
- Migration must avoid PostgreSQL-only SQL/functions/types:
  - no `uuid_generate_v4()`, `gen_random_uuid()`, `ILIKE`, `JSONB`, `ARRAY`, `CITEXT`, `date_trunc(...)`, `timezone(...)`, `interval`.
- Timestamp defaults must use SQLite-safe expression:
  - `server_default=sa.text("CURRENT_TIMESTAMP")` (not `now()`).
- Primary key strategy must be SQLite-safe:
  - prefer `Integer` PK for autoincrement behavior.
  - keep PK/FK types aligned.
- Do not rely on `RETURNING` semantics for correctness; use ORM/session flush behavior as needed.
- Keep migration forward-only compatible with repository policy.

## Regression Risks
- Migration ordering/conflict risk:
  - new revision must chain correctly from current head and not break existing upgrade path.
- Type mismatch risk:
  - introducing non-aligned PK/FK types can break inserts/relations on SQLite.
- Import-path risk:
  - `app/modules/expenses/models.py` must remain importable (`py_compile` gate).
- Scope creep risk:
  - touching unrelated migrations or modules can introduce unintended regressions and violate atomic policy.

## Acceptance Checklist
- [ ] Implementation touches only allowlist product files for `PE-BE-DB-01`.
- [ ] `T_Expense` schema/model is created per task definition.
- [ ] SQLite migration succeeds:
  - `cd backend && alembic upgrade head`
- [ ] Model compiles/imports:
  - `cd backend && python3 -m py_compile app/modules/expenses/models.py`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts generated for task completion claim:
  - `artifacts/PE-BE-DB-01/results.jsonl`
  - `artifacts/PE-BE-DB-01/summary.md`
  - `artifacts/PE-BE-DB-01/git/diff.patch`
