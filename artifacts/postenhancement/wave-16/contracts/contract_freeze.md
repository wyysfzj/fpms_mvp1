# Wave 16 Contract Freeze

## Task
- Task ID: `PE-BE-AN-06`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-06.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-AN-06/**`
- Out of scope:
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (Batch PayList Generation)
- Method/path:
  - `POST /pay-lists/from-fee-items`
- Permission:
  - `PayList.Create`
  - injected as parameter:
  - `_perm: None = Depends(require_perm("PayList.Create"))`
- Request contract assumptions:
  - accepts selected fee-item identifiers to generate one pay-list batch.
  - supports batch-level options required to create pay-list header (for example planned pay date, currency if user-selected).

## Same-Client/Currency Constraints (Mandatory)
- Selected fee items must resolve to one logical client scope.
- Selected fee items must resolve to one effective pay-list currency scope.
- Mixed-client or mixed-currency selection must fail deterministically as business validation:
  - `400` with `PAY_LIST_SCOPE_INVALID`.
- Scope validation must happen before write operations to avoid partial invalid creation.

## Batch Result Contract (Mandatory)
- Endpoint returns batch receipt payload suitable for frontend result display.
- Minimum receipt fields:
  - `total_selected`
  - `accepted_count`
  - `rejected_count`
  - `pay_list` (created pay-list header summary when creation succeeds)
  - `accepted_items` (optional detailed list)
  - `rejected_items` (item-level reason/code/message)
- Partial handling assumption:
  - behavior must be deterministic and documented:
  - either strict fail-fast (no pay-list created) or controlled partial-accept mode.
  - whichever mode is chosen, response must clearly report item outcomes.

## Error Semantics
- `400` business validation errors:
  - single-client/single-currency scope violation (`PAY_LIST_SCOPE_INVALID`)
  - invalid selection scope/business rules
- `401` unauthenticated (`AUTH_REQUIRED`)
- `403` permission denied (`FORBIDDEN`)
- `404` referenced entities not found (if fail-fast lookup strategy is used)
- `409` conflict for duplicate/locked state scenarios if encountered in generation path
- `422` request schema/type validation failure
- Business errors must use standard BusinessError envelope (`error.code/message/details`).

## Regression Risks
- Scope-check regression:
  - weak validation can allow cross-client/currency mixing and corrupt pay-list semantics.
- Receipt contract regression:
  - missing per-item success/failure details breaks frontend result rendering and operator traceability.
- Write-order regression:
  - creating pay-list before full validation can leave orphaned/inconsistent records on failure.
- Permission regression:
  - incorrect permission code/injection style causes access control breakage.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-AN-06`.
- [ ] `POST /pay-lists/from-fee-items` endpoint exists and is wired at module level.
- [ ] Permission enforced with parameter-injected `PayList.Create`.
- [ ] Same-client/same-currency validation is enforced before writes.
- [ ] Scope violations return `400` with `PAY_LIST_SCOPE_INVALID`.
- [ ] Batch result payload returns clear aggregate + item-level outcomes.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-AN-06/results.jsonl`
  - `artifacts/PE-BE-AN-06/summary.md`
  - `artifacts/PE-BE-AN-06/git/diff.patch`
