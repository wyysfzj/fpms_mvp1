# Wave 31 Contract Freeze

## Task
- Task ID: `PE-BE-COM-09`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-09.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-09/**`
- Out of scope:
  - router wiring
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`POST /commission/settlements/{id}/generate-lines`)
- Method/path:
  - `POST /commission/settlements/{id}/generate-lines`
- Path parameter:
  - `id` (settlement id, required)
- Success status:
  - `200 OK`
- Success payload semantics:
  - settlement generation result summary with at least:
    - `settlement_id`
    - `line_count`
    - `total_amount`
    - `created_count`
    - `updated_count`
    - `status` (current settlement status after generation)

## Eligible Commission Selection Criteria
- Settlement preconditions:
  - settlement exists and is in a generation-allowed state (`DRAFT` or already-generated reopenable state).
  - settlement must have valid scope data (`agent_id`, optional `period_from/period_to` coherence).
- Commission eligibility (all required):
  - `is_settleable = true`
  - `status` in active/non-terminal states (exclude settled/closed/cancelled-like terminal states)
  - `agent_id` matches settlement `agent_id`
  - period filter by settlement header:
    - if `period_from` set, `commission.settleable_date >= period_from`
    - if `period_to` set, `commission.settleable_date <= period_to`
    - rows with null `settleable_date` are excluded when period bound exists
  - unsettled amount exists (deterministic amount > 0)
- Deterministic amount basis per commission row:
  - `line_amount = (s1_amount if s1_done=false else 0) + (s2_amount if s2_done=false else 0)`
  - include only rows with `line_amount > 0`.

## Idempotent Behavior (Multiple Calls)
- Hard requirement:
  - multiple calls with same settlement and unchanged source data must not create duplicate lines.
- Duplicate protection:
  - respect unique pair `(settlement_id, commission_id)` from schema contract.
- Rerun behavior:
  - existing lines are reused/updated deterministically, not duplicated.
  - repeated call converges to same `line_count` and `total_amount` for unchanged eligibility set.
  - if no newly eligible rows, endpoint returns success as no-op with stable totals.

## Line Creation, Totals Update, and Status Transitions
- Line creation/update:
  - create one line per eligible commission not already linked.
  - line numbering must remain deterministic and unique within settlement (`line_no` monotonic per settlement).
  - `amount` stores computed unsettled commission amount for that row at generation time.
- Settlement aggregate updates:
  - `line_count` = number of persisted settlement lines for the header.
  - `total_amount` = sum of settlement line `amount`.
  - both fields recalculated from line table after generation, not incremented blindly.
- Settlement status transitions:
  - successful generation with one or more lines: `DRAFT -> GENERATED` (or module-equivalent generated state).
  - idempotent rerun in generated state remains generated.
  - generation attempt in disallowed terminal states must be rejected with conflict semantics.

## Permission Contract
- Required permission:
  - `CommissionSettlement.Action`
- Mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("CommissionSettlement.Action"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Error Semantics (404/400/409)
- `404`:
  - settlement id not found.
- `400`:
  - invalid settlement scope/range data (e.g., invalid period semantics), invalid generation input context.
- `409`:
  - settlement state does not allow line generation.
  - deterministic conflict conditions during line upsert/duplicate protection path.
- Preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Selection regression:
  - missing settleable/status/agent/period gates can include wrong commissions.
- Duplicate regression:
  - reruns creating repeated settlement lines inflate totals.
- Aggregate regression:
  - non-recomputed totals cause mismatch between line table and header fields.
- Status-flow regression:
  - invalid or missing settlement state transition blocks downstream settlement lifecycle.
- Permission regression:
  - wrong permission code/injection pattern breaks access control.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- [ ] `POST /commission/settlements/{id}/generate-lines` endpoint is implemented.
- [ ] Eligibility filter enforces settleable + status + agent + period criteria.
- [ ] Generation is idempotent for repeated calls (no duplicate lines).
- [ ] Line creation/update logic keeps deterministic `line_no` and per-line amount semantics.
- [ ] Settlement `line_count` and `total_amount` are recalculated consistently from lines.
- [ ] Settlement status transition behavior is deterministic and conflict-safe.
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("CommissionSettlement.Action"))`
- [ ] Error semantics align with `404/400/409` contract.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-09/results.jsonl`
  - `artifacts/PE-BE-COM-09/summary.md`
  - `artifacts/PE-BE-COM-09/git/diff.patch`
