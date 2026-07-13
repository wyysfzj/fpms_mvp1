# FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 6
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

impact preview 显示 structured due lineage，缺确认时返回明确 409 blocker。

## Explicit Non-Closure

不写文档/任务，不改变 create/update，不提供推测日期。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_impact_preview.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: Doc.Create，函数参数 Depends 注入。
- Status codes/errors: POST 200 preview；缺确认/配置 409；shape 422；业务字段 400。
- Response envelope: 扩展既有 impact preview 模型，不发明外层 envelope。
- SQLite: 只读/纯计算。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_impact_preview.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_impact_preview.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_impact_preview.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_impact_preview.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_impact_preview.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
