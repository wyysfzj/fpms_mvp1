# P2 #18 高级案件查询增强设计说明（Post-Prerequisite）

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`P2 #18` 的 prerequisite 已经关闭：`T_CaseApplicant` 现在具备了到 applicant masterdata 的稳定查询路径。因此这条工作不再是 prerequisite-heavy program，而是一个标准的 case query enhancement story：在现有 `GET /cases` 与现有案件列表页上，补齐 `applicant_id`、`patent_no`、`fee_status` 三个高级筛选。

## Assumptions

- 当前权威新增过滤对象只固定为：
  - `applicant_id`
  - `patent_no`
  - `fee_status`
- 第一轮结果形态固定为：
  - `仍然落在现有案件统一列表上做筛选增强`
- `applicant_id` 语义固定为：
  - applicant masterdata `id`
  - 精确匹配
  - 一案多申请人时任一命中即可返回案件
- `patent_no` 语义固定为：
  - 对现有案件承载中的 `patent_no` 做大小写不敏感模糊匹配
  - 允许基础空格/连接符归一化
- `fee_status` 语义固定为：
  - 基于案件关联的 `FeeDraft / Bill / PaymentLine`
  - 做最小聚合派生状态过滤
  - 第一轮只冻结三档：
    - `DRAFT`
    - `BILLED`
    - `PAID`
  - 派生优先级：
    - `PAID`：存在关联 `PaymentLine`
    - `BILLED`：无 `PaymentLine`，但存在关联 `BillItem`
    - `DRAFT`：无 `PaymentLine` / `BillItem`，但存在关联 `FeeDraft`
- 第一轮最小闭环固定为：
  - 在现有 case query 上新增：
    - `applicant_id`
    - `patent_no`
    - `fee_status`
  - 其他既有筛选不变
  - 列表投影不变
- 第一轮 deferred slices 固定为：
  - `summary cards`
  - `export`
  - `reporting/dashboard`
  - `fee drill-down`
  - `applicant selector 深度联动`

## Scope

- 在现有 `GET /cases` 上新增三个 query filters
- 在现有 `CaseList.vue` 上新增三个筛选控件
- 在现有 `cases.ts / cases.types.ts` 上补齐 query contract

## Explicit Non-scope

- 新建高级搜索页
- `summary cards`
- `export`
- `reporting/dashboard`
- `fee drill-down`
- `applicant selector 深度联动`
- 变更现有列表投影

## Exact Source Tables / Field Inventory

### Source Objects

- `backend/app/modules/cases/models.py::Case`
- `backend/app/modules/cases/models.py::T_CaseApplicant`
- `backend/app/modules/masterdata/applicants/models.py::Applicant`
- `backend/app/modules/fees/models.py::FeeDraft`
- `backend/app/modules/billing/models.py::BillItem`
- `backend/app/modules/billing/models.py::PaymentLine`

### Existing List Projection Impact

- 继续复用当前 `CaseListItem`
- 不新增列表列
- 只增强 query contract 和 FE filter controls

## `applicant_id` Filter Definition

- 过滤对象是 applicant masterdata `id`
- 匹配语义是精确匹配
- 一案多申请人时，任一申请人命中即返回案件
- 当前不引入：
  - applicant active-only 语义
  - case applicant 行级 id 过滤
  - applicant selector 深度联动

## `patent_no` Filter Definition

- 来源于 `Case.patent_no`
- 匹配语义是大小写不敏感模糊匹配
- 第一轮允许：
  - 首尾空白裁剪
  - 基础空格/连接符归一化
- 当前不要求：
  - 精确匹配模式切换
  - 更复杂的编号标准化规则

## `fee_status` Filter Definition

- 来源于案件关联的：
  - `FeeDraft`
  - `BillItem`
  - `PaymentLine`
- 第一轮只提供三档过滤值：
  - `DRAFT`
  - `BILLED`
  - `PAID`
- 派生规则：
  - `PAID`：案件存在任意 `PaymentLine.case_id = Case.id`
  - `BILLED`：案件不存在 `PaymentLine`，但存在任意 `BillItem.case_id = Case.id`
  - `DRAFT`：案件不存在 `PaymentLine` / `BillItem`，但存在任意 `FeeDraft.case_id = Case.id`
- 第一轮不引入：
  - bill/payment 细分状态过滤
  - 财务 drill-down
  - 多值组合逻辑

## First-round Result Shape

- 现有案件统一列表
- 现有列表页筛选面板增强
- 不新建页面
- 不新增结果卡片

## First-round Filter Definition

- 在现有 case list/query 的基础上新增：
  - `applicant_id`
  - `patent_no`
  - `fee_status`
- 其他现有 filters 保持不变

## Deferred Slices Ledger

- `summary cards`
- `export`
- `reporting/dashboard`
- `fee drill-down`
- `applicant selector 深度联动`

## Model-layer Impact

- 本轮不需要新的 schema / migration
- prerequisite 已提供：
  - `T_CaseApplicant.applicant_id`
- 本轮只消耗现有 carrier

## API / Service Impact

- 在 `backend/app/modules/cases/api.py` 扩 query params
- 在 `backend/app/modules/cases/service.py` 扩 filter / join / fee-status 派生逻辑
- 保持现有 response envelope 与 `CaseListItem` 不变

## UI / Permission Impact

- 增强现有 [CaseList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseList.vue)
- 扩 `frontend/src/api/cases.types.ts`
- 扩 `frontend/src/api/cases.ts`
- 权限继续沿用：
  - `Case.Read`
- 所有用户可见文案必须使用简体中文

## Cross-module Impact

本轮读取但不进入：

- applicant masterdata 编辑链路
- fee drill-down
- export
- dashboard

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- 当前没有新的 schema prerequisite
- `applicant_id / patent_no / fee_status` 都可在现有 ORM 上完成
- 当前可作为标准 `BE -> FE` query enhancement story 执行

## Risks / Blockers / Prerequisite Tasks

- 最大风险是 `fee_status` 漂移成财务 drill-down 语义
- 第二个风险是前端 scope creep，把筛选增强扩成新页面或报表页
- prerequisite 已关闭：
  - `CASEFILTER-DB-01`
  - `CASEFILTER-PRE-01`
  - `CASEFILTER-QA-01`
- 当前没有新的 prerequisite blocker

## Exact Closure Slice Candidates

- `CASEFILTER-BE-01`：在现有 `GET /cases` 上新增 `applicant_id / patent_no / fee_status` backend query contract 与 service filter logic
- `CASEFILTER-FE-01`：在现有 `CaseList.vue` 与 `cases.ts/cases.types.ts` 上新增三项筛选 UI 与 query wiring
- `CASEFILTER-QA-01`：完成 query enhancement 的 gates、evidence 与 close audit

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
