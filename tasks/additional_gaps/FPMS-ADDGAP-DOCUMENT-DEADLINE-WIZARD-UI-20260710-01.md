# FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 6
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

DocumentWizard 每一行展示并持久化 structured due/source/write-status。

## Explicit Non-Closure

不修改 backend contract，不重做 wizard 交互，不实现 edit UI。

## Dependencies

29, 30

## Remaining Follow-Up Task IDs

- 32

## Allowed Files

- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentWizard.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-wizard-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 消费 Doc.Create。
- Status codes/errors: 消费 wizard 成功合同及 400/409/422。
- Response envelope: 消费既有 wizard 结果。
- SQLite: N/A。
- Simplified Chinese UI: 所有逐行字段、阻断和错误必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-document-deadline-wizard-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/documents.ts frontend/src/api/documents.types.ts frontend/src/modules/documents/pages/DocumentWizard.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-wizard-ui.spec.ts`

## Evidence Path

Initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
