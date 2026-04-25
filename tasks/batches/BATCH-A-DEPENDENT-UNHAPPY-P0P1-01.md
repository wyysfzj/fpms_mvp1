# BATCH-A-DEPENDENT-UNHAPPY-P0P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Batch Goal

Land A-wave dependent unhappy P0/P1 automation for:

- TC-A-012
- TC-A-016
- TC-A-018
- TC-A-020
- TC-A-022
- TC-A-024

This batch may only run automation tasks whose readiness blockers are PASS. It must not fake PASS for product/backend gaps.

## Serialized Wave Order

1. Readiness gate: BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE
2. Blocker drain: BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-BLOCKER-DRAIN
3. Automation landing for unblocked tasks, serializing `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`

## Atomic Automation Tasks

### A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01

- Testcase: TC-A-012
- Handler: `handle_tc_a_012`
- Exact closure slice: empty selection rejected, submitted date before receive date rejected, submitted date equal receive date accepted.
- Allowed files:
  - tasks/automation/A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01.md
  - FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
  - FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_batch_submit_handler.py
  - artifacts/A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01/**

### A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01

- Testcase: TC-A-016
- Handler: `handle_tc_a_016`
- Exact closure slice: implement only after PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01 and BE-A-APPLY-FEE-ITEM-VALIDATION-01 PASS.
- Allowed files:
  - tasks/automation/A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01.md
  - FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
  - FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_fee_draft_handler.py
  - artifacts/A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01/**

### A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01

- Testcase: TC-A-018
- Handler: `handle_tc_a_018`
- Exact closure slice: implement only after PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01 and required backend/frontend blockers PASS.
- Allowed files:
  - tasks/automation/A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01.md
  - FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
  - FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_gov_paylist_handler.py
  - artifacts/A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01/**

### A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01

- Testcase: TC-A-020
- Handler: `handle_tc_a_020`
- Exact closure slice: mixed clients, mixed currencies, empty draft/bill, and negative AR bill are rejected with stable billing semantics.
- Allowed files:
  - tasks/automation/A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01.md
  - FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
  - FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_bill_handler.py
  - artifacts/A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01/**

### A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01

- Testcase: TC-A-022
- Handler: `handle_tc_a_022`
- Exact closure slice: payment and offset invalid data branches, duplicate pay number, over-offset, and prepayment recognition.
- Allowed files:
  - tasks/automation/A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01.md
  - FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
  - FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_payment_offset_handler.py
  - artifacts/A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01/**

### A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01

- Testcase: TC-A-024
- Handler: `handle_tc_a_024`
- Exact closure slice: wait-pay threshold and force-settle override assertions through real commission query.
- Allowed files:
  - tasks/automation/A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01.md
  - FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
  - FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_commission_handler.py
  - artifacts/A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01/**

## Non-Closure

- Do not modify skeleton YAML / JSON / manifest / schema / Playwright.
- Do not modify backend/frontend inside automation tasks.
- Do not use offline/default result as PASS.
- Do not remove `@skeleton_case` from blocked handlers.
- Do not use unrelated validation errors as testcase closure.

## Verification

Each PASS automation task must run its task-specific test, `pytest tests/test_wave_a.py -k <TC-ID> -q`, scoped ruff on allowlisted files, real smoke with `FPMS_DB_DSN=`, artifact hygiene, and task gate.
