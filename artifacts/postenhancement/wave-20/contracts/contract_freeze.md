# Wave 20 Contract Freeze

## Task
- Task ID: `PE-BE-CL-03`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-03.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/collections/api.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CL-03/**`
- Out of scope:
  - `backend/app/modules/collections/service.py` behavior changes (owned by earlier collections service task)
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`GET /dunning`)
- Method/path:
  - `GET /dunning`
- Request body:
  - none (GET must not require body)
- Query filters (required by task):
  - `round_no` (optional, int)
  - `status` (optional, string)
  - `client_id` (optional, string)
- Safe optional filters (allowed):
  - `currency` (optional, string)
  - `to_date_from` / `to_date_to` (optional, date range)
- Pagination:
  - `page` (int, `>=1`, default `1`)
  - `page_size` (int, `>=1`, default `20`)

## Permission Contract
- Required permission:
  - `Dunning.Read`
- Mandatory enforcement pattern:
  - `_perm: None = Depends(require_perm("Dunning.Read"))`
- Do not use decorator-level `dependencies=[...]` for permission.

## Response Envelope Shape (List + Pagination)
- Success status:
  - `200 OK`
- Envelope contract:
  - top-level list response with pagination metadata:
    - `items` (list of dunning batch list records)
    - `page`
    - `page_size`
    - `total`
- Item shape should include at minimum list-facing fields:
  - batch identifier / dunning number
  - client identifier
  - round number
  - status
  - cutoff date
  - currency
  - total amount

## Error Semantics Mapping Expectations
- `400`:
  - business/query validation failures (invalid filter values or incompatible filter combinations).
- `404`:
  - explicit scoped lookup not found (for example strict client scope behavior, if used by implementation).
  - default empty list queries should prefer `200` with `items=[]`.
- `422`:
  - FastAPI query/schema validation failures (type/format constraints).
- Envelope constraints:
  - preserve existing BusinessError/FastAPI envelope conventions; do not invent new error shape.

## Regression Risks
- Permission regression:
  - wrong permission code or incorrect dependency injection style can break authorization.
- Envelope regression:
  - returning raw DB payload without `items/page/page_size/total` breaks frontend/client contract.
- Pagination drift:
  - unstable ordering can cause non-deterministic page results.
- Filter semantics drift:
  - incorrect round/status/client filter handling can silently under/over-return batches.
- Scope risk:
  - API task modifying non-allowlist files violates atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted file `backend/app/modules/collections/api.py`.
- [ ] `GET /dunning` supports `round_no`, `status`, `client_id` filters.
- [ ] Pagination parameters `page/page_size` are supported with deterministic ordering.
- [ ] Permission enforced via parameter-injected `Depends(require_perm("Dunning.Read"))`.
- [ ] Success response uses list envelope with `items/page/page_size/total`.
- [ ] Error mapping expectations for `400/404/422` are implemented consistently.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CL-03/results.jsonl`
  - `artifacts/PE-BE-CL-03/summary.md`
  - `artifacts/PE-BE-CL-03/git/diff.patch`
