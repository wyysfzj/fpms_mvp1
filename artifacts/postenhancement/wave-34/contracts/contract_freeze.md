# Wave 34 Contract Freeze

## Task
- Task ID: `PE-BE-CS-02`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-02.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CS-02/**`
- Out of scope:
  - schema/model/migration edits
  - router rewiring unrelated to first-time expenses module entry
  - unrelated module refactors

## Endpoint Contract (`POST /expenses`)
- Method/path:
  - `POST /expenses`
- Success status:
  - `201 Created`
- Success payload semantics (minimum):
  - `id`
  - `case_id`
  - `category`
  - `expense_date`
  - `amount`
  - `currency`
  - `status`
  - `remark`
  - `created_at`
  - `updated_at`

## Request Fields and Required Validation
- Required request fields:
  - `case_id` (required, non-empty)
  - `category` (required, non-empty)
  - `expense_date` (required date)
  - `amount` (required decimal)
- Optional request fields:
  - `client_id`
  - `expense_no`
  - `vendor_name`
  - `currency` (default allowed if omitted)
  - `tax_amount`
  - `remark`
- Required validation rules:
  - `case_id` must reference an existing case (`404` when not found).
  - `category` must be one of:
    - `SEARCH_DB`
    - `TRANSLATION`
    - `TRANSPORT`
    - `OTHER`
  - `expense_date` must be a valid date (and not an invalid future business date if business policy enforces cut-off).
  - `amount` must be numeric and `>= 0` (strictly positive can be chosen if product policy requires).
  - if provided, `tax_amount` must be `>= 0`.
  - normalize string fields (trim whitespace) before business validation.

## Permission Contract
- Required permission:
  - `Expense.Create`
- Mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("Expense.Create"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Success / Error Semantics
- `201`:
  - expense record created with canonical response payload.
- `400`:
  - business validation failures (`category`, `expense_date`, `amount`, required fields).
- `404`:
  - referenced `case_id` not found.
- `409` (as applicable):
  - duplicate conflict for business-unique expense identity if enforced (for example duplicate `expense_no` in same scope).
- `422`:
  - request schema/type validation failures.
- `401` / `403`:
  - unauthenticated / permission denied.
- Preserve existing BusinessError/FastAPI envelope conventions.

## Response Shape Contract
- Response is a single created expense resource object (not wrapped list envelope).
- Field semantics:
  - `status` initializes to `DRAFT` unless task implementation explicitly contracts another initial state.
  - `amount` and `tax_amount` returned as normalized decimals.
  - `currency` returned as normalized code (e.g. uppercase).

## Regression Risks
- Validation regression:
  - weak case/category/date/amount checks allow invalid expense records.
- Permission regression:
  - wrong permission code or injection style bypasses protection.
- Conflict regression:
  - missing duplicate handling causes repeated inserts in idempotent/unique contexts.
- Contract regression:
  - returning wrong status code/body shape breaks consumers.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
- [ ] `POST /expenses` endpoint implemented.
- [ ] Request validation enforces `case/category/date/amount` rules.
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("Expense.Create"))`
- [ ] Success returns `201` with created expense payload.
- [ ] Error semantics align with `400/404/409` (and `422` for schema validation).
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CS-02/results.jsonl`
  - `artifacts/PE-BE-CS-02/summary.md`
  - `artifacts/PE-BE-CS-02/git/diff.patch`
