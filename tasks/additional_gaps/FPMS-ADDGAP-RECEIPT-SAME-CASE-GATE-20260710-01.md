# FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01

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

任何收据附件写入前，附件文档 case_id 必须等于 package case_id。

## Explicit Non-Closure

不判断 OA 来源归属，不扫描历史数据，不 archive package。

## Dependencies

- `FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`
- `FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`
- `FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`

## Allowed Files

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_receipt_same_case_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 OfficialWorkflow.Update。
- Status codes/errors: 404 package/attachment；400 OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH；有效写入 201。
- Response envelope: 沿用当前 receipt 输出模型。
- SQLite: 校验先于任何写；事务短。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_receipt_same_case_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_receipt_same_case_gate.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_receipt_same_case_gate.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_receipt_same_case_gate.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_receipt_same_case_gate.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
