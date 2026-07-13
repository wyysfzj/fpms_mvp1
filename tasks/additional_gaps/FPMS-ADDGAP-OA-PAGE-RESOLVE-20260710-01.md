# FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 2
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

OAReplyPackage 从 DocumentDetail 的 document_id 上下文调用 resolve，并替换为 package_id 路由。

## Explicit Non-Closure

不改变 OA reply checklist/上传业务，不新增文档详情入口。

## Dependencies

- `FPMS-ADDGAP-OA-RESOLVE-API-20260710-01`
- `FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`（shared frontend API 串行前序）

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `frontend/src/api/officialWorkflows.ts`
- `frontend/src/api/officialWorkflows.types.ts`
- `frontend/src/modules/documents/pages/OAReplyPackage.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 消费 OfficialWorkflow.Update。
- Status codes/errors: 消费 POST 200；404/400/409/422 显示简体中文反馈。
- Response envelope: 消费 OaReplyPackageOut。
- SQLite: N/A。
- Simplified Chinese UI: 所有新增/触及可见文本必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-oa-page-resolve.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/officialWorkflows.ts frontend/src/api/officialWorkflows.types.ts frontend/src/modules/documents/pages/OAReplyPackage.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
