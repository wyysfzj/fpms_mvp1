# Wave 19 Contract Freeze

## Task
- Task ID: `PE-BE-CL-02`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-02.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/collections/api.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CL-02/**`
- Out of scope:
  - `backend/app/modules/collections/service.py` behavior changes (owned by `PE-BE-CL-01`)
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`POST /dunning`)
- Method/path:
  - `POST /dunning`
- Request shape:
  - `to_date` (required, date)
  - `client_id` (optional, string)
  - `client_ids` (optional, list[string])
  - `include_statuses` (optional, list[string])
  - `exclude_statuses` (optional, list[string])
  - `strict_conflict` (optional, bool, default `false`)
- Service binding:
  - endpoint must delegate to collections service dunning generation function without re-implementing generation logic in API layer.

## Permission Contract
- Required permission:
  - `Dunning.Create`
- Enforcement pattern (mandatory):
  - `_perm: None = Depends(require_perm("Dunning.Create"))`
- Do not use decorator `dependencies=[...]` for permission enforcement.

## Response Envelope Semantics
- Success status choice:
  - `200 OK` (chosen for action-style batch generation that may create and/or reuse batches in one call).
- Success payload shape:
  - top-level object with:
    - `summary` (batch operation aggregate info)
    - `batches` (list of generated/reused dunning batches)
- `summary` semantics:
  - includes cutoff and operation counts (for example eligible bills/groups/created/reused/batches totals).
- `batches` semantics:
  - batch-level metadata + line snapshots sufficient for caller to render result details.

## BusinessError to Status Mapping
- `400`:
  - `DUNNING_BATCH_STATE_INVALID` for invalid request/filter/state combinations.
- `404`:
  - `DUNNING_BATCH_NOT_FOUND` when scoped client request finds no overdue bills.
- `409`:
  - `DUNNING_BATCH_STATE_INVALID` when `strict_conflict=true` and duplicate generation is detected.
- `422`:
  - request schema/type validation errors (FastAPI validation path).
- Envelope rule:
  - preserve existing BusinessError envelope conventions (`error.code/message/details`).

## Regression Risks
- Permission regression:
  - wrong permission code or non-parameter injection pattern can break access control.
- Contract drift risk:
  - response shape divergence from `summary + batches` breaks downstream callers.
- Status mapping risk:
  - misclassifying duplicate strict conflicts as 400/200 instead of 409 breaks deterministic client handling.
- Scope risk:
  - API task accidentally modifying service or router violates atomic allowlist constraints.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product file `backend/app/modules/collections/api.py`.
- [ ] `POST /dunning` endpoint accepts required request shape (`to_date` + optional filters + `strict_conflict`).
- [ ] Permission enforced via parameter-injected `Depends(require_perm("Dunning.Create"))`.
- [ ] Success response uses `200` with envelope containing `summary` and `batches`.
- [ ] BusinessError status mapping follows `400/404/409` contract.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CL-02/results.jsonl`
  - `artifacts/PE-BE-CL-02/summary.md`
  - `artifacts/PE-BE-CL-02/git/diff.patch`
