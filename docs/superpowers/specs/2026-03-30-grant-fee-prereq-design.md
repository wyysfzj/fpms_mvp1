# GF-PRE 授权费 Workflow Prerequisite 设计说明

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `chained (DB -> BE skeleton)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P2 #15` 当前不能直接进入 grant-fee workflow 本体，因为 repo 中不存在 `T_GrantFeeTask` 承载。`GF-PRE` 的职责不是提前完成 worklist、状态流转或 fee draft linkage，而是先建立稳定 prerequisite：结构化承载、SQLite-safe migration、最小权限命名空间，以及 grant-fee backend 模块骨架。

## Assumptions

- `GF-PRE` 第一轮只处理 prerequisite。
- 字段边界固定为：
  - `id/task_id`
  - `case_id`
  - `type=GRANT`
  - `due_date`
  - `gov_fee_amt`
  - `service_fee_amt`
  - `currency`
  - `client_instruction`
  - `notify_count`
  - `draft_generated`
  - `notice_sent`
  - `is_overdue`
  - `remark`
  - 审计字段
- `client_instruction` 允许值固定为：
  - `NONE`
  - `PAY`
  - `ABANDON`
- 权限骨架固定为：
  - `GrantFeeTask.Read`
  - `GrantFeeTask.Write`
- 第一轮只建立：
  - `T_GrantFeeTask` 承载
  - SQLite-safe migration
  - grant-fee backend 模块骨架
  - 权限命名空间
- 第一轮明确不纳入：
  - worklist/workbench
  - 状态流转动作
  - fee draft linkage
  - bill linkage
  - document/reminder linkage
  - 完整权限矩阵

## Scope

- prerequisite 判定与落地
- 结构化承载
- migration
- backend module skeleton
- permission namespace freeze

## Explicit Non-scope

- workflow page
- state transition engine
- fee draft linkage
- bill linkage
- document/reminder linkage
- 完整权限矩阵

## Exact Model / Field Inventory

### T_GrantFeeTask

- `id/task_id`
- `case_id`
- `type=GRANT`
- `due_date`
- `gov_fee_amt`
- `service_fee_amt`
- `currency`
- `client_instruction`
- `notify_count`
- `draft_generated`
- `notice_sent`
- `is_overdue`
- `remark`
- 审计字段

## Enum / Value Freeze

### client_instruction

- `NONE`
- `PAY`
- `ABANDON`

## Model-layer Impact

- 新增 `T_GrantFeeTask` 承载
- 新增 SQLite-safe migration
- 不复用 `T_AnnuityTask` 作为临时替代

## API / Service Impact

- 第一轮不实现 workflow endpoint
- 只建立 grant-fee backend 模块骨架与后续 story 的稳定落点
- 为后续 `GF-SM / GF-WL / GF-DRAFT` 预留模块边界

## UI / Permission Impact

- 本 story 不实现 workflow 页面
- 冻结权限命名空间：
  - `GrantFeeTask.Read`
  - `GrantFeeTask.Write`

## Cross-module Impact

当前明确不进入：

- `fees` workflow
- `billing`
- `documents`
- `reminders`
- `frontend worklist`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- 本 story 高概率需要 schema/migration，因此是 prerequisite-heavy，而不是 Phase 3 小改

## Risks / Blockers / Prerequisite Tasks

- prerequisite 容易被错误扩成 workflow 本体
- 容易过早加入 detail/billing/document-only 字段
- `AnnuityTask` 只能作为模式参考，不能替代承载

## Exact Closure Slice Candidates

建议冻结为：

`建立 T_GrantFeeTask 的结构化承载、SQLite-safe migration、GrantFeeTask.Read/Write 权限命名空间，以及 grant-fee backend 模块骨架，为后续 GF-SM / GF-WL / GF-DRAFT 提供稳定落点。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
