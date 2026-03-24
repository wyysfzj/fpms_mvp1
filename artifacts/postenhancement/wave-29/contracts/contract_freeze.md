# Wave 29 Contract Freeze

## Task
- Task ID: `PE-BE-COM-07`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-07.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/commission/api.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-07/**`
- Out of scope:
  - `backend/app/modules/commission/service.py` behavior edits
  - router wiring
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`GET /commission`)
- Method/path:
  - `GET /commission`
- Request body:
  - none (GET must not require a body)
- Success status:
  - `200 OK`

## Query Filters (Mandatory + Safe Optional)
- Mandatory supported filters:
  - `agent_id` (optional string)
  - `case_id` (optional string)
  - `status` (optional string; commission row status)
  - date range filter (at least one complete range mode):
    - `settleable_date_from` + `settleable_date_to`, or
    - `created_at_from` + `created_at_to`
- Safe optional filters:
  - `is_settleable` (optional bool)
  - `fee_type` (optional string)
  - `rule_id` (optional int)
- Pagination:
  - `page` (int, `>=1`, default `1`)
  - `page_size` (int, `>=1`, default `20`)

## Permission Contract
- Required permission:
  - `Commission.Read`
- Mandatory enforcement pattern:
  - `_perm: None = Depends(require_perm("Commission.Read"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Response Envelope Contract
- Response shape (mandatory):
  - `items`
  - `page`
  - `page_size`
  - `total`
- `items` entry fields and semantics:
  - `id`: commission row id
  - `case_id`: linked case id
  - `agent_id`: responsible agent id (nullable)
  - `rule_id`: matched commission rule id (nullable)
  - `fee_type`: commission fee type context (for this phase normally `SERVICE`)
  - `base_fee`: commission base amount snapshot
  - `s1_rate`, `s1_amount`, `s1_done`: stage-1 commission ratio/amount/settled-flag
  - `s2_rate`, `s2_amount`, `s2_done`: stage-2 commission ratio/amount/settled-flag
  - `wait_pay`, `force_settle`: settleability policy flags
  - `status`: commission lifecycle status string
  - `is_settleable`: current settleability flag used by settlement flow
  - `settleable_date`: date when row became settleable (nullable)
  - `remark`: optional note
  - `created_at`, `updated_at`: audit timestamps

## Filter and Semantics Rules
- Date range semantics:
  - range boundaries are inclusive.
  - if both start/end provided and start > end, return business validation `400`.
- Empty result behavior:
  - return `200` with `items=[]` and valid paging metadata; do not return `404`.
- Ordering determinism:
  - apply stable default ordering (e.g. `created_at desc, id desc`) to keep pagination deterministic.

## Error Semantics
- `422`:
  - FastAPI query/type validation failures.
- `400`:
  - business-level invalid filter combinations/range violations.
- `401` / `403`:
  - unauthenticated / permission denied via existing auth stack.
- Preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Permission regression:
  - wrong permission code or wrong injection style breaks access control.
- Filter regression:
  - missing required `agent_id/case_id/status/date-range` support breaks search scenarios.
- Envelope regression:
  - returning raw list without `items,page,page_size,total` breaks client contract.
- Pagination regression:
  - unstable ordering causes duplicate/missing rows between pages.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted file:
  - `backend/app/modules/commission/api.py`
- [ ] `GET /commission` implemented with required filters:
  - `agent_id`, `case_id`, `status`, date range (settleable or created range).
- [ ] Pagination implemented with `page` and `page_size`.
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("Commission.Read"))`
- [ ] Success envelope is exactly:
  - `items`, `page`, `page_size`, `total`
- [ ] Response item fields align with commission list semantics.
- [ ] Error behavior includes `422` validation and `400` business range/filter errors.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-07/results.jsonl`
  - `artifacts/PE-BE-COM-07/summary.md`
  - `artifacts/PE-BE-COM-07/git/diff.patch`
