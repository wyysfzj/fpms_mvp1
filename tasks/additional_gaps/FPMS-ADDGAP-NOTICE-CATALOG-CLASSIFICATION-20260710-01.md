# FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 5
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

将全部 60 条 official-notice catalog 行标记为 reference-only/non-selectable，保留源代码且无执行副作用。

## Explicit Non-Closure

不激活任何 OA、授权、复审、年费或其他语义，不删除目录项。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01`
- `FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01`
- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`

## Allowed Files

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/tests/test_addgap_notice_catalog_classification.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（目录数据定义）。
- Status codes/errors: N/A；所有未确认项 fail-closed。
- Response envelope: 目录输出字段沿用现有 schema。
- SQLite: N/A。
- Simplified Chinese UI: N/A；UI clarity 由 Task 20。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_catalog_classification.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py tests/test_addgap_notice_catalog_classification.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py tests/test_addgap_notice_catalog_classification.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py tests/test_addgap_notice_catalog_classification.py`
- Scope: `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/tests/test_addgap_notice_catalog_classification.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
