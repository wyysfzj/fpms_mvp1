# GF-SM 授权费状态机设计说明

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `backend-only`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`GF-PRE` 已经建立 `T_GrantFeeTask` 承载与 grant-fee backend skeleton，但当前 grant-fee workflow 仍缺少主干状态机、状态流转动作 contract，以及非法转移校验。`GF-SM` 的职责是只关闭 state-machine engine，不吸收 worklist、fee draft linkage 或其他 linkage slices。

## Assumptions

- `GF-SM` 第一轮只处理 backend 状态机与动作 contract。
- 第一轮权威状态集合固定为：
  - `OPEN`
  - `WAITING_CLIENT`
  - `READY_TO_DRAFT`
  - `DRAFT_GENERATED`
  - `DONE`
- 第一轮允许动作固定为：
  - `mark_waiting_client`
  - `record_pay_instruction`
  - `record_abandon_instruction`
  - `mark_draft_generated`
  - `mark_done`
- 第一轮最小转移规则固定为：
  - `OPEN -> WAITING_CLIENT`
  - `WAITING_CLIENT -> READY_TO_DRAFT`
  - `WAITING_CLIENT -> DONE`
  - `READY_TO_DRAFT -> DRAFT_GENERATED`
  - `DRAFT_GENERATED -> DONE`
- 第一轮不支持跨级跳转、任意状态修改、终态回退。
- 第一轮优先落在 backend contract 与 service 规则，不要求前端状态操作页面。

## Scope

- grant-fee 主干状态集合冻结
- grant-fee 状态流转动作 contract
- service 层状态机规则
- 非法状态转移校验

## Explicit Non-scope

- worklist/workbench
- fee draft linkage
- bill linkage
- document/reminder linkage
- dashboard/reporting
- 前端状态操作页面

## Exact State / Action Inventory

### States

- `OPEN`
- `WAITING_CLIENT`
- `READY_TO_DRAFT`
- `DRAFT_GENERATED`
- `DONE`

### Actions

- `mark_waiting_client`
- `record_pay_instruction`
- `record_abandon_instruction`
- `mark_draft_generated`
- `mark_done`

## State Machine Definition

- `mark_waiting_client`: `OPEN -> WAITING_CLIENT`
- `record_pay_instruction`: `WAITING_CLIENT -> READY_TO_DRAFT`
- `record_abandon_instruction`: `WAITING_CLIENT -> DONE`
- `mark_draft_generated`: `READY_TO_DRAFT -> DRAFT_GENERATED`
- `mark_done`: `DRAFT_GENERATED -> DONE`

非法转移必须返回 `400`，未找到任务必须返回 `404`。

## Trigger Definition

- 本 story 不实现 trigger。
- 仅消费 `GF-PRE` 已建立的 carrier。

## First-round Closure Recommendation

建议冻结为：

`在已建立的 T_GrantFeeTask 承载与 grant-fee 模块骨架之上，完成 grant-fee 主干状态机与状态流转动作 contract，包括状态枚举、动作 endpoint、service 规则以及非法转移校验。`

## Deferred Slices Ledger

- `GF-WL`
- `GF-DRAFT`
- `GF-BILL`
- `GF-DOC`
- `GF-RPT`
- 前端状态操作 UI

## Model-layer Impact

- 不新增 schema
- 只在现有 `T_GrantFeeTask` 承载上补状态机语义

## API / Service Impact

- 在 `backend/app/modules/grant_fees/api.py` 中增加动作 endpoint
- 在 `backend/app/modules/grant_fees/service.py` 中增加状态转移规则
- 在 `backend/app/modules/grant_fees/schemas.py` 中增加动作 contract schema

## UI / Permission Impact

- 本 story 不改 frontend
- 权限沿用：
  - `GrantFeeTask.Write`

## Cross-module Impact

当前明确不进入：

- `fees` draft generation
- `billing`
- `documents`
- `reminders`
- `frontend worklist`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- prerequisite 已关闭 schema 问题，因此本 story 可作为 backend-only state-machine story 执行

## Risks / Blockers / Prerequisite Tasks

- 最主要风险是把 `mark_draft_generated` 误做成草单生成逻辑，越界进入 `GF-DRAFT`
- 另一个风险是允许任意状态跳转，破坏可验证状态机
- prerequisite 依赖：
  - `GF-PRE`

## Exact Closure Slice Candidates

建议冻结为：

`在已建立的 T_GrantFeeTask 承载与 grant-fee 模块骨架之上，完成 grant-fee 主干状态机与状态流转动作 contract，包括状态枚举、动作 endpoint、service 规则以及非法转移校验。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
