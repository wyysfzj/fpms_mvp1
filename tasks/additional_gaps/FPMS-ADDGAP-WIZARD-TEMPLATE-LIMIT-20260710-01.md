# FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 1
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

DocumentWizard 请求启用模板时将 `page_size` 限制为 API 接受的最大值 100，消除真实页面路径上的确定性 422。

## Explicit Non-Closure

不重做模板分页、搜索、缓存或其他 DocumentWizard 行为。

## Dependencies

Wave 0 planning gate：`FPMS-ADDGAP-WAVE0-CONTRACT-FREEZE-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

`FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `frontend/src/modules/documents/pages/DocumentWizard.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-wizard-template-limit.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 DocTemplate.Read。
- Status codes/errors: GET 成功 200；本任务验证不再发送导致 422 的 page_size。
- Response envelope: 沿用现有模板列表响应包络。
- SQLite: N/A（前端只读请求）。
- Simplified Chinese UI: 触及页面，所有新增或变更可见文本必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-wizard-template-limit.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/modules/documents/pages/DocumentWizard.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-wizard-template-limit.spec.ts`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
