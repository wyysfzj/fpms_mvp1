# SKELE2E-HARNESS-DBASSERT-01 — Skeleton DB assertion SQLite-safe predicates

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack DB assertion helper so `assert_row_exists` and `assert_count` generate SQLite-safe SQL for valid identifiers and `None` values. The helper must quote safe table/column identifiers and express `None` predicates as `IS NULL` instead of `= NULL`.

## Explicit Non-Closure

No product backend code changes. No database schema or migration changes. No changes to business rules, endpoint contracts, handler setup data, frontend code, or browser-use runtime. This task does not fix remaining Skeleton Pack failures unrelated to DB assertion SQL generation.

## Remaining Follow-Up Task IDs

- `SKELE2E-HARNESS-AUTHME-01`
- `SKELE2E-HARNESS-RUNID-01`
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
| shared_file_density | Medium. The task touches one shared Skeleton Pack helper and its focused unit tests. |
| prereq_dependency_density | High. This is an early prerequisite for clean backend E2E assertions across multiple waves. |
| be_fe_coupling | Low. The task is backend test-harness only and has no frontend surface. |
| evidence_cost | Medium. Requires focused helper tests plus task gate evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-DBASSERT-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/db_assert.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_db_assert.py`
- `artifacts/SKELE2E-HARNESS-DBASSERT-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_db_assert.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-DBASSERT-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-DBASSERT-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-DBASSERT-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-DBASSERT-01/`

## Done Definition

- A focused failing test proves the current helper cannot match rows through a reserved identifier column such as `group`.
- A focused failing test proves `None` predicates need `IS NULL` semantics.
- `assert_row_exists` and `assert_count` pass those tests without loosening identifier validation.
- Existing DB assertion helper tests still pass.
- Required evidence files exist and task gates pass.
