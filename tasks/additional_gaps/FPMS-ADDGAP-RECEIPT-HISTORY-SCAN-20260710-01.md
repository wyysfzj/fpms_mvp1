# FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 3
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

新增只读扫描，报告历史 cross-case 与 OA-source-invalid receipt links。

## Explicit Non-Closure

不自动修复/删除历史数据，不修改产品 API，不 close task。

## Dependencies

- `FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`
- `FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`

## Allowed Files

- `backend/scripts/audit_receipt_ownership.py`
- `backend/tests/test_addgap_receipt_history_scan.py`
- `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01.md`
- `artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（离线只读审计）。
- Status codes/errors: 进程 0 表示扫描完成；发现问题通过结构化输出报告而非改写。
- Response envelope: N/A。
- SQLite: 只读、SQLite-safe 查询。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_receipt_history_scan.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix scripts/audit_receipt_ownership.py tests/test_addgap_receipt_history_scan.py && .venv/bin/ruff format scripts/audit_receipt_ownership.py tests/test_addgap_receipt_history_scan.py && .venv/bin/ruff check scripts/audit_receipt_ownership.py tests/test_addgap_receipt_history_scan.py`
- Scope: `git diff --check -- backend/scripts/audit_receipt_ownership.py backend/tests/test_addgap_receipt_history_scan.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
