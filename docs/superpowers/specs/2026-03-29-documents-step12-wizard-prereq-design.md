# Documents Step1-2 Wizard Prerequisite Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `BE-first`
- `evidence_cost`: `medium`
- `chosen_runbook`: `P0-prereq-heavy-story`

## Problem Statement

`P1 #8` 原计划假设 Step 2 最小字段集可以在现有 `T_Document` contract 上承载，但实现 `DOCWIZ-BE-01` 后确认，现有 documents 模型与 schema 只能稳定承载 `title / doc_date / ref_no / extra_data / reply_to_id / need_reply`。已批准的 Step 2 字段 `NeedNotifyAgent / InternalDocNo / Summary / Remark / 基础扩展字段` 没有对应的稳定持久化契约，继续推进 FE 向导会导致 closure slice 漂移。

## Design Judgment

- 对原 `P1 #8 Step1-2 向导` 故事的正式结论：
  - `不可直接实现，必须先新增 prerequisite task(s)`
- 如果当前执行被限定在无 schema 的 `Phase 3 / 3.1 / 3.5`：
  - `受 Phase / schema / shared-ownership 约束，当前应标记 BLOCKED`

## Required Prerequisites

### Prerequisite A: Documents field contract freeze

需要先冻结 Step 2 最小字段集的权威承载方式，至少覆盖：

- `NeedNotifyAgent`
- `InternalDocNo`
- `Summary`
- `Remark`
- 模板基础扩展字段

必须明确这些字段分别落在哪一层：

- `T_Document` 结构化字段
- `extra_data` 中的约定键
- 纯前端临时字段（如被明确排除）

### Prerequisite B: Wizard batch contract revision

`DOCWIZ-BE-01` 当前 batch endpoint 只支持现有 contract 能稳定承载的字段。若 Step 2 仍要保留更丰富字段，需要先修订 batch request/response 契约，再让 FE Step 2 按冻结后的字段集实现。

## Recommended Direction

推荐优先收窄而不是直接扩 schema：

- 方案 1：把 Step 2 最小字段集收窄到当前模型可承载字段
- 方案 2：若业务坚持 `NeedNotifyAgent / Summary / Remark / InternalDocNo` 必须属于 Step 2，则新增 prerequisite story，先补 documents model / schema / API contract

当前更安全的做法是先让人类确认二选一，再重新规划 `P1 #8`。

## Exact Blocked Boundary

当前可确认已完成：

- `DOCWIZ-BE-01` 的批量创建 contract

当前不能继续实现：

- `DOCWIZ-FE-SHELL-01`
- `DOCWIZ-FE-STEP1-01`
- `DOCWIZ-FE-STEP2-01`

因为这些前端任务的 closure slice 依赖 Step 2 字段集冻结，而这个前提目前不存在。
