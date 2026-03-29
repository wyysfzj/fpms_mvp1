# 时限模板关键字段补全设计说明

> Story Shape Classification
> - `shared_file_density`: `high`
> - `prereq_dependency_density`: `high`
> - `be_fe_coupling`: `chained (BE -> FE)`
> - `evidence_cost`: `high`
>
> chosen_runbook: `P0-prereq-heavy-story`

## Problem Statement

当前 `P1 #9` 的缺口不是单纯“任务模板页面少几个字段”，而是 `TaskTemplate`、`task_generation_service`、以及潜在的 `Task` 运行时承载之间存在断层。现有模板只能表达 `add_days / add_months / inner_offset_days / default_worker_role`，无法配置 `deadline_base`、`remind_base`、固定三档提醒偏移、`daily_remind` 与默认监督人，因此新生成任务也无法基于这些规则产出完整的时限与提醒结果。

## Assumptions

- `deadline_base` 的权威位置在 `TaskTemplate` 层。
- `deadline_base` 第一版只要求影响新生成 `Task` 的 deadline 计算，不要求作为实例层独立展示字段。
- `3-level reminders` 固定为三档模板偏移规则，不做动态层级提醒引擎。
- `remind_base` 与 `deadline_base` 独立配置。
- `daily_remind` 第一版定义为模板层布尔开关。
- 当前故事只要求对**新生成**任务生效，不回填或重算已有任务。
- 前端范围仅限现有任务模板管理页面。
- 若运行时提醒结果需要持久化到 `Task`，则该故事天然包含 schema/model prerequisite。

## Scope

- `TaskTemplate` 关键字段补全。
- 模板 CRUD contract 补全。
- `task_generation_service` 读取新字段并对新生成任务生效。
- 任务模板前端配置页补齐字段输入。

## Explicit Non-scope

- 历史 `Task` 回填或重算。
- `TodayReminders`、任务列表、任务详情页展示模板字段。
- reminder execution engine / cron 复杂重构。
- 动态层级提醒配置。
- 每日提醒高级规则（起始日、工作日过滤、频率配置）。
- reminder 专用权限码。

## Template-layer Impact

模板层目标字段冻结为：

- `deadline_base`
- `remind_base`
- `remind_1_offset_days`
- `remind_2_offset_days`
- `remind_3_offset_days`
- `daily_remind`
- `default_supervisor_id`

这些字段都属于模板层权威配置，前端编辑与后端 CRUD 必须保持一致。

## Task-generation Impact

`task_generation_service` 需要根据模板层新增字段：

- 选择 deadline 基准来源
- 选择 remind 基准来源
- 计算三档提醒日期
- 决定新任务是否启用每日提醒
- 使用默认监督人（若该字段纳入执行范围）

这部分是独立于模板 CRUD 的第二个 closure slice，不得被模板字段任务吸收。

## Task-instance Impact

当前 review/spec 明确指向运行时字段缺口：

- `remind1`
- `remind2`
- `remind3`
- `daily_remind_from`
- `daily_remind`

因此只做模板字段和前端表单并不能诚实关闭缺口。若要让“新生成 task 生效”，必须先确认运行时任务是否需要稳定承载这些结果；若需要，则这是 schema/model prerequisite。

## UI / Permission Impact

- 前端仅影响 `TaskTemplateList.vue`。
- 所有新文案保持简体中文。
- 权限沿用：
  - `TaskTemplate.Read`
  - `TaskTemplate.Create`
  - `TaskTemplate.Edit`

## SQLite / Phase Compatibility

- SQLite PoC 本身不是 blocker；新增普通字段与普通 service 逻辑都可兼容。
- 真正的 blocker 在 `Phase 3 / 3.1 / 3.5`：
  - 如果需要新增 `TaskTemplate` / `Task` 字段，则不能在当前无 schema phase 内直接实现。

## Risks / Blockers / Prerequisite Tasks

核心 blocker：

1. `TaskTemplate` 当前缺关键字段。
2. `Task` 当前缺提醒结果字段。
3. `task_generation_service` 当前缺对应业务逻辑。

因此本故事应先拆为 prerequisite：

1. 模型 / schema prerequisite
2. generation logic prerequisite
3. 前端模板表单 prerequisite

## Exact Closure Slice Candidates

理想故事级 closure：

`TaskTemplate` 可配置 `deadline_base / remind_base / remind_1/2/3_offset_days / daily_remind / default_supervisor_id`，且这些配置会对新生成 `Task` 的 deadline / reminder 计算生效；前端模板页面可维护这些字段；不影响已有任务。

但基于当前代码现状，这个 closure 不能在现有 phase 约束下直接完成。

## Final Design Judgment

正式结论：

- `不可直接实现，必须先新增 prerequisite task(s)`

如果当前执行仍受 `Phase 3 / 3.1 / 3.5` 无 schema 约束，则进一步结论：

- `受 Phase / schema / shared-ownership 约束，当前应标记 BLOCKED`
