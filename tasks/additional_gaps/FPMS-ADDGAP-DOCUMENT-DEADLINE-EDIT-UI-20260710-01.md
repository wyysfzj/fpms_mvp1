# FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01

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

DocumentEdit 显示期限 lineage，可确认 missing/legacy 的同一日期，并将 confirmed date 保持只读。

## Explicit Non-Closure

不提供已确认日期 override，不同步非 OA task，不改 create/wizard。

## Dependencies

25, 26, 31

## Remaining Follow-Up Task IDs

- 46

## Allowed Files

- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentEdit.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-edit-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 消费 Doc.Edit。
- Status codes/errors: 消费 update 200/400/409/422。
- Response envelope: 消费 DocumentOut。
- SQLite: N/A。
- Simplified Chinese UI: lineage、确认动作、只读原因及错误必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-document-deadline-edit-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/documents.ts frontend/src/api/documents.types.ts frontend/src/modules/documents/pages/DocumentEdit.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-edit-ui.spec.ts`

## Evidence Path

Initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
