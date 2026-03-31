# P2 #16 费用综合查询设计说明

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

当前 repo 已分别具备 `payment` 与 `receipt` 的独立查询入口，但缺少一个基于 `payment + receipt` 的统一综合查询层。`P2 #16` 的第一轮职责不是做财务统一分析平台，而是在现有承载之上提供一个 `UNION-like` unified query，包括统一投影、最小筛选集、统一明细列表和专属综合查询页面。

## Assumptions

- 当前权威查询对象只固定为：
  - `payment`
  - `receipt`
- 第一轮结果形态固定为：
  - `一个统一明细列表`
- dual-table query 语义固定为：
  - `payment` 与 `receipt` 各自查询后做 `UNION-like` 统一投影
  - 不做 join-like 成对匹配视图
  - 允许 `payment-only` / `receipt-only` 行
- 第一轮 unified projection 固定为：
  - `record_type`
  - `record_id`
  - `case_id`
  - `biz_no`
  - `party_name`
  - `amount`
  - `currency`
  - `status`
  - `biz_date`
  - `remark`
- 第一轮最小筛选集固定为：
  - `record_type`
  - `case_id`
  - `biz_no`
  - `party_name`
  - `status`
  - `currency`
  - `date_range`
  - `amount_range`
- 第一轮 deferred slices 固定为：
  - `summary cards`
  - `export`
  - `print`
  - `reconciliation semantics`
  - `drill-down`
  - `reporting/dashboard`

## Scope

- unified query service
- unified query API contract
- unified query response schema
- billing 模块专属综合查询页
- billing 前端 api/types、route、menu 落点

## Explicit Non-scope

- `summary cards`
- `export`
- `print`
- `reconciliation semantics`
- `drill-down`
- `reporting/dashboard`
- `bill / fee draft / settlement / refund` 联动查询

## Exact Source Tables / Field Inventory

### Source Objects

- `backend/app/modules/billing/models.py::Payment`
- `backend/app/modules/billing/models.py::CaseReceipt`

### Unified Projection

- `record_type`
  - payment 来源：固定值 `PAYMENT`
  - receipt 来源：固定值 `RECEIPT`
- `record_id`
  - payment 来源：`Payment.id`
  - receipt 来源：`CaseReceipt.id`
- `case_id`
  - payment 来源：从 `PaymentLine.case_id` 聚合出的最小可用案件上下文；无可用案件时允许为空
  - receipt 来源：`CaseReceipt.case_id`
- `biz_no`
  - payment 来源：`Payment.pay_no`
  - receipt 来源：`CaseReceipt.invoice_no`，为空时回退 `CaseReceipt.id`
- `party_name`
  - payment 来源：客户端名称投影
  - receipt 来源：客户端名称投影
- `amount`
  - payment 来源：`Payment.amount`
  - receipt 来源：`CaseReceipt.received_amt`
- `currency`
  - payment 来源：`Payment.currency`
  - receipt 来源：`CaseReceipt.currency`
- `status`
  - payment 来源：`prepayment_status` 投影
  - receipt 来源：`is_arrears` / 收款事实投影出的只读状态字符串
- `biz_date`
  - payment 来源：`Payment.pay_date`
  - receipt 来源：`CaseReceipt.last_receipt_date`
- `remark`
  - payment 来源：`Payment.remark` 或 notes 投影
  - receipt 来源：`CaseReceipt.remark`

## Dual-table Query Semantics

- 查询语义是：
  - `payment` 与 `receipt` 各自按冻结筛选集查询
  - 各自映射为统一投影
  - 在 service 层进行 `UNION-like` 合并与统一排序
- 当前不要求：
  - 基于某个关联键做 join-like 配对
  - payment 与 receipt 的对账匹配视图
  - 未匹配项的补偿解释层

## First-round Result Shape

- 统一明细列表
- 分页
- 统一排序
- 最小筛选区
- 不附带 summary cards

## First-round Filter Definition

- `record_type`
- `case_id`
- `biz_no`
- `party_name`
- `status`
- `currency`
- `date_range`
- `amount_range`

## Deferred Slices Ledger

- `summary cards`
- `export`
- `print`
- `reconciliation semantics`
- `drill-down`
- `reporting/dashboard`

## Model-layer Impact

- 不新增 schema
- 不新增 migration
- 复用现有 `Payment` / `CaseReceipt` / `PaymentLine` 承载

## API / Service Impact

- 在 `backend/app/modules/billing/service.py` 中增加 unified query service
- 在 `backend/app/modules/billing/schemas.py` 中增加 unified projection schema
- 在 `backend/app/modules/billing/api.py` 中增加综合查询 endpoint
- 权限建议：
  - endpoint 使用 `Payment.Read` 与 `CaseReceipt.Read` 双读权限约束

## UI / Permission Impact

- 新增 billing 模块综合查询页面
- 新增 `frontend/src/api/billing.ts` / `billing.types.ts` 中的 unified query client/types
- 新增 billing route 与 menu 落点
- 所有用户可见文案必须使用简体中文

## Cross-module Impact

当前明确不进入：

- `fees`
- `bills`
- `settlement`
- `refund`
- `reports`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- 当前无明显 schema prerequisite
- 本 story 可作为标准 `BE -> FE` 查询条目执行

## Risks / Blockers / Prerequisite Tasks

- 最大风险是把 `UNION-like` query 漂移成对账或 join-like 匹配视图
- 第二个风险是把 bill/draft/reconciliation 字段提前吸入 unified projection
- 第三个风险是把综合查询硬塞进现有 `PaymentList.vue` 或 `CaseReceiptList.vue`
- 当前无单独 prerequisite task 要求

## Exact Closure Slice Candidates

建议冻结为：

`在现有 payment 与 receipt 承载之上，提供一个基于 UNION-like unified projection 的第一轮费用综合查询，包括 unified query contract、统一明细列表、最小筛选集，以及专属综合查询页面。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
