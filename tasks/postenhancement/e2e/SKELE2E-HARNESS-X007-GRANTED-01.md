# SKELE2E-HARNESS-X007-GRANTED-01 — Skeleton X007 granted case setup

Task ID: `SKELE2E-HARNESS-X007-GRANTED-01`

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack `TC-X-007` granted-case setup so the `GRANTED` test case includes the product-required publication, grant, and annuity fields when it is created.

This task closes only:

1. `TC-X-007` passes required fields for a `GRANTED` case: `pub_no`, `pub_date`, `grant_no`, `grant_date`, `first_annuity_year`, and `valid_until`.
2. The focused handler unit test proves the granted-case POST payload contains those fields.
3. The case report assertions and product backend behavior remain unchanged.

## Explicit Non-Closure

No product backend changes. No database schema or migration changes. No frontend changes.
Do not change case status validation rules, report endpoint behavior, other X-wave handlers, or remaining backend E2E blockers.

## Remaining Follow-Up Task IDs

- `SKELE2E-COMMISSION-SPLIT-01`
- `SKELE2E-READINESS-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one X-wave handler and one focused handler test. |
| prereq_dependency_density | Medium. It removes a test-data blocker before remaining X-wave/backend failures can be measured cleanly. |
| be_fe_coupling | Low. This is backend E2E harness-only and has no frontend surface. |
| evidence_cost | Medium. Requires RED/GREEN focused tests, lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-X007-GRANTED-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_report_handler.py`
- `artifacts/SKELE2E-HARNESS-X007-GRANTED-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-X007-GRANTED-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_x_case_report_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_report_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-X007-GRANTED-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-X007-GRANTED-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-X007-GRANTED-01/`

## Done Definition

- Focused tests prove the X007 granted-case payload includes the required product fields.
- The real X007 handler creates the granted-case fixture without relying on invalid product state.
- No product files are modified.
- Required evidence files exist and task gates pass.
