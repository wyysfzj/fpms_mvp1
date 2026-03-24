# Wave 11 Contract Freeze

## Task
- Task ID: `PE-BE-AN-01`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/annuity/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-AN-01/**`
- Out of scope:
  - Any files other than `backend/app/modules/annuity/service.py`.
  - API router/schema/model/migration changes.
  - Cross-module refactors unrelated to annuity task extraction.

## Service Contract Assumptions
- Service provides annuity task retrieval by due-date range and status filters.
- Service returns a paginated result compatible with existing module pagination conventions.
- Service must support pending-task filtering (`待处理`) as a first-class filter mode.
- Filtering semantics are deterministic:
  - same inputs must produce stable ordering and page slicing.
- No request/response envelope invention in service output; reuse module patterns consumed by existing API layer.

## SQLite/Platform Constraints
- No schema or migration edits are allowed in this task.
- Query logic must remain SQLite-safe:
  - no PostgreSQL-only operators/functions in ORM/raw SQL.
  - avoid assumptions that depend on `RETURNING` or dialect-only behavior.
- Keep transaction scope short and read-focused for PoC SQLite lock tolerance.

## Regression Risks
- Filter semantics risk:
  - due-range boundary handling (inclusive/exclusive) can cause off-by-one result regressions.
- Status mapping risk:
  - pending status interpretation may drift from business rules and return wrong task sets.
- Pagination determinism risk:
  - missing explicit ordering can produce unstable page results.
- Scope risk:
  - touching files outside allowlist violates atomic policy and increases regression surface.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product file for `PE-BE-AN-01`.
- [ ] Service supports due-date range filtering.
- [ ] Service supports status-based filtering, including pending-task mode.
- [ ] Service returns paginated task list with deterministic ordering.
- [ ] Targeted verification passes:
  - `cd backend && pytest -q tests/test_b6_search_filters.py`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-AN-01/results.jsonl`
  - `artifacts/PE-BE-AN-01/summary.md`
  - `artifacts/PE-BE-AN-01/git/diff.patch`
