# SKELE2E-HARNESS-COMMSPLIT-01 — Skeleton commission split setup persists case agent splits

Task ID: `SKELE2E-HARNESS-COMMSPLIT-01`

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack `TC-W0-CFG-006` setup so case agent splits are persisted through the product-supported `PUT /cases/{case_id}` path after the case is created.

This task closes only:

1. `TC-W0-CFG-006` no longer relies on `POST /cases` silently accepting `agent_splits`.
2. The focused handler unit test proves the handler sends the 70/30 split through `PUT /cases/{case_id}`.
3. Product commission service behavior, case API behavior, and split expectations remain unchanged.

## Explicit Non-Closure

No product backend changes. No database schema or migration changes. No frontend changes.
Do not change commission calculation rules, commission API response shape, case create schema, or other W0 readiness/batch/pay-list blockers.

## Remaining Follow-Up Task IDs

- `SKELE2E-READINESS-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one W0 handler and one focused handler test. |
| prereq_dependency_density | Medium. It removes a W0 setup blocker before remaining backend E2E failures can be measured cleanly. |
| be_fe_coupling | Low. This is backend E2E harness-only and has no frontend surface. |
| evidence_cost | Medium. Requires RED/GREEN focused tests, lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-COMMSPLIT-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py`
- `artifacts/SKELE2E-HARNESS-COMMSPLIT-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-COMMSPLIT-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_w0_commission_rule_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-COMMSPLIT-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-COMMSPLIT-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-COMMSPLIT-01/`

## Done Definition

- Focused tests prove the split setup issues a `PUT /cases/{case_id}` with the 70/30 `agent_splits`.
- `TC-W0-CFG-006` still expects two commission rows with 700/300 base fees.
- No product files are modified.
- Required evidence files exist and task gates pass.
