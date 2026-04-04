# RPT-FEE Balance Semantics Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `semantics freeze before cross-module implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-FEE` 在 grouped aggregate 与 agent-income slice 后，剩余最容易被误做假的能力是 “billed / received / unpaid”。当前 repo 同时存在：

- `T_FeeDraft / T_FeeItem` 的草单统计 carrier
- `T_Bill / T_BillItem` 的应收账单 carrier
- `T_Offset` 的冲销明细
- `T_CaseReceipt` 的个案实收汇总

如果不先冻结 fee report 的 balance authority，后续实现很容易在：

- 以 `FeeDraft.total_*` 直接当 billed
- 以 `Bill.amount - Bill.balance` 当 received
- 以 `CaseReceipt.received_amt` 当全量 received

之间随意切换，导致费用统计与 billing/receipt 口径不一致。

## Assumptions

- `FPMS SPEC 2.0 9.4.2` 的 residual 语义包括：
  - 按时间段统计各种费用类型总额
  - 统计未收金额（Balance 合计）
- `RPT-FEE` 当前 authority 仍是：
  - `GET /fees/drafts`
  - `FeeDraftList.vue`
- 关闭标准继续固定为：
  - 只有真实产品行为存在，才允许该 residual capability 计入 closure
- 本 wave 只冻结 billed / received / unpaid semantics，不做任何产品实现

## Scope

- 冻结 `billed / received / unpaid` 的 source-of-truth
- 冻结 `Bill / Offset / CaseReceipt` 的优先级与职责边界
- 判断该 residual 当前是否可直接进入实现
- 推荐下一条 implementation slice

## Explicit Non-scope

- 不做任何 fees/billing 产品实现补丁
- 不做 agent-income 扩展
- 不做趋势统计
- 不做图表 / 导出
- 不更新 `RPT-FEE` 或 `#13` close decision

## Current Carrier Evidence

- `backend/app/modules/billing/models.py`
  - `Bill.amount`
  - `Bill.balance`
  - `Bill.status`
  - `Bill.direction`
  - `BillItem.bill_id`
  - `BillItem.draft_id`
  - `Offset.offset_amt`
  - `CaseReceipt.receivable_amt`
  - `CaseReceipt.received_amt`
- `backend/app/modules/billing/service.py`
  - `create_offset(...)`
  - `_allocate_offset_to_receipts(...)`
  - 现有语义：
    - 冲销时更新 `Bill.balance / status`
    - 同步按比例更新 `CaseReceipt.received_amt`
- `backend/app/modules/billing/schemas.py`
  - `BillListReportSummaryResponse`
  - `CaseReceiptResponse`
- `backend/app/modules/fees/service.py`
  - 当前 fee report summary 仍未实现 billed / received / unpaid residual

## Semantics Decision

### Billed source-of-truth

- `billed` 的 authority 采用：
  - `T_Bill / T_BillItem`
- 第一轮 billed 统计只纳入：
  - `Bill.direction == "AR"`
  - 且能通过 `BillItem.draft_id` 追溯到 fee-draft lineage 的账单项
- `T_FeeDraft.total_*` 只保留 draft-stage 统计语义：
  - 不能直接充当 billed totals

### Received source-of-truth

- `received` 的 authority 采用：
  - `T_Offset` 驱动的 `Bill.amount - Bill.balance`
- `T_CaseReceipt.received_amt` 只作为 case-view 投影与核对 carrier
  - 不作为第一轮 fee report received totals 的主 authority
- 原因：
  - `CaseReceipt` 在 `_allocate_offset_to_receipts(...)` 中是按 bill item 分摊后的派生结果
  - 对 fee-report 的 billed/received/unpaid 口径，账单余额是更直接的 AR source-of-truth

### Unpaid / balance source-of-truth

- `unpaid` 的 authority 采用：
  - `Bill.balance`
- 第一轮 unpaid metric 定义为：
  - 所有 in-scope AR bill rows 当前 `Balance` 的合计
- `bad_debt` 账单如仍有 `Balance > 0`：
  - 继续计入 unpaid / balance totals
  - 不在本 slice 中拆分出坏账专属视图

### Status semantics

- billed:
  - 账单创建后即进入 billed universe
- received:
  - 对单张 Bill，`received_amount = amount - balance`
- unpaid:
  - 对单张 Bill，`unpaid_amount = balance`
- partially received:
  - `0 < balance < amount`
- fully received:
  - `balance == 0`
- unpaid-only filter:
  - `balance > 0`

### Grouping lineage

- fee report 的 billed / received / unpaid 汇总必须按 `BillItem.draft_id -> FeeDraft` 回投到 fee-report authority
- 对无法追溯到 `draft_id` 的手工账单项：
  - 第一轮不纳入 `RPT-FEE` residual slice
  - 作为后续 deferred cross-finance issue

### Amount family

- 第一轮 billed / received / unpaid 先按总额语义落地：
  - `billed_amount`
  - `received_amount`
  - `unpaid_balance_amount`
- 不在本 slice 中继续拆：
  - `service billed`
  - `gov billed`
  - `misc billed`
  - per-fee-type balance buckets

## Implementation Readiness Judgment

- `billed / received / unpaid` 在当前 carrier 下可直接进入实现
- 不需要新增 schema / migration
- 但这条 residual 必须单独作为 cross-module implementation slice，不能与 trend reporting 混做

## Recommended Next Slice

- `FEERPT-BALANCE-01`
- exact closure candidate:
  - extend fee-report summary with:
    - `billed_amount`
    - `received_amount`
    - `unpaid_balance_amount`
    - `partially_received_bill_count`
  - source semantics:
    - `Bill / BillItem` authority
    - `Bill.amount - Bill.balance` for received
    - `Bill.balance` for unpaid
  - render a narrow billed/received/unpaid summary block on `FeeDraftList.vue`

## Explicitly Deferred

- time trend reporting
- service/gov/misc billed-received-balance breakdown
- chart / export
- hand-made bill rows without `draft_id` lineage
- bad-debt dedicated fee-report slice

## Risks

- 把 `FeeDraft.total_*` 错当成 billed totals
- 把 `CaseReceipt.received_amt` 错当成第一权威 received source
- 把所有手工账单项也自动吸进 fee report
- 在同一条 story 里混入趋势统计

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- 但必须先以本语义冻结作为 authority，再进入 `FEERPT-BALANCE-01`
