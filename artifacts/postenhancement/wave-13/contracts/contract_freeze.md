# Wave 13 Contract Freeze

## Task
- Task ID: `PE-BE-AN-03`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-03.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-AN-03/**`
- Out of scope:
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract
- Method/path:
  - `PUT /annuity/tasks/{task_id}/instruction`
- Request body contract assumptions:
  - instruction value supports: `PAY`, `ABANDON`, `DEFER`
  - optional instruction date / remark may be accepted if needed by service
- Permission:
  - must enforce `AnnuityTask.Action`
  - injection pattern must be parameter-based:
  - `_perm: None = Depends(require_perm("AnnuityTask.Action"))`
- Success response:
  - HTTP `200`
  - response envelope must follow existing module conventions (no new custom envelope shape)

## State-Transition Assumptions
- Transition guard applies to `AnnuityTask.status` and instruction-related fields.
- Allowed instruction updates apply to non-terminal tasks only.
- Terminal/closed-like states are treated as non-editable for instruction updates.
- Repeated no-op or contradictory updates should be handled deterministically:
  - either idempotent success with unchanged state or explicit conflict (see `409` semantics below), but behavior must be consistent.
- Instruction update must persist:
  - `client_instruction`
  - `instruction_date` (explicit or derived)
  - status transition fields when required by business rule

## 400/404/409 Semantics (Mandatory)
- `400` Business validation failure:
  - invalid instruction value/payload
  - invalid state transition attempt
  - use annuity business error semantics (for example `ANNUITY_INSTRUCTION_INVALID`)
- `404` Resource not found:
  - annuity task ID does not exist
  - use annuity not-found semantics (for example `ANNUITY_TASK_NOT_FOUND`)
- `409` Conflict:
  - task exists but cannot accept instruction due to current conflicting state
  - duplicate/conflicting update scenario must return conflict rather than generic validation
- Envelope rule:
  - follow post-enhancement BusinessError envelope constraints (`error.code/message/details`)

## Regression Risks
- Transition drift risk:
  - transition rules in API and service can diverge, causing inconsistent behavior across callers.
- Semantic misclassification risk:
  - returning `400` where `409` is expected (or vice versa) breaks acceptance and client handling.
- Permission risk:
  - wrong permission code or wrong dependency injection style causes authorization regressions.
- Scope risk:
  - touching files outside allowlist violates atomic policy.
- Wiring interpretation risk:
  - endpoint may still be unreachable before module router wiring task (`PE-BE-WIRE-01`).

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-AN-03`.
- [ ] `PUT /annuity/tasks/{task_id}/instruction` implemented in annuity API.
- [ ] Permission enforced with `AnnuityTask.Action` via parameter-injected `Depends`.
- [ ] Service enforces valid instruction state transitions.
- [ ] `400/404/409` semantics are explicitly implemented and testable.
- [ ] Error envelope follows post-enhancement BusinessError conventions.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-AN-03/results.jsonl`
  - `artifacts/PE-BE-AN-03/summary.md`
  - `artifacts/PE-BE-AN-03/git/diff.patch`
