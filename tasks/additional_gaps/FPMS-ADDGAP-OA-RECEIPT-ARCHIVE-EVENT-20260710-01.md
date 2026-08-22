# FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 4
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

在一个 OFFICIAL_RECEIPT_ARCHIVED 事务中重验收据、精确关闭一个 OA task、archive package、将 OA1/OA2 恢复 SUB_EXAM 并写证据。

## Explicit Non-Closure

override 不发事件、不关 task、不改 case；不实现收据号内容匹配或通用状态矩阵。

## Dependencies

- `FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01`
- `FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`
- `FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`
- `FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-BACKEND-REGRESSION-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_oa_receipt_archive_event.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 OfficialWorkflow.Update。
- Status codes/errors: 缺/无效收据、零/多任务、错误 case state 均 409 且零写入；override 200/OVERRIDE；重复 archive 幂等。
- Response envelope: 沿用现有 `OfficialWorkPackageArchiveResultOut`（`package + evaluation`），不新增响应字段。
- SQLite: 单短事务，关闭选择必须确定且 SQLite-safe。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_receipt_archive_event.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_archive_event.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_archive_event.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_archive_event.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_oa_receipt_archive_event.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
