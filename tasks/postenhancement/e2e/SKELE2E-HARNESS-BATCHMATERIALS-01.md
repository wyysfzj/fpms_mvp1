# SKELE2E-HARNESS-BATCHMATERIALS-01 — Skeleton Batch 2 cases seed final material documents

Task ID: `SKELE2E-HARNESS-BATCHMATERIALS-01`

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack Batch 2 case arrangement helper so cases submitted by `TC-A-011` through `TC-A-014` have the mandatory final material documents required by the product batch filing material gate.

This task closes only:

1. `_arrange_batch2_cases` creates or reuses `CLIENT_IN` material documents for each arranged case.
2. Invention and utility model cases receive request, specification, claims, and abstract documents.
3. Design cases receive request and design picture/photo documents.

## Explicit Non-Closure

No product backend changes. No database schema or migration changes. No frontend changes.
Do not change batch filing gate rules, submit endpoint behavior, case state transitions, task generation, fee generation, or pay-list behavior.

## Remaining Follow-Up Task IDs

- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one Wave A handler and one focused Wave A harness test. |
| prereq_dependency_density | High. It removes the shared material-gate prerequisite for TC-A-011 through TC-A-014 before remaining Wave A failures can be measured cleanly. |
| be_fe_coupling | Low. This is backend E2E harness-only and has no frontend surface. |
| evidence_cost | Medium. Requires RED/GREEN focused tests, lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-BATCHMATERIALS-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_batch_materials_handler.py`
- `artifacts/SKELE2E-HARNESS-BATCHMATERIALS-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-BATCHMATERIALS-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_a_batch_materials_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_batch_materials_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-BATCHMATERIALS-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-BATCHMATERIALS-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-BATCHMATERIALS-01/`

## Done Definition

- Focused tests prove `_arrange_batch2_cases` seeds mandatory final material documents by patent category.
- Batch filing submit gate rules remain product-owned and unchanged.
- No product files are modified.
- Required evidence files exist and task gates pass.
