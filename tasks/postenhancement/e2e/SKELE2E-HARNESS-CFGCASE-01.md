# SKELE2E-HARNESS-CFGCASE-01 — Skeleton config case setup reuse

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack W0 document impact preview setup so `TC-W0-CFG-009` looks up the run-id config case by `case_no` before creating it. This closes the `CASE_NO_DUPLICATE` failure observed in the post-RUNID backend E2E rerun when an earlier W0 setup case already created `CASE-CFG-${FPMS_RUN_ID}-001`.

## Explicit Non-Closure

No product backend changes. No frontend changes. No database schema or migration changes. No change to product case uniqueness validation. No changes to fee calc modes, commission rule reuse, seed readiness expectations, case priority DB contract, batch material gate setup, granted-case setup, pay-list lifecycle, or browser-use runtime.

## Remaining Follow-Up Task IDs

- `SKELE2E-FEERATE-CALCMODE-01`
- `SKELE2E-READINESS-CONTRACT-01`
- `SKELE2E-CASEPRIORITY-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-GRANTED-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one W0 handler file and one focused W0 handler test file. |
| prereq_dependency_density | Medium. It removes one W0 setup collision before remaining backend blockers can be isolated. |
| be_fe_coupling | Low. This is backend automation harness only and has no frontend surface. |
| evidence_cost | Medium. Requires focused TDD tests, lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-CFGCASE-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_doc_impact_preview_handler.py`
- `artifacts/SKELE2E-HARNESS-CFGCASE-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_w0_doc_impact_preview_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_doc_impact_preview_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-CFGCASE-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-CFGCASE-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-CFGCASE-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-CFGCASE-01/`

## Done Definition

- Focused tests prove `TC-W0-CFG-009` reuses an existing config case found by `case_no`.
- Focused tests prove document impact preview uses the reused case id.
- Product case uniqueness validation remains untouched.
- Required evidence files exist and task gates pass.
