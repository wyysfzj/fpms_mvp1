# FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01

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

同案 OA 收据必须附着于 linked reply document 或显式 package manifest。

## Explicit Non-Closure

不验证收据号内容，不扫描历史数据，不 archive/close。

## Dependencies

- `FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`
- `FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`

## Allowed Files

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_oa_receipt_source_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 OfficialWorkflow.Update。
- Status codes/errors: 无效来源 400 OA_RECEIPT_ATTACHMENT_SOURCE_INVALID；有效写入 201。
- Response envelope: 沿用当前 receipt 输出模型。
- SQLite: 先校验后写入。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_receipt_source_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_source_gate.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_source_gate.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_source_gate.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_oa_receipt_source_gate.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
