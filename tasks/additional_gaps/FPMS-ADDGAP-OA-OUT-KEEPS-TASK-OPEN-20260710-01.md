# FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01

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

OA_OUT 仅记录内部答复日期，不改变 OA task 或 case state；普通非 OA reply 行为保持原范围。

## Explicit Non-Closure

不校验收据、不 archive package、不关闭任务、不恢复 SUB_EXAM。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_oa_out_keeps_task_open.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_spec_alignment_e2e.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 Doc.Create。
- Status codes/errors: 成功创建状态保持 201；语义冲突 409；不得产生提前 close。
- Response envelope: 沿用 DocumentOut。
- SQLite: 单事务内保持短写入。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_out_keeps_task_open.py`
- Legacy regression behavior: `cd backend && .venv/bin/pytest -q tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_oa_out_keeps_task_open.py backend/tests/test_b2_reply_chain.py backend/tests/test_spec_alignment_e2e.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/**`, preserve RED/GREEN and legacy regression command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
