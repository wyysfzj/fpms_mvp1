# Grant Fee Post-draft Workflow Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend wiring on top of existing backend state action`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`GF-RESIDUAL-SPEC-01` 已经明确 `#15` 的第一条 residual follow-up 应是 post-draft workflow rule。当前 backend 已存在 `PUT /grant-fee-tasks/{task_id}/state` 和 `mark_done` action，状态机测试也已经覆盖 `DRAFT_GENERATED -> DONE`。真正缺的是可到达的产品行为：`GrantFeeTaskList.vue` 仍只支持单行生成草单，没有任何 post-draft 完成入口，因此用户无法把已生成草单的授权费任务在前端真实完成。

## Assumptions

- backend authority 已存在且继续有效：
  - `mark_done` remains manual-only
  - no downstream bill/document proof is required in this slice
- in-scope status path fixed to:
  - `DRAFT_GENERATED -> DONE`
- current worklist page authority remains:
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Scope

- frontend API layer:
  - add one state-action client for grant-fee tasks
- frontend page:
  - expose one row-level `标记完成` action for `DRAFT_GENERATED`
  - refresh row/list state after success
  - keep all user-facing text in Simplified Chinese
- qa:
  - verify exact post-draft closure and evidence

## Explicit Non-scope

- no backend code changes
- no bill linkage
- no document/reminder linkage
- no detail/edit drawer or page
- no batch action shell

## Exact Closure Slice

- make the existing post-draft `mark_done` state action reachable from the current grant-fee worklist page for rows in `DRAFT_GENERATED`

## Shared-file Decisions

- serialized frontend ownership:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Verification

- `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `cd frontend && npm run typecheck`

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
