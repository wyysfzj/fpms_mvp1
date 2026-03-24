# Wave 35 Contract Freeze

## Task
- Task ID: `PE-BE-CS-03`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-03.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CS-03/**`
- Out of scope:
  - schema/model/migration edits
  - router rewiring unrelated to first-time expenses module entry
  - unrelated module refactors

## Endpoint Contract (`GET /expenses`)
- Method/path:
  - `GET /expenses`
- Request body:
  - none
- Success status:
  - `200 OK`

## Query Filters Contract
- Required supported filters:
  - `case_id` (optional)
  - `category` (optional)
  - date range filter:
    - `date_from` (optional, based on `expense_date`)
    - `date_to` (optional, based on `expense_date`)
- Date-range semantics:
  - boundaries are inclusive.
  - open-ended range is allowed.
  - if both provided and `date_from > date_to`, return `400`.
- Safe optional filters:
  - `currency` (optional)
  - `status` (optional)
  - `q` keyword (optional, for expense_no/vendor_name/remark where applicable)

## Pagination + Envelope Contract
- Required pagination params:
  - `page` (int, `>=1`, default `1`)
  - `page_size` (int, `>=1`, default `20`)
- Required response envelope:
  - `items`
  - `page`
  - `page_size`
  - `total`
- `items` list entry (minimum list fields):
  - `id`
  - `expense_no`
  - `case_id`
  - `category`
  - `expense_date`
  - `amount`
  - `currency`
  - `status`
  - `remark`
  - `created_at`
  - `updated_at`
- Deterministic ordering:
  - stable default ordering (e.g. `expense_date desc`, then `id desc`) to keep pagination deterministic.

## Optional Stats Block Contract
- Query toggle:
  - `include_stats` (optional bool, default `false`)
- When `include_stats=false`:
  - response may omit `stats` or return `stats=null`.
- When `include_stats=true`:
  - response includes `stats` with category aggregates from the same filtered dataset (before pagination cut):
    - `count_by_category`
    - `sum_by_category`
    - optional top-level `count_total` and `sum_total` if implementation prefers explicit totals.
- Stats and list must be filter-consistent:
  - stats computed against the same filter scope used for `total`.

## Permission Contract
- Required permission:
  - `Expense.Read`
- Mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("Expense.Read"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Success / Error Semantics
- `200`:
  - valid list response, including empty `items=[]` when no match.
- `400`:
  - business validation failures (invalid range/filter combination).
- `422`:
  - query/type validation errors (FastAPI).
- `401` / `403`:
  - unauthenticated / permission denied.
- `404`:
  - not used for empty list queries; explicit case filter with no rows should still return `200` + empty list.
- Preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Filter regression:
  - missing case/category/date range support breaks expense search requirements.
- Paging regression:
  - unstable ordering causes duplicate/missing rows across pages.
- Stats regression:
  - stats computed on paged subset instead of filtered full set leads to incorrect totals.
- Permission regression:
  - wrong permission code or injection style bypasses access control.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
- [ ] `GET /expenses` endpoint implemented with required filters:
  - `case_id`, `category`, `date_from/date_to`
- [ ] Pagination envelope implemented:
  - `items`, `page`, `page_size`, `total`
- [ ] Optional stats block supported for count/sum by category.
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("Expense.Read"))`
- [ ] Success/error semantics align with frozen contract (`200/400/422`, auth `401/403`).
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CS-03/results.jsonl`
  - `artifacts/PE-BE-CS-03/summary.md`
  - `artifacts/PE-BE-CS-03/git/diff.patch`
