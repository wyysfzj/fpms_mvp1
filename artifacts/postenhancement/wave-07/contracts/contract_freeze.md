# Wave 07 Contract Freeze

## Task
- Task ID: `PE-BE-DB-05`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-05.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend schema task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/alembic/versions/<new>_create_t_dunning.py`
  - `backend/app/modules/collections/models.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-DB-05/**`
- Out of scope:
  - Any product files outside allowlist.
  - Router/API/service/test edits not explicitly required by this schema task.
  - Unrelated migration/model refactors.

## Schema/Migration Constraints (SQLite)
- SQLite compatibility is mandatory (MVP1 PoC baseline).
- Use SQLite-safe defaults and SQL:
  - use `server_default=sa.text("CURRENT_TIMESTAMP")` for timestamp defaults where needed.
  - avoid PG-only constructs (`uuid_generate_v4()`, `gen_random_uuid()`, `ILIKE`, `JSONB`, `ARRAY`, `CITEXT`, `date_trunc(...)`, `timezone(...)`, `interval`).
- PK/FK typing must remain aligned and SQLite-safe:
  - prefer `Integer` PK autoincrement conventions where applicable.
  - keep FK column types consistent with referenced PK types.
- Do not rely on `RETURNING` behavior for correctness.
- Keep migration forward-only compatible with repository policy.

## Regression Risks
- Migration sequencing risk:
  - incorrect revision linkage can break `alembic upgrade head`.
- Relational integrity risk:
  - `T_DunningLine` must correctly reference `T_Dunning` and related bill entities; type/table mismatches can fail migration or runtime inserts.
- Snapshot semantics risk:
  - missing or weak bill snapshot fields can break “账单快照” acceptance intent.
- Scope risk:
  - changes beyond allowlist increase regression surface and violate atomic task rules.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-DB-05`.
- [ ] `T_Dunning` and `T_DunningLine` are both added per task definition.
- [ ] Schema supports required business intent:
  - multi-round dunning records
  - bill snapshot fields in line items
- [ ] Migration succeeds on SQLite:
  - `cd backend && alembic upgrade head`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-DB-05/results.jsonl`
  - `artifacts/PE-BE-DB-05/summary.md`
  - `artifacts/PE-BE-DB-05/git/diff.patch`
