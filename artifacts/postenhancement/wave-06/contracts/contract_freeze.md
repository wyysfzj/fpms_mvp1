# Wave 06 Contract Freeze

## Task
- Task ID: `PE-BE-DB-04`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-04.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend schema task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/alembic/versions/<new>_create_t_annuity_task.py`
  - `backend/app/modules/annuity/models.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-DB-04/**`
- Out of scope:
  - Any product files outside the allowlist.
  - Router/API/service/test changes not explicitly required by this schema task.
  - Unrelated migration/model refactors.

## Schema/Migration Constraints (SQLite)
- SQLite compatibility is mandatory (MVP1 PoC baseline).
- Use SQLite-safe SQL/defaults:
  - use `server_default=sa.text("CURRENT_TIMESTAMP")` for timestamp defaults where needed.
  - do not use PG-only constructs (`uuid_generate_v4()`, `gen_random_uuid()`, `ILIKE`, `JSONB`, `ARRAY`, `CITEXT`, `date_trunc(...)`, `timezone(...)`, `interval`).
- PK/FK typing must be aligned and SQLite-safe:
  - prefer `Integer` PK autoincrement conventions where applicable.
  - keep FK column types consistent with referenced PK types.
- Do not rely on `RETURNING` behavior for correctness.
- Migration must remain forward-only compatible with repository policy.

## Regression Risks
- Migration chain risk:
  - incorrect revision linkage/order may break `alembic upgrade head`.
- Field contract risk:
  - missing or incorrect annual/deadline/client-instruction/notification-status fields can fail acceptance.
- SQLite dialect risk:
  - non-SQLite SQL/features may pass static review but fail in runtime migration.
- Scope risk:
  - edits beyond allowlist can introduce unrelated regressions and violate atomic discipline.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-DB-04`.
- [ ] `T_AnnuityTask` table is added per task definition.
- [ ] Schema supports required fields:
  - annual/year field
  - deadline/date field
  - client instruction field
  - notification status field
- [ ] Migration succeeds on SQLite:
  - `cd backend && alembic upgrade head`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-DB-04/results.jsonl`
  - `artifacts/PE-BE-DB-04/summary.md`
  - `artifacts/PE-BE-DB-04/git/diff.patch`
