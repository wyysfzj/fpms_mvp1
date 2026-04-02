# P2 #15 授权费管理 Workflow Decomposition 设计说明

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared multi-lane workflow`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P2 #15 授权费管理` 不是单一 story。review 直接指出 `T_GrantFeeTask model + full workflow` 缺失，而当前 repo 中既没有 `T_GrantFeeTask` 结构化承载，也没有 grant-fee 专属 endpoint、worklist 或 UI。第一步不应直接尝试实现“full workflow”，而应先冻结 workflow inventory、最小状态机、trigger source、第一轮 closure，以及哪些 linkage slices 必须 deferred。

## Assumptions

- `P2 #15` 先视为 workflow program
- `full workflow` 权威组成固定为：
  - `T_GrantFeeTask` 承载
  - auto-generation trigger
  - worklist / workbench
  - detail/edit
  - state transitions
  - fee draft / bill linkage
  - document / reminder linkage
- 第一轮最小状态机固定为：
  - `OPEN`
  - `WAITING_CLIENT`
  - `READY_TO_DRAFT`
  - `DRAFT_GENERATED`
  - `DONE`
- 第一轮 trigger 固定为：
  - 授权通知/授权事实写入后自动生成
  - 生成逻辑幂等
  - 不做历史回填 / 重建 / 重算
- 若 repo 中不存在 `T_GrantFeeTask` 承载，则必须先拆为 schema/migration prerequisite
- 第一轮最小闭环固定为：
  - `model`
  - `auto-generated task list/worklist`
  - `state transition`
  - `fee draft linkage`
- 第一轮 deferred slices 固定为：
  - `bill linkage`
  - `document/reminder linkage`
  - `detail/edit`
  - `dashboard/reporting`
  - `search/filter 扩展`
  - `import/export`

## Scope

- 判断 `P2 #15` 是否是 prerequisite + 多 story workflow item
- 冻结 workflow inventory、状态机、trigger、第一轮 closure
- 给出 decomposition ledger 与优先顺序

## Explicit Non-scope

- 一次做完整 `full workflow`
- 直接吸收所有 linkage slices
- 把 deferred slices 模糊写成“剩余流程后续补齐”

## Workflow Decomposition Recommendation

建议拆为：

1. `GF-PRE`
2. `GF-SM`
3. `GF-WL`
4. `GF-DRAFT`

明确 deferred：

- `GF-DETAIL`
- `GF-BILL`
- `GF-DOC`
- `GF-RPT`

## Exact Model / Field Inventory

`T_GrantFeeTask` 最小字段按 spec 冻结为：

- `TaskID`
- `CaseID`
- `Type=GRANT`
- `DueDate`
- `GovFeeAmt`
- `ServiceFeeAmt`
- `Currency`
- `ClientInstruction`
- `NotifyCount`
- `DraftGenerated`
- `NoticeSent`
- `IsOverdue`
- `Remark`
- 审计字段

## Exact State / Action Inventory

### States

- `OPEN`
- `WAITING_CLIENT`
- `READY_TO_DRAFT`
- `DRAFT_GENERATED`
- `DONE`

### Actions

- trigger create
- set client instruction
- mark ready to draft
- generate draft
- mark done

当前不纳入：

- revoke
- cancel
- skip
- close

## State Machine Definition

- `OPEN` -> `WAITING_CLIENT`
  - 条件：任务生成后进入待客户指示主状态
- `WAITING_CLIENT` -> `READY_TO_DRAFT`
  - 条件：客户指示为 `PAY`
- `WAITING_CLIENT` -> `DONE`
  - 条件：客户指示为 `ABANDON`
- `READY_TO_DRAFT` -> `DRAFT_GENERATED`
  - 条件：授权费草单生成成功且幂等校验通过
- `DRAFT_GENERATED` -> `DONE`
  - 条件：本轮只做最小完成标记，不延伸到账单链路

## Trigger Definition

- 来源：授权通知/授权事实写入
- 行为：自动生成 `T_GrantFeeTask`
- 要求：幂等
- 当前不纳入：
  - 历史回填
  - 重建工具
  - 重算工具

## First-round Closure Recommendation

不建议直接把第一轮 closure 做成“full workflow”。更合理的是：

- 先完成 `GF-PRE`
- 然后基于 `GF-PRE` 再推进：
  - `GF-SM`
  - `GF-WL`
  - `GF-DRAFT`

## Deferred Slices Ledger

- `GF-BILL`: bill linkage
- `GF-DOC`: document/reminder linkage
- `GF-DETAIL`: detail/edit
- `GF-RPT`: dashboard/reporting
- `GF-SEARCH`: search/filter 扩展
- `GF-IO`: import/export

## Model-layer Impact

- 当前 repo 没有 `T_GrantFeeTask`
- 高概率需要新增模型/表/migration
- `annuity` 只能作为模式参考，不能作为承载替代

## API / Service Impact

- 未来至少涉及：
  - grant fee task generation
  - grant fee task list/worklist
  - state transition actions
  - draft generation action
- 当前均不存在 grant-fee 专属 contract

## UI / Permission Impact

- 未来至少涉及：
  - grant-fee worklist/workbench 页面
  - batch action UI
- 当前权限命名空间也需要对应 grant-fee workflow 明确化

## Cross-module Impact

会影响但当前不建议一次吸收的模块：

- `fees`
- `billing`
- `documents`
- `reminders`
- `tasks`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：理论上可行
- 但如果要新增 `T_GrantFeeTask`，就天然是 schema/migration prerequisite
- 因而整体不应被视为 Phase 3 小改

## Risks / Blockers / Prerequisite Tasks

- `T_GrantFeeTask` 承载不存在
- 容易错误复用 `T_AnnuityTask`
- linkage slices 容易被误吸收进第一轮 closure
- 状态机/trigger 若不先冻结，后续返工概率高

## Exact Closure Slice Candidates

### GF-PRE
- `T_GrantFeeTask` 承载
- schema necessity / migration
- 最小权限与模块骨架

### GF-SM
- 最小状态机
- state transition actions
- client instruction / overdue / draft-generated 主干规则

### GF-WL
- grant-fee worklist / workbench
- list contract
- 主干状态展示

### GF-DRAFT
- fee draft linkage
- 满足条件时生成 `GRANT_FEE` 草单
- 幂等保护

## Final Design Judgment

- `不可直接实现，必须先新增 prerequisite task(s)`
