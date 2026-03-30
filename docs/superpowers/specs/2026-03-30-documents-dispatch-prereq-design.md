# P2 #12 邮寄 / 交接单 / 信封（FR-WD-08~10）设计说明

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `chained (DB -> BE -> FE)`
- `evidence_cost`: `high`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前仓库缺少 `FR-WD-08~10` 要求的邮寄登记、交接单、信封打印能力。现有 `documents` 模块只有基础 CRUD、模板、附件和详情页面，没有：

- 对去文批量登记 `OutgoingRegNo / ForwardDate` 的 action
- `T_DocDispatch / T_DocDispatchLine` 的结构化承载
- 面向交接单与信封打印的最小 contract 与 UI

因此，这条故事的最小可执行解释不是“documents 再补几个字段”，而是补齐一个最小可用的 dispatch workflow。

## Assumptions

- 本故事由 3 个相关但独立的动作组成：
  - `A. 邮寄信息登记`
  - `B. 文件交接单`
  - `C. 信封打印`
- `A` 落在现有 `Document` 上，新增结构化字段：
  - `outgoing_reg_no`
  - `forward_date`
- `B` 必须新增：
  - `T_DocDispatch`
  - `T_DocDispatchLine`
- `C` 第一版不新增持久化表，只做即时打印数据生成。
- 第一版只要求：
  - `A` 批量 action 可用
  - `B` 生成与详情查看可用
  - `C` 单文档即时预览/打印数据可用
- 第一版不做：
  - `DocumentList` 通用列表增强
  - timeline
  - 导出报表
  - 附件/模板自动联动
  - 复杂物流跟踪

## Scope

- `Document.outgoing_reg_no / forward_date`
- `T_DocDispatch / T_DocDispatchLine`
- 邮寄登记 action
- 交接单生成与详情 query
- 信封打印数据生成 query
- 最小前端流程页与打印预览页

## Explicit Non-scope

- `DocumentList` 通用增强
- timeline
- report/export
- attachment/template 自动联动
- 历史数据批量回填
- 快递/物流跟踪体系

## Exact Object / Field Inventory

### A. 邮寄信息登记

- 作用对象：现有 `Document`
- 第一版结构化字段：
  - `outgoing_reg_no`
  - `forward_date`
- 第一版动作输入：
  - `selected_document_ids`
  - `outgoing_reg_no`
  - `forward_date`

### B. 文件交接单

- 主表：`T_DocDispatch`
- 第一版字段：
  - `id`
  - `client_id`
  - `dispatch_date`
  - `remark`
- 明细表：`T_DocDispatchLine`
- 第一版字段：
  - `dispatch_id`
  - `document_id`

### C. 信封打印

- 第一版不做持久化表
- 即时打印数据：
  - `document_id`
  - `recipient_name`
  - `recipient_address`
  - `address_source`

## Exact Workflow Definition

1. 用户进入 documents 下的邮寄/交接流程入口。
2. 选择一批目标去文。
3. 执行 `A. 邮寄信息登记`，批量写入：
   - `outgoing_reg_no`
   - `forward_date`
4. 执行 `B. 文件交接单`，按选中文档生成：
   - `T_DocDispatch`
   - `T_DocDispatchLine`
5. 查看交接单详情。
6. 对单文档执行 `C. 信封打印`，按地址优先级生成即时打印数据并预览。

## State / Action Boundaries

- `A/B/C` 是三个动作
- 它们可以相关，但不是一个必须同事务完成的 mega action
- 第一版不要求：
  - 交接单打印归档
  - 邮寄签收闭环
  - 物流状态追踪

## Model-layer Impact

- `Document` 新增：
  - `outgoing_reg_no`
  - `forward_date`
- 新增：
  - `T_DocDispatch`
  - `T_DocDispatchLine`

## API / Service Impact

- 新增邮寄登记批量 action
- 新增交接单生成 action
- 新增交接单详情 query
- 新增信封打印数据 query
- service 负责：
  - 批量文档合法性校验
  - 交接单客户归属约束
  - 信封地址优先级解析

## UI / Permission Impact

- 新增 documents 下的专用流程入口
- 所有用户可见文案使用简体中文
- 权限建议：
  - 查询/详情：`Document.Read`
  - 邮寄登记/交接单生成：`Document.Dispatch`

## Downstream Impact

第一版明确不进入：

- `templates`
- `attachments`
- `print log`
- `timeline`
- `report`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：可行
- 若按本设计实现，明确包含表/字段 prerequisite，因此不是当前无 schema Phase 可直接完成的小改

## Risks / Blockers / Prerequisite Tasks

- `FR-WD-09` 明确要求 `T_DocDispatch / T_DocDispatchLine`
- `FR-WD-10` 依赖地址优先级解析，若地址 contract 不完整会暴露额外 prerequisite
- `documents` 模块模型、schemas、api、service、前端页面都是 shared ownership，高密度串行

## Exact Closure Slice Candidates

建议冻结为：

`提供一个最小可用的 documents dispatch workflow：支持对现有去文批量登记 outgoing_reg_no / forward_date，生成并查看 T_DocDispatch / T_DocDispatchLine 交接单，以及按地址优先级生成单文档信封打印数据。`

## Final Design Judgment

- `不可直接实现，必须先新增 prerequisite task(s)`
- 如果继续受 `Phase 3 / 3.1 / 3.5` 无 schema 约束，则：
  - `受 Phase / schema / shared-ownership 约束，当前应标记 BLOCKED`
