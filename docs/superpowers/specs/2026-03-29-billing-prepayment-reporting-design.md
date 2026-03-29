# Billing Prepayment Management Reporting Design

## Story Shape Classification

- shared_file_density: `medium`
- prereq_dependency_density: `low`
- be_fe_coupling: `chained (BE -> FE)`
- evidence_cost: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`P1 #7 预收款管理报表` 当前不是“从零开始的预收款模块”，而是要把现有 payment / payment_line / offset 链路补齐成可管理、可筛选、可汇总的预收款报表。仓库中已经存在预收语义基础：`/payments` 返回 `allocated_amt / unapplied_amt / prepayment_status`，`PaymentList.vue` 也已经展示“预收状态”和“未分配金额”。缺口在于它还不是一条完整的管理报表链路，缺少按预收口径筛选、按客户与日期约束查询、以及与当前筛选结果一致的核心汇总。

## Assumptions

- 第一版只基于现有 payment / payment_line / offset 语义，不重构预收款定义。
- 预收款时间口径统一使用 `Payment.pay_date`。
- 第一版状态分类固定为：
  - `UNALLOCATED` = 全部未核销
  - `PARTIALLY_ALLOCATED` = 部分核销
  - `FULLY_ALLOCATED` = 已核销完成
- 第一版报表核心汇总至少包含：
  - `预收款笔数`
  - `预收总额`
  - `已核销金额`
  - `剩余预收余额`
- 第一版前端落点是现有 `PaymentList.vue`，不新建独立页面。
- “客户筛选”第一版以现有 `client_id` 为权威过滤条件；若可安全返回 `client_name`，前端只作为显示增强，不引入新的客户搜索契约。

## Scope

- `GET /payments` 支持预收款管理报表所需的筛选条件。
- `GET /payments` 返回当前筛选结果集的核心汇总字段。
- `PaymentList.vue` 增加预收款筛选区。
- `PaymentList.vue` 增加预收款核心汇总展示。
- `PaymentList.vue` 将列表字段收敛为预收款管理报表最小字段集：
  - 付款编号
  - 客户
  - 收款日期
  - 预收总额
  - 已核销金额
  - 剩余预收余额
  - 预收状态

## Explicit Non-scope

- 不新增独立预收款报表页面。
- 不新增预收款登记/分配/退款等业务动作。
- 不重构 `PaymentLine.BalanceAmt` / `AllocatedAmt` 的业务定义。
- 不支持多时间口径切换。
- 不支持复杂分析维度（案件组、账龄、费用类型矩阵等）。
- 不处理 dashboard 聚合或跨模块首页卡片。
- 不处理 schema / migration 变更。

## Domain Model Impact

- 无新增持久化结构。
- 无 schema prerequisite。
- 仅消费现有：
  - `T_Payment`
  - `T_PaymentLine`
  - `T_Offset`
- 报表口径可基于现有聚合字段计算：
  - 预收总额 = `Payment.amount`
  - 已核销金额 = `sum(PaymentLine.allocated_amt)` 或等价现有聚合
  - 剩余预收余额 = `sum(PaymentLine.balance_amt)`
  - 预收状态 = 现有 `prepayment_status` 推导逻辑

## API / Service / UI / Report Impact

### API / Service

- 扩展 `GET /payments`，增加最小筛选参数：
  - `client_id`
  - `prepayment_status`
  - `pay_date_from`
  - `pay_date_to`
  - `has_unapplied_only`
- 保持现有分页 envelope：
  - `items`
  - `page`
  - `page_size`
  - `total`
- 在顶层增加汇总字段：
  - `prepayment_count`
  - `prepayment_total_amount`
  - `allocated_total_amount`
  - `remaining_prepayment_balance`
- 现有 list item 需要补齐 `client_name`，便于前端列表展示。

### UI

- 修改现有 `PaymentList.vue`，不新增独立页面。
- 增加预收款筛选区：
  - 客户 ID
  - 预收状态
  - 收款日期范围
  - 仅看仍有剩余预收余额
- 增加预收款 summary 卡片。
- 将现有表格列调整为更接近管理报表口径。
- 所有用户可见文案必须为简体中文。

### Report Semantics

- summary 与列表必须基于相同过滤结果集。
- summary 计算口径应基于过滤后的全集，而不是仅当前分页页内数据。

## SQLite / Phase Compatibility Assessment

- 对 SQLite PoC：兼容，无新增方言依赖。
- 对 Phase 3 / 3.1 / 3.5：
  - 兼容。
  - 不需要 schema 变更。
  - 后端工作集中在模块级 `api.py` / `service.py` 的 list/query 逻辑扩展。
- 因此本故事当前结论是：
  - `可在当前约束下拆成可执行原子任务`

## Risks / Blockers / Prerequisite Tasks

### Main Risks

- `/payments` 当前仍在 `api.py` 内直接做较多聚合逻辑，若继续堆入筛选与汇总，文件耦合会上升。
- `frontend/src/api/billing.ts` 与 `frontend/src/api/billing.types.ts` 是 shared ownership 文件，必须串行。
- 若现有 `PaymentList.vue` 上的“回款列表”与“预收款管理报表”信息架构冲突，需要在同页内谨慎布局，不能偷扩 scope 成独立页面。

### Blocker Check

- 当前未发现 schema blocker。
- 当前未发现必须回到 prerequisite planning 的共享模型重构。
- 已发现的共享文件风险可以通过串行 wave 解决，不构成 `BLOCKED`。

## Approaches

### 方案 1：最小报表化补齐（推荐）

- 后端只扩 `GET /payments` 的筛选与 summary。
- 前端只改 `PaymentList.vue`。
- 优点：最符合当前故事名和最小闭环，零 schema 风险。
- 缺点：报表仍依附在回款列表页，不是独立信息架构。

### 方案 2：新建独立预收款报表页

- 新建专门 `/billing/prepayments` 页面和对应 frontend route。
- 优点：信息架构更纯。
- 缺点：明显扩大 scope，需要新页面 wiring 与更多 shared ownership，不符合第一版最小闭环。

### 方案 3：预收款定义重构后再做报表

- 先把预收池、分配、退款等语义抽象成更独立模型，再做查询。
- 优点：长期更完整。
- 缺点：对当前条目完全过度设计。

## Recommended Approach

- 采用 **方案 1：最小报表化补齐**。

## Exact Closure Slice Candidates

- 候选 closure：
  - 现有 `GET /payments` 与 `PaymentList.vue` 形成一条完整的预收款管理报表链路，支持按客户/状态/收款日期/是否仍有余额筛选，返回并展示核心汇总与最小列表字段集。

- 候选 non-closure：
  - 独立预收款报表页面
  - 新的预收款业务动作
  - 预收款定义重构
  - 多时间口径切换
  - 更复杂分析维度

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
