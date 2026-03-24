# Wave 15 Contract Freeze

## Task
- Task ID: `PE-BE-AN-05`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-05.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/annuity/api.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-AN-05/**`
- Out of scope:
  - `backend/app/modules/annuity/service.py` logic changes (owned by `PE-BE-AN-04`)
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (Batch)
- Method/path:
  - `POST /annuity/tasks/generate-drafts`
- Permission:
  - `AnnuityTask.Action`
  - must be injected as parameter:
  - `_perm: None = Depends(require_perm("AnnuityTask.Action"))`
- Request contract assumptions:
  - JSON body includes batch task identifiers and options.
  - minimum fields:
    - `task_ids: list[int]` (non-empty)
    - `pay_next_year: bool` (default `false`)
- Response contract assumptions (batch receipt):
  - returns batch success/failed detail for frontend display.
  - minimum envelope shape:
    - `total`
    - `success_count`
    - `failed_count`
    - `successes` (per-task result items)
    - `failures` (per-task error detail items with code/message)
- Success status:
  - `200` for syntactically valid batch processing with receipt payload.

## Batch Behavior Assumptions
- Endpoint delegates generation behavior to AN-04 service; API layer does not re-implement domain logic.
- Partial success is supported:
  - successful items and failed items are both returned in one response payload.
- Idempotence/conflict outcomes from service are surfaced per item in `failures`.
- `pay_next_year` option is forwarded to service and reflected in item-level result semantics.

## Error Semantics (Mandatory)
- `400` Business validation failure:
  - malformed business payload (for example empty logical selection after normalization)
  - invalid batch options not covered by schema typing
- `401` unauthenticated (`AUTH_REQUIRED`)
- `403` permission denied (`FORBIDDEN`)
- `404` not-found semantics when endpoint chooses fail-fast on invalid references
  - otherwise not-found may appear as per-item failure in batch receipt
- `409` conflict semantics:
  - duplicate/conflicting generation (for example `ANNUITY_DRAFT_ALREADY_GENERATED`)
  - missing critical generation config (`ANNUITY_CONFIG_MISSING`)
- `422` request validation failure (schema/type)
- Envelope semantics:
  - business errors must follow BusinessError envelope (`error.code/message/details`)
  - do not introduce new custom top-level error envelope

## Regression Risks
- Contract drift risk:
  - response payload fields not matching frontend expectation can break receipt display.
- Partial-failure handling risk:
  - collapsing all item failures into one top-level error loses actionable per-item detail.
- Permission regression risk:
  - wrong permission code or incorrect dependency injection pattern causes access issues.
- Service/API boundary risk:
  - API re-implements AN-04 logic and diverges from idempotence/pay_next_year rules.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product file for `PE-BE-AN-05`.
- [ ] `POST /annuity/tasks/generate-drafts` endpoint exists in annuity API.
- [ ] Permission enforced with parameter-injected `AnnuityTask.Action`.
- [ ] Batch request supports task IDs + `pay_next_year` option.
- [ ] Batch response returns success/failed item details.
- [ ] Error semantics follow `400/401/403/404/409/422` contract and BusinessError envelope.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-AN-05/results.jsonl`
  - `artifacts/PE-BE-AN-05/summary.md`
  - `artifacts/PE-BE-AN-05/git/diff.patch`
