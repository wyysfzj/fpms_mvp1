# SKELE2E-HARNESS-PAYLISTPARTIAL-01 — Skeleton TC-A-018 expects partial pay-list status

Task ID: `SKELE2E-HARNESS-PAYLISTPARTIAL-01`

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack `TC-A-018` DB assertion so it expects the product pay-list status after one of multiple GOV payment rows is paid.

This task closes only:

1. `TC-A-018` still verifies zero-payment validation, duplicate government payment rejection, and mark-paid state conflict.
2. The final DB assertion expects `t_pay_list.status = PARTIAL` after only the first GOV item is paid.
3. Existing product pay-list status recomputation remains unchanged.

## Explicit Non-Closure

No product backend changes. No database schema or migration changes. No frontend changes.
Do not change pay-list creation, government payment registration, duplicate validation, mark-paid rules, fee draft generation, or batch filing behavior.

## Remaining Follow-Up Task IDs

- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one Wave A handler and one focused Wave A harness test. |
| prereq_dependency_density | Medium. It removes the final backend Wave A E2E blocker before full backend rerun. |
| be_fe_coupling | Low. This is backend E2E harness-only and has no frontend surface. |
| evidence_cost | Medium. Requires RED/GREEN focused tests, lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-PAYLISTPARTIAL-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_gov_paylist_partial_handler.py`
- `artifacts/SKELE2E-HARNESS-PAYLISTPARTIAL-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-PAYLISTPARTIAL-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_a_gov_paylist_partial_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_gov_paylist_partial_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-PAYLISTPARTIAL-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-PAYLISTPARTIAL-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-PAYLISTPARTIAL-01/`

## Done Definition

- Focused tests prove `TC-A-018` asserts `PARTIAL` after a single GOV row is paid from a multi-row pay list.
- The full backend Skeleton Pack rerun no longer fails on `TC-A-018`.
- No product files are modified.
- Required evidence files exist and task gates pass.
