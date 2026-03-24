# Wave 10 Contract Freeze

## Task
- Task ID: `PE-BE-DB-08`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-08.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend schema task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/alembic/versions/<new>_create_t_commission_settlement.py`
  - `backend/app/modules/commission/models.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-DB-08/**`
- Out of scope:
  - Any product files outside allowlist.
  - Router/API/service/test edits not explicitly required by this schema task.
  - Unrelated migration/model refactors.

## Schema/Migration Constraints (SQLite)
- SQLite compatibility is mandatory (MVP1 PoC baseline).
- Use SQLite-safe SQL/defaults only:
  - use `server_default=sa.text("CURRENT_TIMESTAMP")` for timestamp defaults where needed.
  - avoid PG-only constructs (`uuid_generate_v4()`, `gen_random_uuid()`, `ILIKE`, `JSONB`, `ARRAY`, `CITEXT`, `date_trunc(...)`, `timezone(...)`, `interval`).
- PK/FK typing must remain aligned and SQLite-safe:
  - prefer `Integer` PK autoincrement conventions where applicable.
  - keep FK column types consistent with referenced PK types.
- Do not rely on `RETURNING` behavior for correctness.
- Keep migration forward-only compatible with repository policy.

## Regression Risks
- Migration chain risk:
  - incorrect revision linkage can break `alembic upgrade head`.
- Relational integrity risk:
  - settlement line linkage to settlement batch and commission records can fail if FK types/tables are mismatched.
- Data-contract risk:
  - missing batch-level or line-level fields can block required batch-detail association behavior.
- Scope risk:
  - edits outside allowlist can introduce unrelated regressions and violate atomic rules.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-DB-08`.
- [ ] `T_CommissionSettlement` and `T_CommissionSettleLine` tables are both added per task definition.
- [ ] Schema supports required settlement behavior:
  - settlement batch header
  - settlement detail line association
- [ ] Migration succeeds on SQLite:
  - `cd backend && alembic upgrade head`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-DB-08/results.jsonl`
  - `artifacts/PE-BE-DB-08/summary.md`
  - `artifacts/PE-BE-DB-08/git/diff.patch`
