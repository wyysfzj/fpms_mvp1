# FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01

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

文档普通创建和 wizard 均拒绝 reference-only official catalog template。

## Explicit Non-Closure

不拒绝普通非目录模板，不激活目录语义，不更改 UI。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`
- `FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_notice_catalog_reference_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 Doc.Create。
- Status codes/errors: reference-only 使用返回 409；可执行/普通模板保持既有成功状态。
- Response envelope: 错误沿用既有 detail 语义；成功沿用 DocumentOut/wizard 包络。
- SQLite: 校验先于持久化。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_catalog_reference_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_notice_catalog_reference_gate.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_notice_catalog_reference_gate.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_notice_catalog_reference_gate.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_notice_catalog_reference_gate.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
