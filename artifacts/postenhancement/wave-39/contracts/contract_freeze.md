# Wave 39 Contract Freeze

## Task
- Task ID: `PE-BE-QA-01`
- Task file: `tasks/postenhancement/backend/PE-BE-QA-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze error-envelope unification contract for one atomic backend task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/billing/api.py`
- In-scope behavior change:
  - replace naked `HTTPException(status_code=..., detail=...)` with `raise_business_error(...)` in allowlist files only.
- In-scope evidence outputs:
  - `artifacts/PE-BE-QA-01/**`
- Out of scope:
  - schema/model/migration changes
  - router wiring changes
  - success response payload changes
  - permission contract changes
  - edits outside allowlist files

## Error Envelope Unification Contract
- All business branches in allowlist currently raising `HTTPException(detail=...)` must raise `BusinessError` through:
  - `from app.core.errors import raise_business_error`
  - `raise_business_error(code=..., message=..., status_code=...)`
- Required envelope for these branches (via global handler):
  - `{"error": {"code": "<CANONICAL_CODE>", "message": "<existing detail intent>", "details": null|object}}`
- Status semantics must be preserved exactly as-is for each branch.
- User-facing message intent must be preserved (wording may be normalized only if intent is unchanged).
- FastAPI request validation remains unchanged:
  - `422` continues using global `VALIDATION_ERROR` envelope.

## Canonical Code Mapping (Frozen)
- Not-found (`404`) branches:
  - `"Case not found"` -> `CASE_NOT_FOUND`
  - `"Fee draft not found"` -> `FEE_DRAFT_NOT_FOUND`
  - `"Fee item not found"` -> `FEE_ITEM_NOT_FOUND`
  - `"Bill not found"` -> `BILL_NOT_FOUND`
  - `"Client not found"` -> `CLIENT_NOT_FOUND`
  - `"Payment not found"` -> `PAYMENT_NOT_FOUND`
  - `"Case receipt not found"` -> `CASE_RECEIPT_NOT_FOUND`
- Conflict (`409`) branches:
  - `"case_no already exists"` (create case conflict path) -> `CASE_NO_DUPLICATE`
  - `"Bill template not configured"` -> `BILL_TEMPLATE_NOT_CONFIGURED`
- Validation (`400`) branches:
  - `"case_no is required"` -> `CASE_INVALID`
  - `"case_no already exists"` (update case validation path currently `400`) -> `CASE_NO_DUPLICATE`
  - `"client_id is required"` -> `BILL_INVALID`
- Internal error branch currently present in allowlist:
  - `"Template file missing"` (`500`) -> `BILL_TEMPLATE_FILE_MISSING`

## Non-Regression Constraints
- Do not alter happy-path response schema/body for any endpoint in allowlist.
- Do not change endpoint URLs, methods, permission codes, or dependency injection pattern.
- Do not change branch HTTP status codes for existing error conditions.
- Do not convert framework-level `422` validation behavior to `400`.
- Keep doc-print behavior intact except for error raising path replacement.
- Keep imports minimal and lint-clean after replacing `HTTPException` usage.

## Acceptance Checklist
- [ ] Only allowlist product files were edited.
- [ ] Every allowlist `HTTPException(... detail=...)` business branch is replaced by `raise_business_error(...)`.
- [ ] Each replaced branch keeps the same HTTP status code as before.
- [ ] User-facing message intent remains equivalent to previous `detail` text.
- [ ] Canonical codes in this contract are used consistently in replaced branches.
- [ ] Error responses in affected branches now use global envelope (`error.code/error.message/error.details`).
- [ ] Existing success payload/envelope semantics are unchanged.
- [ ] Existing permission behavior is unchanged.
- [ ] Verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-QA-01/results.jsonl`
  - `artifacts/PE-BE-QA-01/summary.md`
  - `artifacts/PE-BE-QA-01/git/diff.patch`
