# SKELE2E-HARNESS-CASEPRIORITY-01 — Skeleton A002 priority table DB assertion

Task ID: `SKELE2E-HARNESS-CASEPRIORITY-01`

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack `TC-A-002` DB assertion contract so it checks the product priority table `t_priority` instead of the non-existent legacy table name `t_case_priority`.

This task closes only:

1. `TC-A-002` uses the current product table name for priority rows.
2. The focused handler unit test expects the same table name.
3. The API payload, UI expectations, and product backend behavior remain unchanged.

## Explicit Non-Closure

No product backend changes. No database schema or migration changes. No frontend changes.
Do not change case creation payloads, priority validation, bio-deposit assertions, or any non-`TC-A-002` handler behavior.
Do not change other remaining backend E2E blockers.

## Remaining Follow-Up Task IDs

- `SKELE2E-COMMISSION-SPLIT-01`
- `SKELE2E-READINESS-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-GRANTED-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one A-wave handler and one focused handler test. |
| prereq_dependency_density | Medium. It removes a DB contract blocker before remaining A-wave failures can be measured cleanly. |
| be_fe_coupling | Low. This is backend E2E harness-only and has no frontend surface. |
| evidence_cost | Medium. Requires RED/GREEN focused tests, lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-CASEPRIORITY-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_minimal_required_handler.py`
- `artifacts/SKELE2E-HARNESS-CASEPRIORITY-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-CASEPRIORITY-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_a_minimal_required_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_minimal_required_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-CASEPRIORITY-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-CASEPRIORITY-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-CASEPRIORITY-01/`

## Done Definition

- Focused tests prove `TC-A-002` expects `t_priority` for priority DB rows.
- `TC-A-002` handler asserts `t_priority` in real DB mode.
- No product files are modified.
- Required evidence files exist and task gates pass.
