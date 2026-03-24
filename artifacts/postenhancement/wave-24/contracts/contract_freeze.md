# Wave 24 Contract Freeze

## Task
- Task ID: `PE-BE-COM-02`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-02.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/commission/api.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-02/**`
- Out of scope:
  - `backend/app/modules/commission/service.py` behavior edits (owned by service tasks)
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`GET /commission/rules`)
- Method/path:
  - `GET /commission/rules`
- Request body:
  - none (GET must not require request body)
- Query filters:
  - `enabled` (optional bool)
  - `case_type` (optional string)
  - `fee_type` (optional string)
  - `q` keyword search (optional string; safe for name/remark/key dimension matching)
- Safe optional filters (allowed):
  - `flow_dir` (optional string)
  - `patent_category` (optional string)
  - `wait_pay` (optional bool)
  - `force_settle` (optional bool)
  - effective window scope (`effective_on` date or from/to pair), if implementation chooses to expose
- Pagination:
  - `page` (int, `>=1`, default `1`)
  - `page_size` (int, `>=1`, default `20`)

## Permission Contract
- Required permission:
  - `CommissionRule.Read`
- Mandatory enforcement pattern:
  - `_perm: None = Depends(require_perm("CommissionRule.Read"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Response Envelope Contract
- Success status:
  - `200 OK`
- Response shape (mandatory list envelope):
  - `items`
  - `page`
  - `page_size`
  - `total`
- `items` entry expectation:
  - rule list-safe fields (id, rule_name, dimensions, rates/fixed amounts, enabled, effective range, flags).

## Error Semantics Expectations
- `422`:
  - query validation/type errors (FastAPI validation path; required).
- `400` (optional but allowed):
  - business-level invalid parameter combinations not covered by schema typing.
- Empty result behavior:
  - return `200` with `items=[]`, not `404`.
- Envelope rule:
  - preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Permission regression:
  - wrong permission code or injection pattern breaks access control.
- Envelope regression:
  - returning raw list without pagination metadata breaks frontend/API clients.
- Filter drift:
  - inconsistent `enabled/case_type/fee_type/q` semantics causes non-deterministic list behavior.
- Pagination drift:
  - unstable ordering can produce duplicate/missing items across pages.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted file:
  - `backend/app/modules/commission/api.py`
- [ ] `GET /commission/rules` supports required filters (`enabled`, `case_type`, `fee_type`, keyword `q`) and pagination (`page`, `page_size`).
- [ ] Permission enforced with parameter-injected `Depends(require_perm("CommissionRule.Read"))`.
- [ ] Success response envelope is exactly list+paging shape:
  - `items`, `page`, `page_size`, `total`
- [ ] Error semantics include `422` and optional business `400` for invalid parameter combos.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-02/results.jsonl`
  - `artifacts/PE-BE-COM-02/summary.md`
  - `artifacts/PE-BE-COM-02/git/diff.patch`
