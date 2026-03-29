# 案卷缺失字段补全设计说明

> Story Shape Classification
> - `shared_file_density`: `high`
> - `prereq_dependency_density`: `high`
> - `be_fe_coupling`: `chained (DB -> BE -> FE)`
> - `evidence_cost`: `high`
>
> chosen_runbook: `P0-prereq-heavy-story`

## Problem Statement

当前 `P1 #10` 的缺口不是“页面少几个输入框”，而是 `Case` 主档、CRUD contract、以及 create/edit/detail 页面之间同时存在结构化字段断层。现有实现无法完整承载 spec/review 要求的 15 个关键字段，导致案卷基本信息、规格页数、控制标记、国别/地址、授权编号等信息无法在系统内以结构化方式保存和维护。

## Assumptions

- 本故事冻结的字段清单为 15 个：
  - `recv_date`
  - `draw_pages`
  - `claim_pages`
  - `manuscript_words`
  - `discount_rate`
  - `no_power`
  - `no_prio_text`
  - `require_hk`
  - `from_country`
  - `to_country`
  - `doc_address_id`
  - `bill_address_id`
  - `issue_date`
  - `cert_no`
  - `first_annuity_year`
- 这些字段统一属于 `Case` 顶层结构化字段。
- 第一版只要求这些字段在 `create / update / detail` 生效。
- 旧案卷允许手工补录这些字段，但不做历史数据批量回填。
- 前端仅覆盖 `CaseCreate.vue`、`CaseEdit.vue`、`CaseDetail.vue`。
- `CaseList`、搜索、筛选、导入导出、downstream 联动全部不纳入本故事。
- 当前 repo 没有独立 `T_Country` 主数据，因此 `from_country / to_country` 第一版采用 `country_code` 风格字符串字段，而不是新增外键主表依赖。
- `doc_address_id / bill_address_id` 第一版允许引用现有 `t_client_address.id`。

## Scope

- `Case` 模型字段承载。
- `CaseCreate / CaseUpdateFull / CaseDetail` contract 补齐。
- create/update service 校验补齐。
- `CaseCreate.vue`、`CaseEdit.vue` 补齐字段输入。
- `CaseDetail.vue` 补齐字段展示。

## Explicit Non-scope

- `CaseList.vue`
- list/filter/search/export/import
- 历史数据批量回填或自动补值
- 依赖这些字段的 downstream 自动联动
- `client_ref`
- `description`

## Exact Field Inventory

### 日期类
- `recv_date`
- `issue_date`

### 页面/数量类
- `draw_pages`
- `claim_pages`
- `manuscript_words`

### 费率/控制标记类
- `discount_rate`
- `no_power`
- `no_prio_text`
- `require_hk`

### 国别/地址类
- `from_country`
- `to_country`
- `doc_address_id`
- `bill_address_id`

### 授权/年费编号类
- `cert_no`
- `first_annuity_year`

## Model-layer Impact

- `recv_date`、`first_annuity_year` 已存在于模型，但 contract / FE 暴露不完整。
- 其余字段大多属于真实模型缺口，需要新的持久化承载。
- `doc_address_id / bill_address_id` 需要与现有 `ClientAddress` 做引用校验。
- `from_country / to_country` 需要先按最小字符串字段落地，避免引入新的国家主数据 prerequisite。

## API / Service Impact

后端至少需要同步补齐：
- `CaseCreate`
- `CaseUpdateFull`
- `CaseDetail`
- `_serialize_case(...)`
- `create_case(...)`
- `update_case_full(...)`

最小校验预期：
- 数量/页数字段非负整数
- `discount_rate` 范围 `0..1`
- 外向 / 国家阶段案件的 `to_country` 条件性校验
- 地址 ID 存在性与归属客户校验
- 授权相关状态下 `issue_date / cert_no / first_annuity_year` 的基础一致性校验

## UI / Permission Impact

- 前端仅影响：
  - `CaseCreate.vue`
  - `CaseEdit.vue`
  - `CaseDetail.vue`
- 所有用户可见文案必须为简体中文。
- 权限沿用现有：
  - `Case.Create`
  - `Case.Update`
  - `Case.Read`

## SQLite / Phase Compatibility

- SQLite 本身不是 blocker；这些字段可用普通 `String / Integer / Numeric / Boolean / Date` 实现。
- 真正的 blocker 在 `Phase 3 / 3.1 / 3.5`：
  - 如果要诚实完成本故事，必须新增模型字段和 migration，因此不能被视为无 schema 小改。

## Risks / Blockers / Prerequisite Tasks

主要风险：
1. 这条故事天然包含 schema/model prerequisite。
2. 地址字段会触达 `ClientAddress` 的共享 contract。
3. 国别字段若强制 FK 到国家主表，会引入新的 prerequisite；因此第一版必须保持为字符串代码。
4. 如果把列表/搜索/导入导出吸进来，closure 会立即失控。

## Exact Closure Slice Candidates

理想故事级 closure：

`在 Case 上结构化承载 15 个缺失字段，并使这些字段在 create / update / detail 三个面向可维护、可见、可手工补录。`

## Final Design Judgment

正式结论：

- `不可直接实现，必须先新增 prerequisite task(s)`

若仍受无 schema 的 `Phase 3 / 3.1 / 3.5` 约束，则进一步结论：

- `受 Phase / schema / shared-ownership 约束，当前应标记 BLOCKED`
