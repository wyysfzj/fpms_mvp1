# FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 2
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

文档 need-reply 与案件状态副作用只消费 resolver 输出，不直接读取原始字段或模板名称。

## Explicit Non-Closure

不改变目录激活范围，不实现 OA 收据闭环，不修改任务期限规则。

## Dependencies

`FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01`
- `FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`
- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_document_semantic_state_effect.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用调用方权限。
- Status codes/errors: 冲突语义 fail-closed 为 409；成功状态码保持调用端既有合同。
- Response envelope: 沿用调用端既有包络。
- SQLite: 保持 SQLite 兼容查询和短事务。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_semantic_state_effect.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_document_semantic_state_effect.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_document_semantic_state_effect.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_document_semantic_state_effect.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_document_semantic_state_effect.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
