# P2 #11 批件递交（US-CM-05）设计说明

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `chained (DB -> BE -> FE)`
- `evidence_cost`: `high`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前仓库缺少 `US-CM-05 / FR-CM-07` 要求的“案件递交批处理”能力。系统虽然已有 `Case.Status`、`recv_date`、`has_exam_request` 以及 `NOT_FILED / WAITING_RECEIPT` 状态枚举，但没有一个专用 workflow 来按条件筛出尚未递交案件、批量设置递交日期、批量执行状态迁移，并在需要时同步更新 `has_exam_request`。

## Assumptions

- 这是一个 **批量动作 workflow**，不是单案编辑能力。
- 第一版只关闭 `Case` 侧的批量筛选与状态迁移闭环。
- `submitted_date` 作为 `Case` 顶层结构化字段持久化。
- `apply_exam_now` 是动作输入，不单独持久化；其结果落到 `Case.has_exam_request`。
- 第一版不新增子状态，不新增批次主表。
- 第一版不实现：
  - 递交清单文档生成
  - 自动申请费时限任务生成
  - timeline / documents / billing / report 联动

## Scope

- `Case` 新增 `submitted_date`
- 专用批量筛选 contract
- 专用批量执行递交动作 contract
- 前端“案件递交”页面
- 批量勾选与执行
- `Status: NOT_FILED -> WAITING_RECEIPT`
- `has_exam_request` 的批量更新规则

## Explicit Non-scope

- 递交清单文档生成
- `T_Document / T_DocAttachment` 联动
- 自动申请费时限任务生成
- timeline 展示
- 历史批量补录/回填
- 通用列表/导出/报表增强

## Exact Field Inventory

### 1. 筛选字段

- `case_type`
- `flow_dir`
- `status`
- `recv_date_from`
- `recv_date_to`
- `client_id`
- `primary_agent_id`
- `patent_category`

### 2. 列表字段

- `id`
- `case_no`
- `title_cn`
- `client_name`
- `case_type`
- `patent_category`
- `flow_dir`
- `recv_date`
- `status`
- `has_exam_request`

### 3. 批处理参数

- `selected_case_ids`
- `submitted_date`
- `apply_exam_now`
- `generate_list`

## Exact Workflow Definition

1. 用户进入“案件递交”页面。
2. 使用最小筛选集查询，默认 `status = NOT_FILED`。
3. 系统返回候选案件列表。
4. 用户勾选一批案件。
5. 用户填写：
   - `submitted_date`
   - `apply_exam_now`
   - `generate_list`（第一版不生效）
6. 用户执行“批件递交”。
7. 系统逐案校验后批量更新：
   - `submitted_date`
   - `status: NOT_FILED -> WAITING_RECEIPT`
   - 当 `apply_exam_now=true` 时更新 `has_exam_request = true`
8. 返回批处理结果摘要。

## State Transition / Action Boundaries

- 起点：`NOT_FILED`
- 终点：`WAITING_RECEIPT`
- 第一版不支持：
  - 撤回递交
  - 重提
  - 失败重试
  - 批次撤销

## Model-layer Impact

- 当前最小模型影响是 `Case.submitted_date`
- 不新增批次主表
- 不新增动作日志表

## API / Service Impact

- 新增批件递交专用查询 contract
- 新增批件递交专用执行 contract
- service 负责：
  - V-BF-01：至少勾选一案
  - V-BF-02：`submitted_date >= recv_date`
  - 状态迁移与 `has_exam_request` 更新

## UI / Permission Impact

- 新增专用页面，不复用 `CaseList.vue` 直接改造成批处理页
- 所有用户可见文案使用简体中文
- 权限建议：
  - 查询：`Case.Read`
  - 批件递交动作：`Case.BatchFiling`

## Downstream Impact

第一版明确不进入：

- `documents`
- `tasks`
- `billing`
- `reminders`
- `timeline`
- `report`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：可行
- 若 `submitted_date` 需要结构化持久化，则该故事不是当前无 schema Phase 可直接完成的小改

## Risks / Blockers / Prerequisite Tasks

- 若 `submitted_date` 缺失，则需要 schema/model prerequisite
- cases API / service / FE 页面共享文件密度高，必须串行 wave
- 若后续想把 `generate_list` 拉回 scope，将直接扩展到 documents shared ownership

## Exact Closure Slice Candidates

建议冻结为：

`提供一个 Cases 批件递交 workflow：按最小筛选集检索 NOT_FILED 案件，勾选后批量设置 submitted_date 和 apply_exam_now，并将案件状态批量更新为 WAITING_RECEIPT，同时更新 has_exam_request。`

## Final Design Judgment

- `不可直接实现，必须先新增 prerequisite task(s)`
- 如果继续受 `Phase 3 / 3.1 / 3.5` 无 schema 约束，则：
  - `受 Phase / schema / shared-ownership 约束，当前应标记 BLOCKED`
