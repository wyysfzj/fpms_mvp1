# GF-DRAFT 授权费草单生成设计说明

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`GF-PRE` 已建立 carrier，`GF-SM` 已建立状态机，`GF-WL` 已建立 worklist，但授权费 workflow 仍缺少真正的 `GrantFeeTask -> FeeDraft` 草单生成链路。`GF-DRAFT` 的职责是只关闭 fee-draft linkage，不吸收 bill/document linkage、detail/edit 或复杂操作台能力。

## Assumptions

- `GF-DRAFT` 第一轮只处理 `GrantFeeTask -> FeeDraft` 的授权费草单生成链路。
- 第一轮生成前提固定为：
  - task 当前投影状态必须是 `READY_TO_DRAFT`
  - `draft_generated = false`
  - task 必须具备有效 `case_id`
  - `currency` 必须存在
- 第一轮金额规则固定为：
  - 允许 `gov_fee_amt + service_fee_amt = 0`
  - 零金额 task 也可以生成草单
- 第一轮生成结果回写固定为：
  - 创建 `FeeDraft`
  - 创建最小必要 `FeeItem`
  - 将 task 标记 `draft_generated = true`
  - 通过现有状态投影进入 `DRAFT_GENERATED`
- 第一轮前端只提供最小触发入口。

## Scope

- grant-fee generate-draft backend action
- 幂等保护
- 最小 `FeeDraft` / `FeeItem` 创建
- task `draft_generated` 回写
- 最小前端触发入口

## Explicit Non-scope

- bill linkage
- document/reminder linkage
- detail/edit
- 复杂批量选择器
- 失败重试 UI
- dashboard/reporting

## Exact Precondition / Result Inventory

### Preconditions

- `status == READY_TO_DRAFT`
- `draft_generated == false`
- valid `case_id`
- non-empty `currency`

### Result Writes

- create `FeeDraft`
- create minimal `FeeItem`
- set `draft_generated = true`
- state projection becomes `DRAFT_GENERATED`

## First-round Closure Recommendation

建议冻结为：

`在已建立的 T_GrantFeeTask 承载、GF-SM 状态机与 GF-WL 页面入口壳之上，完成 GrantFeeTask -> FeeDraft 的第一轮授权费草单生成链路，包括生成前提校验、幂等保护、最小 FeeDraft/FeeItem 创建、task draft_generated 回写，以及最小前端触发入口。`

## Deferred Slices Ledger

- `GF-BILL`
- `GF-DOC`
- `GF-DETAIL`
- 复杂批量选择器
- 失败重试 UI
- `GF-RPT`

## Model-layer Impact

- 不新增 schema
- 复用现有 `T_GrantFeeTask`、`FeeDraft`、`FeeItem`

## API / Service Impact

- 在 `backend/app/modules/grant_fees/api.py` 中增加 generate-draft action
- 在 `backend/app/modules/grant_fees/service.py` 中增加 linkage service
- 在 `backend/app/modules/grant_fees/schemas.py` 中增加 generate result contract
- 可能读写 `backend/app/modules/fees/models.py` 中现有实体，但不改 schema

## UI / Permission Impact

- 在 grant-fee worklist 页面启用最小“草单联动”触发入口
- 沿用 `GrantFeeTask.Write`

## Cross-module Impact

当前明确不进入：

- `billing`
- `documents`
- `reminders`
- workflow detail/edit

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- prerequisite 已关闭 schema 问题，因此本 story 可作为标准 `BE -> FE` fee-linkage story 执行

## Risks / Blockers / Prerequisite Tasks

- 最大风险是把 generate action 扩成 bill/document linkage
- 另一个风险是幂等不足，导致重复草单
- prerequisite 依赖：
  - `GF-PRE`
  - `GF-SM`
  - `GF-WL`

## Exact Closure Slice Candidates

建议冻结为：

`在已建立的 T_GrantFeeTask 承载、GF-SM 状态机与 GF-WL 页面入口壳之上，完成 GrantFeeTask -> FeeDraft 的第一轮授权费草单生成链路，包括生成前提校验、幂等保护、最小 FeeDraft/FeeItem 创建、task draft_generated 回写，以及最小前端触发入口。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
