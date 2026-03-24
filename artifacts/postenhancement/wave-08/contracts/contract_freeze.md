# Wave 08 Contract Freeze

## Task
- Task ID: `PE-BE-DB-06`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-06.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend schema task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/alembic/versions/<new>_create_t_commission_rule.py`
  - `backend/app/modules/commission/models.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-DB-06/**`
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
- Field-contract risk:
  - missing or incorrect `CaseType`/`FeeType`/`S1`/`S2`/`WaitPay`/`ForceSettle` fields will fail acceptance intent.
- SQLite compatibility risk:
  - dialect-specific SQL/features can fail migration/runtime on SQLite.
- Scope risk:
  - non-allowlist edits increase regression surface and violate atomic rules.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-DB-06`.
- [ ] `T_CommissionRule` table is added per task definition.
- [ ] Schema supports required rule dimensions:
  - `CaseType`
  - `FeeType`
  - `S1`
  - `S2`
  - `WaitPay`
  - `ForceSettle`
- [ ] Migration succeeds on SQLite:
  - `cd backend && alembic upgrade head`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-DB-06/results.jsonl`
  - `artifacts/PE-BE-DB-06/summary.md`
  - `artifacts/PE-BE-DB-06/git/diff.patch`
