# Wave 25 Contract Freeze

## Task
- Task ID: `PE-BE-COM-03`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-03.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-03/**`
- Out of scope:
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`PUT /commission/rules/{rule_id}`)
- Method/path:
  - `PUT /commission/rules/{rule_id}`
- Path parameter:
  - `rule_id` (required)
- Permission:
  - `CommissionRule.Edit`
  - mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("CommissionRule.Edit"))`
- Success status:
  - `200 OK`
- Success payload semantics:
  - returns full updated rule resource (including `id` and persisted normalized fields).

## Updatable Fields (Contracted)
- Rule control:
  - `rule_name`
  - `enabled`
  - `remark`
- Scope dimensions:
  - `case_type`
  - `fee_type`
  - `flow_dir`
  - `patent_category`
- Commission parameters:
  - `s1_rate`
  - `s2_rate`
  - `s1_fixed_amount`
  - `s2_fixed_amount`
  - `wait_pay`
  - `force_settle`
- Effective window:
  - `effective_from`
  - `effective_to`

## Validation Semantics
- Parameter validation (`400` business level):
  - `s1_rate`, `s2_rate` must remain in `[0, 1]`.
  - fixed amounts must be `>= 0`.
  - if both provided, `effective_from <= effective_to`.
  - invalid update payload or incompatible field combinations should fail deterministically.
- Partial update handling:
  - omitted fields retain existing persisted values.
  - validation must run on effective final state (current + patch), not only incoming delta.

## Overlap-Conflict Recheck Semantics
- On update, uniqueness/overlap check must be re-evaluated against other rules.
- Conflict definition (same as create contract):
  - same applicability dimensions (`case_type`, `fee_type`, `flow_dir`, `patent_category`, `wait_pay`, `force_settle`)
  - overlapping effective windows (open-ended supported)
  - excluding the current `rule_id` itself from conflict comparison.
- Conflict response:
  - `409` with `COMMISSION_RULE_CONFLICT`.

## Error Mapping Expectations
- `400`:
  - business parameter/range/date validation failures.
- `404`:
  - `rule_id` not found (`COMMISSION_RULE_NOT_FOUND` alignment).
- `409`:
  - overlap/duplicate conflict after recheck (`COMMISSION_RULE_CONFLICT`).
- Preserve BusinessError/FastAPI envelope conventions; do not introduce custom error shape.

## Regression Risks
- Update-delta validation risk:
  - validating only changed fields can permit invalid final state.
- Conflict-recheck risk:
  - missing exclusion of current rule or missing overlap logic causes false positives/negatives.
- Scope-drift risk:
  - unplanned updates to non-updatable fields break contract expectations.
- Permission regression:
  - wrong permission code or non-parameter injection breaks authorization control.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted files:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- [ ] `PUT /commission/rules/{rule_id}` endpoint implemented.
- [ ] Permission enforced via parameter-injected `Depends(require_perm("CommissionRule.Edit"))`.
- [ ] Updatable fields conform to contracted field set and preserve non-updated fields.
- [ ] Validation rules enforce rate/fixed/effective-range constraints on final merged state.
- [ ] Overlap/duplicate conflict recheck executed during update (excluding self rule).
- [ ] Error mapping follows `400/404/409` contract.
- [ ] Success returns `200` with updated resource payload.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-03/results.jsonl`
  - `artifacts/PE-BE-COM-03/summary.md`
  - `artifacts/PE-BE-COM-03/git/diff.patch`
