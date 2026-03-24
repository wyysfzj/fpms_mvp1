# PE-BE-CS-02 Evidence Summary

## Task
- Task ID: `PE-BE-CS-02`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-02.md`
- Scope (allowlist):
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`

## Implemented
1. Added endpoint `POST /expenses` in expenses API.
2. Added permission injection exactly:
   - `_perm: None = Depends(require_perm("Expense.Create"))`
3. Implemented create service with required validation:
   - `case_id` required, trimmed, and must exist (`404 CASE_NOT_FOUND`)
   - `category` required, trimmed, uppercase, and restricted to:
     - `SEARCH_DB`, `TRANSLATION`, `TRANSPORT`, `OTHER`
   - `expense_date` required
   - `amount` required and `> 0`
   - optional `tax_amount` must be `>= 0` when provided
4. Implemented default/normalization behavior:
   - `status` initialized to `DRAFT`
   - `currency` normalized uppercase with default `CNY`
   - optional strings trimmed
5. Implemented deterministic `expense_no` generation after `flush()`:
   - `EXP-YYYYMMDD-<id(6 digits)>` when not provided.
6. Endpoint returns `201` with key fields including:
   - `id, expense_no, case_id, category, expense_date, amount, currency, status, remark, created_at, updated_at`

## Verification
- `./scripts/evidence_run.sh PE-BE-CS-02 lint bash -lc 'cd backend && ruff check app/modules/expenses/api.py app/modules/expenses/service.py && ruff format --check app/modules/expenses/api.py app/modules/expenses/service.py'`
  - `rc=0`
- `./scripts/evidence_run.sh PE-BE-CS-02 test bash -lc 'cd backend && pytest -q'`
  - `rc=0` (`141 passed, 3 warnings`)

## Status Semantics
- `201`: expense created.
- `400`: business validation failure (`category`, required fields, `amount <= 0`, invalid `tax_amount`).
- `404`: referenced `case_id` not found.
- `401/403`: auth/permission denied by existing deps.
- `422`: request schema/type validation failure.

## Evidence Files
- `artifacts/PE-BE-CS-02/results.jsonl`
- `artifacts/PE-BE-CS-02/summary.md`
- `artifacts/PE-BE-CS-02/git/diff.patch`
