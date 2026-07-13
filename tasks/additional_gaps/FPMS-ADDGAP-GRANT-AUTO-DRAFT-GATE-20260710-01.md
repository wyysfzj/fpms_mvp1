# FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 7
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

授权通知登记在客户指示前不再自动生成 generic zero-value FeeDraft。

## Explicit Non-Closure

不改变其他文档类型 B3 fee linking，不实现客户指示 workflow，不删除既有 fee draft。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`
- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_addgap_grant_auto_draft_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 Doc.Create。
- Status codes/errors: 授权文档创建成功但无零金额草稿；其他类型状态不变。
- Response envelope: 沿用调用端响应。
- SQLite: 校验/分支在现有事务内。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_auto_draft_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/fee_linking_service.py tests/test_addgap_grant_auto_draft_gate.py && .venv/bin/ruff format app/modules/documents/fee_linking_service.py tests/test_addgap_grant_auto_draft_gate.py && .venv/bin/ruff check app/modules/documents/fee_linking_service.py tests/test_addgap_grant_auto_draft_gate.py`
- Scope: `git diff --check -- backend/app/modules/documents/fee_linking_service.py backend/tests/test_addgap_grant_auto_draft_gate.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/**`, preserve RED/GREEN and focused non-grant regression evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
