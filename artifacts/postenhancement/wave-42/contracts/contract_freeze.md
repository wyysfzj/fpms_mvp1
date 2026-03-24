# Wave 42 Contract Freeze

## Task
- Task ID: `PE-BE-TEST-01`
- Task file: `tasks/postenhancement/backend/PE-BE-TEST-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze critical E2E test contract for annuity/collections/commission/consulting modules.

## Allowlist Boundaries
- In-scope test files only:
  - `backend/tests/test_annuity_e2e.py`
  - `backend/tests/test_collections_e2e.py`
  - `backend/tests/test_commission_e2e.py`
  - `backend/tests/test_consulting_e2e.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-TEST-01/**`
- Out of scope:
  - product code edits (`backend/app/**`)
  - test infrastructure edits outside allowlist (`backend/tests/conftest.py`, other test files)
  - schema/migration changes

## E2E Critical Paths (Mandatory)

### Annuity (`test_annuity_e2e.py`)
- Path A1: task list + filters + pagination
  1. `GET /annuity/tasks` with valid filters.
  2. Assert list envelope (`items/page/page_size/total`) and filter coherence.
- Path A2: instruction transition
  1. `PUT /annuity/tasks/{task_id}/instruction` valid transition.
  2. Assert updated `client_instruction`, `instruction_date`, `status` unchanged except allowed transitions.
- Path A3: draft generation + optional next-year branch
  1. `POST /annuity/tasks/generate-drafts` with `task_ids`, with/without `pay_next_year`.
  2. Assert `summary/success/failed` structure and duplicate behavior on repeated call.
- Path A4: pay-list + gov payment chain
  1. `POST /pay-lists/from-fee-items`.
  2. `POST /gov-payments`.
  3. Assert pay-list status recompute semantics (`DRAFT/PARTIAL/PAID`) and duplicate protection.

### Collections (`test_collections_e2e.py`)
- Path C1: dunning generation + idempotency/strict conflict
  1. `POST /dunning` (valid scope).
  2. Repeat same request with `strict_conflict=false` (expect reuse/idempotent semantics).
  3. Repeat with `strict_conflict=true` (expect conflict semantics).
  4. Assert `summary + batches` payload integrity.
- Path C2: dunning list filters
  1. `GET /dunning` using `round_no/status/client_id/page/page_size`.
  2. Assert pagination envelope and filter consistency.
- Path C3: bad-debt lifecycle
  1. `POST /bills/{bill_id}/bad-debt`.
  2. `POST /bills/{bill_id}/bad-debt/restore`.
  3. Assert deterministic restore status mapping from `amount/balance`.

### Commission (`test_commission_e2e.py`)
- Path M1: rule lifecycle
  1. `POST /commission/rules`.
  2. `GET /commission/rules` with filters/pagination.
  3. `PUT /commission/rules/{rule_id}`.
  4. Assert created/updated fields and conflict validation behavior.
- Path M2: settlement lifecycle
  1. `POST /commission/settlements`.
  2. `POST /commission/settlements/{id}/generate-lines` (repeat to verify idempotent update behavior).
  3. Assert line/totals/status transitions and duplicate-line protection semantics.
- Path M3: read/report endpoints
  1. `GET /commission` with required filters and date-range params.
  2. `GET /commission/reports/settlement`.
  3. Assert envelope shape (`items/page/page_size/total` or report aggregate schema) and range validation behavior.

### Consulting (`test_consulting_e2e.py`)
- Path S1: consulting/search case creation
  1. `POST /consulting/cases` for `CONSULTING` and/or `SEARCH`.
  2. Assert required fields persisted and `status` initialized per contract.
- Path S2: fee-draft modes
  1. `POST /consulting/fee-drafts` for `FIXED`.
  2. `POST /consulting/fee-drafts` for `HOURLY` or `HYBRID`.
  3. Assert deterministic totals and line-level traceability fields.
- Path S3: conflict/error branches
  1. Re-submit same open-draft scope to trigger conflict.
  2. Assert conflict/error envelope semantics for invalid mode/input and missing case.

## Minimum Assertions and Status-Code Coverage

### Global Minimum Assertions (all four files)
- Every success path must assert:
  - HTTP status code
  - critical response keys (not only status)
  - at least one business invariant relevant to the flow
- Every error path must assert:
  - HTTP status code
  - error envelope structure: `error.code`, `error.message`
  - stable domain error code when contract defines one

### Minimum Status Coverage by Module
- Annuity:
  - success: `200`
  - error: `400`, `404`, `409`, `422` (where schema/range invalidity applies)
- Collections:
  - success: `200`
  - error: `400`, `404`, `409`, `422`
- Commission:
  - success: `200`, `201`
  - error: `400`, `404`, `409`, `422`
- Consulting:
  - success: `201`
  - error: `400`, `404`, `409`, `422`

## Fixture and Data-Isolation Expectations
- Use existing shared fixtures only:
  - `client`
  - `auth_headers`
  - `session_factory` only when DB-state assertion is necessary.
- Test data must be isolated by unique IDs/names per test (`uuid`-based helper), because test DB is session-scoped.
- Do not rely on absolute row counts from global DB state; assert by IDs created in-test.
- Do not rely on inter-test ordering; each test must be independently runnable.
- Avoid mutating seed records except read-only lookup (admin user, seeded templates).
- For idempotency checks, perform repeated calls inside the same test and assert deterministic behavior.

## Non-Regression Constraints
- New tests must not require changing API contracts or app wiring.
- Tests should validate existing frozen contracts, not redefine endpoint semantics.
- Keep runtime stable:
  - avoid flaky timing-based assertions
  - use deterministic dates/inputs where possible.
- Keep assertion granularity focused on critical contract points, not fragile implementation internals.

## Acceptance Checklist
- [ ] Only allowlisted test files are edited:
  - `backend/tests/test_annuity_e2e.py`
  - `backend/tests/test_collections_e2e.py`
  - `backend/tests/test_commission_e2e.py`
  - `backend/tests/test_consulting_e2e.py`
- [ ] Each file covers at least one full critical path for its module.
- [ ] Minimum status coverage matrix (`200/201` + required `400/404/409/422`) is satisfied across the suite.
- [ ] Assertions include envelope/status + key business invariants (not status-only checks).
- [ ] Idempotency/duplicate-protection assertions are present where contracted (dunning, annuity draft/pay flows, settlement lines).
- [ ] Fixture/data isolation expectations are followed (unique data, no order dependency).
- [ ] Verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-TEST-01/results.jsonl`
  - `artifacts/PE-BE-TEST-01/summary.md`
  - `artifacts/PE-BE-TEST-01/git/diff.patch`
