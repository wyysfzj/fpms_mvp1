# FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 5
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

DocumentCreate 显示全部目录行，使用简体中文可执行/仅供参考标签，并禁选 reference-only。

## Explicit Non-Closure

不隐藏 reference-only 项，不激活语义，不修改 backend gate。

## Dependencies

- `FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-notice-catalog-ui-clarity.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 DocTemplate.Read/Doc.Create。
- Status codes/errors: 读取成功 200；reference-only 在客户端不可提交。
- Response envelope: 消费既有模板列表响应。
- SQLite: N/A。
- Simplified Chinese UI: 所有标签、说明、禁用原因必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-notice-catalog-ui-clarity.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/modules/documents/pages/DocumentCreate.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-notice-catalog-ui-clarity.spec.ts`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
