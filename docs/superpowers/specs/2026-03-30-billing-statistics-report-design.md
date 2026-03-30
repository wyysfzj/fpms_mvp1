# RPT-BILL — Billing Statistics Report Design

- Story Shape Classification:
  - `shared_file_density`: `medium`
  - `prereq_dependency_density`: `low`
  - `be_fe_coupling`: `chained (BE -> FE)`
  - `evidence_cost`: `medium`
- `chosen_runbook`: `P0-frontend-heavy-story`

## Problem Statement

当前仓库已有账单列表与坏账汇总，但尚未在 `billing` 模块内形成一个可收敛的第一轮统计报表闭环。`RPT-BILL` 第一轮需要在不改 schema 的前提下，基于既有账单、核销、催款、收款事实数据，在 `BillList.vue` 上闭合 `应收 / 逾期 / 坏账 / 账龄` 的基础统计报表。

## Assumptions

- 页面落点固定为 `frontend/src/modules/billing/pages/BillList.vue`
- 数据口径仅基于已存在账单、核销、催款、收款事实数据
- 第一轮最小筛选集：
  - `client_id`
  - `bill_status`
  - `currency`
  - `date_range`
  - `aging_bucket`
  - `is_overdue`
  - `is_bad_debt`
- 第一轮最小闭环：
  - 筛选
  - summary cards
  - 明细列表

## Scope

- `GET /bills` report/list contract 收敛
- `BillList.vue` 报表筛选、summary cards、明细列表闭环
- 账龄桶、逾期标记、坏账标记的只读展示

## Non-scope

- `PaymentList.vue` 预收/核销统计增强
- 图表、打印、导出
- 潜在应收预测、未来现金流预测
- 独立 `BillingReport.vue`

## Closure

- 在 `billing` 模块中，基于已存在账单、核销、催款、收款事实数据，在 `BillList.vue` 上提供应收 / 逾期 / 坏账 / 账龄的第一轮统计报表闭环，包括筛选、summary cards 和明细列表。
