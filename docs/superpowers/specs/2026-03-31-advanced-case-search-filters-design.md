# P2 #18 高级案件查询增强设计说明（Replanned）

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `chained (DB -> BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前 repo 已具备现有案件统一列表、基础案件筛选和案件详情中的 `patent_no` 承载，但缺少 review 指定的三项高级案件查询增强能力：`applicant_id`、`patent_no`、`fee_status`。在执行前的仓库核查中发现，`applicant_id` 当前无法按已批准语义实现，因为 case applicant 承载还没有到 applicant masterdata 的稳定查询路径。因此 `P2 #18` 不能再被视为一个直接可执行的单一 query enhancement story，而必须先拆成 prerequisite + follow-up query story。

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
  - 对现有案件承载中的编号字段做大小写不敏感模糊匹配
  - 允许基础空格/连接符归一化
- `fee_status` 语义固定为：
  - 基于案件关联的 `fee draft / bill / payment` 记录
  - 做最小聚合派生状态过滤
  - 仅作为案件级筛选条件，不做 drill-down
- 原始第一轮最小闭环曾冻结为：
  - 在现有 case query 上新增：
    - `applicant_id`
    - `patent_no`
    - `fee_status`
  - 其他既有筛选不变
  - 列表投影不变
- 执行前重新判定后，当前实际可执行边界变为：
  - `CASEFILTER-PRE`：仅建立 case applicant -> applicant masterdata 的稳定查询路径
  - 后续 `CASEFILTER-QRY`：在 prerequisite 完成后再补 `applicant_id` + `patent_no` + `fee_status`
- 第一轮 deferred slices 固定为：
  - `summary cards`
  - `export`
  - `reporting/dashboard`
  - `fee drill-down`
  - `applicant selector 深度联动`

## Scope

- 识别并冻结 `applicant_id` prerequisite
- 识别并冻结后续 query story 边界
- 为 prerequisite 与 follow-up query story 提供 decomposition ledger

## Explicit Non-scope

- `summary cards`
- `export`
- `reporting/dashboard`
- `fee drill-down`
- `applicant selector 深度联动`
- 在本轮 replanning 中直接实现任何产品代码
- 绕过 prerequisite 继续强做 `applicant_id`

## Exact Source Tables / Field Inventory

### Source Objects

- `backend/app/modules/cases/models.py::Case`
- `backend/app/modules/cases/models.py::T_CaseApplicant`
- `backend/app/modules/masterdata/applicants/models.py::Applicant`
- `backend/app/modules/fees/models.py::FeeDraft`
- `backend/app/modules/billing/models.py::Bill`
- `backend/app/modules/billing/models.py::Payment`

### Existing List Projection Impact

- 后续 query story 仍应保持现有 `CaseListItem` 投影不变
- 当前 replanning 不变更列表投影

## `applicant_id` Filter Definition

- 过滤对象是 applicant masterdata `id`
- 匹配语义是精确匹配
- 一案多申请人时，任一申请人命中即返回案件
- 当前不引入：
  - applicant active-only 语义
  - case applicant 行级 id 过滤
  - applicant selector 深度联动
- 执行前新发现的 blocker：
  - 当前 `T_CaseApplicant` 没有 `applicant_id`
  - 当前也没有到 applicant masterdata 的稳定映射列或查询桥
  - 因此该 filter 不能在现有 schema 下按批准语义诚实实现

## `patent_no` Filter Definition

- 来源于现有案件承载中的编号字段
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
  - `Bill`
  - `Payment`
- 第一轮语义是案件级最小聚合派生状态
- 过滤行为是：
  - 只决定案件是否命中
  - 不返回财务 drill-down 结果
- 当前不要求：
  - 财务明细联查
  - 账务时间线
  - dashboard/reporting 聚合

## Replanning Result

### CASEFILTER-PRE

- 目标：为 case applicant 建立到 applicant masterdata 的稳定查询路径
- 当前高概率属于：
  - schema / migration prerequisite
  - carrier/contract prerequisite
- 非闭包：
  - 不做 case list UI
  - 不做 `patent_no`
  - 不做 `fee_status`

### CASEFILTER-QRY

- 目标：在 prerequisite 关闭后，完成 `applicant_id` + `patent_no` + `fee_status` 的 query enhancement
- 当前是 follow-up story，不应在 prerequisite 未完成前直接执行

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

- `CASEFILTER-PRE` 是明确的 schema-bearing prerequisite
- 需要在 `T_CaseApplicant` 上新增可空 `applicant_id`
- 需要 SQLite-safe migration、索引与到 `Applicant.id` 的稳定引用
- 在 prerequisite 关闭前，后续 `applicant_id` query enhancement 不应开启

## API / Service Impact

- 对于 `CASEFILTER-PRE`：
  - 先落在 data carrier / mapping 层
  - 再落在 case full create/update 的 payload 与持久化路径
  - 当前不扩现有 `GET /cases`
- 对于后续 `CASEFILTER-QRY`：
  - 在 prerequisite 关闭后再扩 `backend/app/modules/cases/service.py`
  - 在 prerequisite 关闭后再扩 `backend/app/modules/cases/api.py`
  - 在 prerequisite 关闭后再扩 `frontend/src/api/cases.types.ts`
  - 在 prerequisite 关闭后再扩 `frontend/src/api/cases.ts`

## UI / Permission Impact

- `CASEFILTER-PRE` 当前不应触达前端
- 后续 `CASEFILTER-QRY` 仍应仅增强现有 [CaseList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseList.vue)
- 权限继续沿用：
  - `Case.Read`
- 所有用户可见文案必须使用简体中文

## Cross-module Impact

当前明确不进入：

- billing drill-down
- fee reporting
- export
- dashboard
- applicant selector 深度联动

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- `patent_no` 与 `fee_status` 单独看没有明显 schema prerequisite
- 但 `applicant_id` 已发现明确 prerequisite：
  - 当前 case applicant 承载无法连接 applicant masterdata
- 因此 `P2 #18` 作为整体应改判为 prerequisite-heavy

## Risks / Blockers / Prerequisite Tasks

- 已确认 blocker：
  - `T_CaseApplicant` 当前不持有 `applicant_id`
  - 现有 repo 中不存在 case applicant -> applicant masterdata 的稳定查询路径
- 第二个风险是 `fee_status` 漂移成财务 drill-down 语义
- 第三个风险是把现有案件列表增强误做成新页面或报表页
- 必须新增 prerequisite task：
  - `CASEFILTER-PRE`

## Exact Closure Slice Candidates

建议改冻结为两段：

- `CASEFILTER-PRE`: 建立 case applicant -> applicant masterdata 的稳定查询路径
- `CASEFILTER-QRY`: 在 prerequisite 完成后，再完成 applicant_id、patent_no、fee_status 三个新增筛选的 query enhancement

## Final Design Judgment

- `不可直接实现，必须先新增 prerequisite task(s)`
