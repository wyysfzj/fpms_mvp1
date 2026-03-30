# GF-WL 授权费 Worklist 设计说明

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`GF-PRE` 已建立 `T_GrantFeeTask` 承载，`GF-SM` 已完成主干状态机，但 grant-fee workflow 仍缺少真正的 worklist/list/query 与 grant-fee 专属 workbench 页面。`GF-WL` 的职责是只关闭列表承载与页面查看能力，不吸收 fee draft linkage、账单/文书联动或 detail/edit。

## Assumptions

- `GF-WL` 第一轮只处理 worklist/list/query 与 grant-fee 专属页面承载。
- 第一轮最小列表字段固定为：
  - `task_id`
  - `case_id`
  - `status`
  - `due_date`
  - `client_instruction`
  - `gov_fee_amt`
  - `service_fee_amt`
  - `currency`
  - `draft_generated`
  - `notice_sent`
  - `is_overdue`
- 第一轮最小筛选集固定为：
  - `status`
  - `client_instruction`
  - `draft_generated`
  - `is_overdue`
  - `case_id`
  - `date_range`
- 第一轮页面只提供：
  - 查看
  - 筛选
  - 后续动作入口壳
- 第一轮不承诺：
  - 完整批量动作
  - 嵌入式编辑
  - workflow 动作执行

## Scope

- grant-fee task list/query endpoint
- list response schema
- 最小筛选与分页
- grant-fee 专属 worklist 页面
- route 与 frontend api/types 最小承载

## Explicit Non-scope

- fee draft linkage
- bill linkage
- document/reminder linkage
- dashboard/reporting
- detail/edit
- 前端真实状态动作执行

## Exact Field / Filter Inventory

### List Fields

- `task_id`
- `case_id`
- `status`
- `due_date`
- `client_instruction`
- `gov_fee_amt`
- `service_fee_amt`
- `currency`
- `draft_generated`
- `notice_sent`
- `is_overdue`

### Filters

- `status`
- `client_instruction`
- `draft_generated`
- `is_overdue`
- `case_id`
- `date_range`

## First-round Closure Recommendation

建议冻结为：

`在已建立的 T_GrantFeeTask 承载与 GF-SM 状态机 contract 之上，完成 grant-fee task 的第一轮 worklist/list/query 与专属 workbench 页面承载，包括最小筛选、分页列表、状态只读展示和后续动作入口壳。`

## Deferred Slices Ledger

- `GF-DRAFT`
- `GF-BILL`
- `GF-DOC`
- `GF-DETAIL`
- `GF-RPT`
- 前端状态动作执行

## Model-layer Impact

- 不新增 schema
- 复用现有 `T_GrantFeeTask` 承载

## API / Service Impact

- 在 `backend/app/modules/grant_fees/api.py` 中增加 list/query endpoint
- 在 `backend/app/modules/grant_fees/schemas.py` 中增加 list response schema
- 在 `backend/app/modules/grant_fees/service.py` 中增加 list/query service

## UI / Permission Impact

- 新增 grant-fee 专属 worklist 页面
- 新增前端 grant-fee api/types
- 新增 grant-fee route
- 权限沿用：
  - `GrantFeeTask.Read`

## Cross-module Impact

当前明确不进入：

- `fees` draft generation
- `billing`
- `documents`
- `reminders`
- workflow detail/edit

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- prerequisite 与状态机已关闭 schema 问题，因此本 story 可作为标准 `BE -> FE` worklist story 执行

## Risks / Blockers / Prerequisite Tasks

- 风险在于把 list endpoint 做成半个 workflow console，越界进入 `GF-SM` 或 `GF-DRAFT`
- 另一个风险是错误复用通用 tasks/fees 页面，导致 shared shell 改造膨胀
- prerequisite 依赖：
  - `GF-PRE`
  - `GF-SM`

## Exact Closure Slice Candidates

建议冻结为：

`在已建立的 T_GrantFeeTask 承载与 GF-SM 状态机 contract 之上，完成 grant-fee task 的第一轮 worklist/list/query 与专属 workbench 页面承载，包括最小筛选、分页列表、状态只读展示和后续动作入口壳。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
