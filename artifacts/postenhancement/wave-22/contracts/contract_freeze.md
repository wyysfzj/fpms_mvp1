# Wave 22 Contract Freeze

## Task
- Task ID: `PE-BE-CL-05`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-05.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CL-05/**`
- Out of scope:
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`POST /bills/{bill_id}/bad-debt/restore`)
- Method/path:
  - `POST /bills/{bill_id}/bad-debt/restore`
- Path parameter:
  - `bill_id` (required)
- Request payload assumptions:
  - body may be empty; optional restore remark/reason fields are acceptable if implemented.
- Success status:
  - `200 OK`
- Expected success payload:
  - action result for restored bill with at minimum:
    - `bill_id`
    - restored `status`
    - bad-debt marker cleared evidence
    - `amount` and `balance` snapshot values

## Eligibility Rules (Mandatory)
- Bill must currently be in `BAD_DEBT` status (or equivalent bad-debt marker state).
- Restore is invalid when bill is not in bad-debt state.
- Restore must preserve financial integrity:
  - no mutation of `amount`/`balance` by restore action itself (status/marker action only).

## Deterministic Restore Target Status Mapping
- Restore target status must be derived from current `amount` and `balance`:
  - if `balance == amount` -> `UNSETTLED`
  - if `Decimal("0") < balance < amount` -> `PARTIALLY_SETTLED`
  - if `balance <= Decimal("0")` -> `SETTLED`
- Mapping must be deterministic and aligned with existing billing balance semantics.
- Any invalid financial state needed for mapping (for example impossible/null numeric context) should fail as business validation.

## Permission Contract
- Required permission:
  - `BadDebt.Action`
- Mandatory injection pattern:
  - `_perm: None = Depends(require_perm("BadDebt.Action"))`
- Do not use decorator-level `dependencies=[...]` for permission enforcement.

## Error Semantics (400/404/409)
- `400` business validation:
  - invalid financial/state data preventing deterministic restore mapping.
- `404` not found:
  - `bill_id` not found.
- `409` conflict:
  - restore requested for bill not currently in bad-debt state.
  - expected code alignment: `BAD_DEBT_RESTORE_INVALID`.
- Envelope semantics:
  - preserve existing BusinessError/FastAPI envelope conventions; do not invent new error shape.

## Regression Risks
- Eligibility regression:
  - allowing restore from non-`BAD_DEBT` states can corrupt bill lifecycle.
- Status mapping regression:
  - inconsistent mapping from `amount/balance` leads to divergent bill states.
- Financial integrity regression:
  - restore action incorrectly altering `amount`/`balance`.
- Permission regression:
  - wrong permission code or non-parameter injection breaks auth control.
- Scope risk:
  - edits beyond allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted files:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- [ ] `POST /bills/{bill_id}/bad-debt/restore` endpoint implemented.
- [ ] Permission enforced via parameter-injected `Depends(require_perm("BadDebt.Action"))`.
- [ ] Eligibility enforces current `BAD_DEBT` state requirement.
- [ ] Restore target status follows deterministic `amount/balance` mapping.
- [ ] Error semantics follow `400/404/409` contract (`BAD_DEBT_RESTORE_INVALID` on conflict).
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CL-05/results.jsonl`
  - `artifacts/PE-BE-CL-05/summary.md`
  - `artifacts/PE-BE-CL-05/git/diff.patch`
