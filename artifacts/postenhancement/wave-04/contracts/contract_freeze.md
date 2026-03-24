# Wave 04 Contract Freeze

## Task
- Task ID: `PE-BE-DB-02`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-02.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend schema task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/alembic/versions/<new>_create_t_pay_list.py`
  - `backend/app/modules/annuity/models.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-DB-02/**`
- Out of scope:
  - Any non-allowlisted product files.
  - Router/API/service/test edits not explicitly required by this schema task.
  - Unrelated migration or model refactors.

## Schema/Migration Constraints (SQLite)
- SQLite compatibility is mandatory (MVP1 PoC baseline).
- Use SQLite-safe defaults and SQL only:
  - timestamp defaults must use `server_default=sa.text("CURRENT_TIMESTAMP")`.
  - do not use PG-only functions/types (for example `uuid_generate_v4()`, `gen_random_uuid()`, `ILIKE`, `JSONB`, `ARRAY`, `CITEXT`, `date_trunc(...)`, `timezone(...)`, `interval`).
- PK/FK typing must remain SQLite-safe and aligned:
  - prefer `Integer` PK for autoincrement behavior where applicable.
  - keep FK types compatible with referenced PK types.
- Migration must be forward-only compatible with repository policy.
- Do not rely on `RETURNING` for correctness.

## Regression Risks
- Migration chain risk:
  - wrong `down_revision` or ordering can break `alembic upgrade head`.
- Schema compatibility risk:
  - incorrect field types/defaults can violate SQLite constraints.
- Model coherence risk:
  - mismatch between `T_PayList` migration columns and ORM model fields can cause runtime failures.
- Scope compliance risk:
  - edits outside allowlist can introduce unrelated regressions and violate atomic execution.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-DB-02`.
- [ ] `T_PayList` table is added with required fields:
  - status
  - currency
  - date fields
  - creation audit fields
- [ ] Migration succeeds on SQLite:
  - `cd backend && alembic upgrade head`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-DB-02/results.jsonl`
  - `artifacts/PE-BE-DB-02/summary.md`
  - `artifacts/PE-BE-DB-02/git/diff.patch`
