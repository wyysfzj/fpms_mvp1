# BATCH-A-P1-COMPLETION-01-BLOCKER-DRAIN

Batch ID: `BATCH-A-P1-COMPLETION-01-BLOCKER-DRAIN`

Source: `docs/automation/readiness/BATCH-A-P1-COMPLETION-01-READINESS-GATE.md`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Drain Order

### Wave 1: Product Contracts

1. `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01`
   - Path: `tasks/product/PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01.md`
   - Type: product contract
   - Closure: decide `TC-A-002` assertion surface for `PrioDate`, `GeneralPowerUsed`, full field persistence, and audit fields.
   - Non-closure: no backend/frontend/pytest handler changes.
   - Allowed files: task doc, `docs/product/PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01.md`, artifacts.

2. `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01`
   - Path: `tasks/product/PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01.md`
   - Type: product contract
   - Closure: decide strict-country inventor requirement, disabled-address representation, empty doc/bill address warning/block envelope.
   - Non-closure: no backend/frontend/pytest handler changes.
   - Allowed files: task doc, `docs/product/PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01.md`, artifacts.

3. `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01`
   - Path: `tasks/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md`
   - Type: product contract
   - Closure: decide save-time `fee_reduction` 0..1 semantics, `discount_rate` assertion surface, and applicant-kind/fee-policy warning/block.
   - Non-closure: no backend/frontend/pytest handler changes.
   - Allowed files: task doc, `docs/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md`, artifacts.

### Wave 2: Backend Readiness

4. `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01`
   - Path: `tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01.md`
   - Type: backend capability
   - Closure: make batch filing generated `APPLY_FEE_LIMIT` tasks honor supported `TaskTemplate.deadline_base` values needed by `TC-A-014`, especially `CASE_EVENT` and `FILING_DATE`, with reminders and daily reminder behavior preserved.
   - Non-closure: no pytest handler, no frontend, no skeleton data.
   - Allowed files:
     - `tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01.md`
     - `backend/app/modules/cases/service.py`
     - `backend/tests/test_apply_fee_limit_base_source.py`
     - `artifacts/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01/**`
   - Verification from `backend/`:
     - `python3 -m ruff check --fix app/modules/cases/service.py tests/test_apply_fee_limit_base_source.py`
     - `python3 -m ruff format app/modules/cases/service.py tests/test_apply_fee_limit_base_source.py`
     - `python3 -m ruff check app/modules/cases/service.py tests/test_apply_fee_limit_base_source.py`
     - `pytest tests/test_apply_fee_limit_base_source.py -q`
     - `pytest tests/test_apply_fee_limit_task_fields.py -q`

5. `BE-A-TASK-REMINDER-RESPONSE-01`
   - Path: `tasks/backend/apis_ext/BE-A-TASK-REMINDER-RESPONSE-01.md`
   - Type: backend API response
   - Closure: expose existing reminder fields in task detail and list responses so automation can assert TC-A-014 with `FPMS_DB_DSN=`.
   - Non-closure: no task generation, case logic, frontend, skeleton data, or pytest handler changes.
   - Allowed files:
     - `tasks/backend/apis_ext/BE-A-TASK-REMINDER-RESPONSE-01.md`
     - `backend/app/modules/tasks/schemas.py`
     - `backend/app/modules/tasks/api.py`
     - `backend/tests/test_task_reminder_response.py`
     - `artifacts/BE-A-TASK-REMINDER-RESPONSE-01/**`
   - Verification from `backend/`:
     - `python3 -m ruff check --fix app/modules/tasks/schemas.py app/modules/tasks/api.py tests/test_task_reminder_response.py`
     - `python3 -m ruff format app/modules/tasks/schemas.py app/modules/tasks/api.py tests/test_task_reminder_response.py`
     - `python3 -m ruff check app/modules/tasks/schemas.py app/modules/tasks/api.py tests/test_task_reminder_response.py`
     - `pytest tests/test_task_reminder_response.py -q`
     - `pytest tests/test_apply_fee_limit_base_source.py -q`

### Wave 3: Contract-Dependent Backend Tasks

Only author and execute these after their product contracts PASS:

- `BE-A-CASE-A2-FULL-FIELDS-READINESS-01`
- `BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01`
- `BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01`

## Executed Drain Status

| Task ID | Status |
| --- | --- |
| `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01` | PASS |
| `BE-A-TASK-REMINDER-RESPONSE-01` | PASS |
| `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01` | product_decision_required |
| `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01` | product_decision_required |
| `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01` | product_decision_required |

If product contracts mark behavior as deferred, do not implement backend guesses. Update the matching automation task scope only if the contract explicitly narrows the assertion surface.

## Hard Rules

- Do not modify `wave_a.py` in blocker drain.
- Do not run SQLite write tests concurrently.
- Serialize all tasks touching `backend/app/modules/cases/service.py`.
- No fake PASS for product_decision_required behavior.
