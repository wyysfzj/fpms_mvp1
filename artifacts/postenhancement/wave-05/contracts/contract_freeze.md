# Wave 05 Contract Freeze

## Task
- Task ID: `PE-BE-DB-03`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-03.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend schema task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/alembic/versions/<new>_create_t_gov_payment.py`
  - `backend/app/modules/annuity/models.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-DB-03/**`
- Out of scope:
  - Any non-allowlisted product files.
  - Router/API/service/test edits not explicitly required by this schema task.
  - Unrelated migrations/model refactors.

## Schema/Migration Constraints (SQLite)
- SQLite compatibility is mandatory (MVP1 PoC baseline).
- Migration SQL and defaults must be SQLite-safe:
  - use `server_default=sa.text("CURRENT_TIMESTAMP")` for timestamp defaults as needed.
  - avoid PG-only constructs (`uuid_generate_v4()`, `gen_random_uuid()`, `ILIKE`, `JSONB`, `ARRAY`, `CITEXT`, `date_trunc(...)`, `timezone(...)`, `interval`).
- PK/FK type alignment is required:
  - FK columns to `T_PayList`, Case, and FeeItem must match referenced PK types.
  - prefer `Integer` PK autoincrement patterns where applicable.
- Do not rely on `RETURNING` semantics for correctness.
- Keep migration forward-only compatible with repository migration policy.

## Regression Risks
- Dependency chain risk:
  - incorrect `down_revision` can break migration sequencing from `PE-BE-DB-02`.
- Referential integrity risk:
  - FK definitions to `T_PayList`/Case/FeeItem can fail if table names, column names, or types are mismatched.
- SQLite compatibility risk:
  - dialect-specific SQL may pass review but fail at runtime on SQLite.
- Scope compliance risk:
  - extra edits outside allowlist increase regression surface and violate atomic rules.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-DB-03`.
- [ ] `T_GovPayment` table is added per task definition.
- [ ] Foreign keys are correctly defined to:
  - `T_PayList`
  - Case
  - FeeItem
- [ ] Migration succeeds on SQLite:
  - `cd backend && alembic upgrade head`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-DB-03/results.jsonl`
  - `artifacts/PE-BE-DB-03/summary.md`
  - `artifacts/PE-BE-DB-03/git/diff.patch`
