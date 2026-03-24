# Wave 23 Contract Freeze

## Task
- Task ID: `PE-BE-COM-01`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-01/**`
- Out of scope:
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`POST /commission/rules`)
- Method/path:
  - `POST /commission/rules`
- Permission:
  - `CommissionRule.Create`
  - mandatory parameter injection pattern:
  - `_perm: None = Depends(require_perm("CommissionRule.Create"))`
- Success status:
  - `201 Created`
- Success payload:
  - created commission rule resource (or equivalent full created object)
  - includes persisted `id` and normalized effective range fields.

## Request Fields and Validation Ranges
- Core fields:
  - `rule_name` (required, non-empty string)
  - `case_type` (optional string)
  - `fee_type` (optional string)
  - `flow_dir` (optional string)
  - `patent_category` (optional string)
  - `s1_rate` (required decimal ratio)
  - `s2_rate` (required decimal ratio)
  - `s1_fixed_amount` (optional/required by schema, decimal)
  - `s2_fixed_amount` (optional/required by schema, decimal)
  - `wait_pay` (required bool)
  - `force_settle` (required bool)
  - `enabled` (optional bool, default true)
  - `effective_from` (optional date)
  - `effective_to` (optional date)
  - `remark` (optional string)
- Required validation ranges:
  - `s1_rate`, `s2_rate` must be within `[0, 1]`.
  - `s1_fixed_amount`, `s2_fixed_amount` must be `>= 0`.
  - effective range rule: if both dates provided, `effective_from <= effective_to`.

## Uniqueness / Conflict Rule Definition
- A new rule conflicts with an existing rule when:
  - same applicability dimensions:
    - `case_type`
    - `fee_type`
    - `flow_dir`
    - `patent_category`
    - `wait_pay`
    - `force_settle`
  - and effective date windows overlap (treat open-ended dates as unbounded).
- Conflict should return domain conflict semantics:
  - `409` with `COMMISSION_RULE_CONFLICT`.

## Error Mapping (400/409)
- `400` business validation failures:
  - invalid ranges/amounts/date window
  - missing required business fields after normalization
- `409` conflict:
  - duplicate/overlapping rule per uniqueness definition
  - expected code: `COMMISSION_RULE_CONFLICT`
- Preserve standard envelope conventions (BusinessError/FastAPI), no new custom error envelope.

## Regression Risks
- Range-validation regression:
  - accepting out-of-range rates or negative fixed amounts breaks downstream commission math.
- Effective-window regression:
  - missing overlap checks allows conflicting active rules.
- Uniqueness drift:
  - inconsistent dimension matching creates non-deterministic rule selection.
- Permission regression:
  - wrong permission code or non-parameter injection pattern breaks auth control.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted files:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- [ ] `POST /commission/rules` endpoint implemented.
- [ ] Permission enforced via parameter-injected `Depends(require_perm("CommissionRule.Create"))`.
- [ ] Request field validation enforces rate/fixed-amount/date-range rules.
- [ ] Uniqueness conflict check implemented using defined dimensions + effective-window overlap.
- [ ] Success returns `201` with created rule payload.
- [ ] Error mapping includes `400` validation and `409 COMMISSION_RULE_CONFLICT`.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-01/results.jsonl`
  - `artifacts/PE-BE-COM-01/summary.md`
  - `artifacts/PE-BE-COM-01/git/diff.patch`
