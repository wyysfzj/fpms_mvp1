# SKELE2E-HARNESS-RUNID-01 — Skeleton run-id setup idempotency

## Exact Closure Slice

Update only FPMS Automation Skeleton Pack setup helpers so records reused within the same `FPMS_RUN_ID` are looked up before creation. This closes duplicate setup collisions for W0 config client/task-template/doc-template setup and A-wave applicant setup when multiple cases in the same clean backend wave reuse the same run-id-derived keys.

## Explicit Non-Closure

No product backend changes. No frontend changes. No database schema or migration changes. No weakening of product uniqueness validation. No changes to fee calc modes, case priority assertions, batch material gate setup, granted-case setup, pay-list lifecycle, or browser-use runtime.

## Remaining Follow-Up Task IDs

- `SKELE2E-FEERATE-CALCMODE-01`
- `SKELE2E-CASEPRIORITY-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-GRANTED-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. The task touches W0 and A-wave harness handlers plus focused harness tests. |
| prereq_dependency_density | High. This removes repeated setup collisions before remaining product/test-contract blockers can be isolated. |
| be_fe_coupling | Low. This is backend automation harness only and has no frontend surface. |
| evidence_cost | Medium. Requires focused TDD tests, lint, task gate, and a clean backend wave rerun. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-RUNID-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_task_deadline_template_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_doc_impact_preview_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py`
- `artifacts/SKELE2E-HARNESS-RUNID-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_w0_task_deadline_template_handler.py tests/test_w0_doc_impact_preview_handler.py tests/test_w0_commission_rule_handler.py tests/test_a_case_create_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_task_deadline_template_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_doc_impact_preview_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-RUNID-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-RUNID-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-RUNID-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-RUNID-01/`

## Done Definition

- Focused tests prove repeated W0 task/doc template setup reuses existing records instead of posting duplicates.
- Focused tests prove repeated W0 config client setup reuses existing records instead of posting duplicates.
- Focused tests prove A-wave applicant setup can find an existing applicant by `name_cn` when code search misses it.
- Product uniqueness validation remains untouched.
- Required evidence files exist and task gates pass.
