# FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01

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

新增唯一 `ResolvedDocumentSemantics` resolver，并对缺失、冲突或畸形的执行元数据 fail-closed。

## Explicit Non-Closure

不根据模板名称推断执行语义，不激活任何目录项，不改变持久化模型。

## Dependencies

`FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01`
- `FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01`
- `FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01`
- `FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01`
- `FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01`
- `FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01`
- `FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`
- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01`
- `FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`
- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`
- `FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`
- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`

## Allowed Files

- `backend/app/modules/documents/semantics.py`
- `backend/tests/test_addgap_document_semantics.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（纯服务组件）。
- Status codes/errors: resolver 以领域异常表达 400/409 语义，具体 API 映射由消费者保持。
- Response envelope: N/A（纯内部值对象）。
- SQLite: N/A。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_semantics.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py tests/test_addgap_document_semantics.py && .venv/bin/ruff format app/modules/documents/semantics.py tests/test_addgap_document_semantics.py && .venv/bin/ruff check app/modules/documents/semantics.py tests/test_addgap_document_semantics.py`
- Scope: `git diff --check -- backend/app/modules/documents/semantics.py backend/tests/test_addgap_document_semantics.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
