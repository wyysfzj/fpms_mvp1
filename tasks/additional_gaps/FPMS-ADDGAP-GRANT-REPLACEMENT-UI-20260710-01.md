# FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 7
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

Execution-time recheck after discovering the template-read prerequisite: all four classifications
remain unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`; no new source ownership or
backend slice is required.

## Exact Closure Slice

GrantFeeTaskList 提供显式 replacement-notice 动作，录入 reason、request key、confirmed due。

## Explicit Non-Closure

不允许 legacy/superseded task 发起替换，不改变普通状态动作，不修改 backend contract。

## Dependencies

- 40
- 43

## Remaining Follow-Up Task IDs

- 46

## Allowed Files

- `frontend/src/api/grantFees.ts`
- `frontend/src/api/grantFees.types.ts`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime Contracts

- Permission: replacement 动作可见性消费 `GrantFeeTask.Write` 与 `Doc.Create`；backend endpoint
  仍只执行这两个写权限。模板选择器另以 `DocTemplate.Read` 作为只读可用前置：权限未加载或
  缺少该权限时 fail closed，动作保持可见但禁用，并显示“缺少文书模板读取权限，无法选择更正通知模板”。
- Template source: 复用既有 `getDocTemplates({ direction: 'IN', enabled: true, page_size: 100 })`，
  仅在本页面过滤 `catalog_status=EXECUTABLE` 且 `execution_behavior=GRANT_NOTICE`；不得修改
  documents API/types、不得手工录入或硬编码 template ID。模板加载失败时禁止提交并给出简体中文提示。
- Status codes/errors: 消费 POST 200/400/404/409/422。
- Response envelope: 消费 GrantFeeTaskReplacementNoticeOut。
- SQLite: N/A。
- Simplified Chinese UI: 对话框、字段、确认、错误和成功反馈必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-replacement-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/grantFees.ts frontend/src/api/grantFees.types.ts frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/**`

## Done Definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
