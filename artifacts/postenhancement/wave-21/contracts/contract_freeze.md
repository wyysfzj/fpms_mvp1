# Wave 21 Contract Freeze

## Task
- Task ID: `PE-BE-CL-04`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-04.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CL-04/**`
- Out of scope:
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`POST /bills/{bill_id}/bad-debt`)
- Method/path:
  - `POST /bills/{bill_id}/bad-debt`
- Path parameter:
  - `bill_id` (required)
- Request payload assumptions:
  - no complex body required; optional remark/reason payload is acceptable if task implementation chooses to support it.
- Success status:
  - `200 OK` (action endpoint with content payload)
- Expected success payload:
  - action result/summary for the updated bill, including at minimum:
    - `bill_id`
    - updated `status` (toward `BAD_DEBT`)
    - `is_bad_debt` flag (or equivalent status evidence)
    - `balance` snapshot
    - optional `bad_debt_date` / `bad_debt_reason`

## Permission Contract
- Required permission:
  - `BadDebt.Action`
- Mandatory enforcement pattern:
  - `_perm: None = Depends(require_perm("BadDebt.Action"))`
- Do not use decorator-level `dependencies=[...]` for permission enforcement.

## Bill Eligibility Rules (Mandatory)
- Only bills with outstanding balance are eligible:
  - `balance > 0`
- Bill must not already be marked bad debt.
- Bill statuses representing settled/closed/cancelled/voided/zero-balance should be excluded from bad-debt marking.
- Eligibility validation is service-owned and must be deterministic for repeated calls.

## Status Transition Semantics (Toward `BAD_DEBT`)
- Valid transition target:
  - bill status transitions to `BAD_DEBT` (or module-defined equivalent with explicit bad-debt marker).
- Transition effects:
  - set bad-debt marker metadata (`is_bad_debt`, date/reason if used)
  - preserve financial fields (no artificial balance zeroing by this action alone)
- Repeated mark attempt on already bad-debt bill:
  - treated as conflict, not success.

## Error Mapping Expectations
- `400` business validation:
  - bill is not eligible for bad-debt action
  - expected code: `BAD_DEBT_NOT_ALLOWED`
- `404` resource not found:
  - `bill_id` does not exist / inaccessible scope
- `409` conflict:
  - bill already marked as bad debt
  - expected code: `BAD_DEBT_ALREADY_MARKED`
- Envelope semantics:
  - preserve BusinessError/FastAPI envelope conventions; do not invent new error shapes.

## Regression Risks
- Eligibility regression:
  - allowing settled/cancelled/zero-balance bills into bad debt corrupts receivables logic.
- Transition regression:
  - failing to set consistent bad-debt state/markers causes downstream reporting mismatch.
- Duplicate action regression:
  - repeated calls without conflict protection can create unstable audit/state behavior.
- Permission regression:
  - wrong permission code or non-parameter injection breaks authorization control.
- Scope risk:
  - changes outside allowlist violate atomic task policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted files:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- [ ] `POST /bills/{bill_id}/bad-debt` endpoint implemented.
- [ ] Permission enforced via parameter-injected `Depends(require_perm("BadDebt.Action"))`.
- [ ] Eligibility enforces outstanding-balance-only and excludes ineligible bill states.
- [ ] Successful action transitions bill state toward `BAD_DEBT` with expected payload.
- [ ] Error mapping follows `400/404/409` contract (`BAD_DEBT_NOT_ALLOWED`, `BAD_DEBT_ALREADY_MARKED`).
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CL-04/results.jsonl`
  - `artifacts/PE-BE-CL-04/summary.md`
  - `artifacts/PE-BE-CL-04/git/diff.patch`
