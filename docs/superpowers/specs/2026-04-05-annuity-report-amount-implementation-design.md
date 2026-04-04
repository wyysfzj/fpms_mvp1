# 2026-04-05 Annuity Report Amount Implementation Design

- Story Shape Classification
  - `shared_file_density`: medium
  - `prereq_dependency_density`: medium
  - `be_fe_coupling`: medium
  - `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Problem Statement

`RPT-ANN` 已完成第一轮任务统计，但相对 `FPMS SPEC 2.0 9.4.3` 仍缺按客户 / 国家 / 年度查看年费应缴、官费实缴、客户实收的 grouped amount reporting。`ANNRPT-AMOUNT-SPEC-01` 已冻结 source-of-truth 与 grouping semantics，本轮只把这些 grouped amount summary 接入现有 `/annuity/tasks` 报表与 `AnnuityTaskList.vue`。

## Scope

- 后端在 `/annuity/tasks` summary 增加：
  - `client_amounts`
  - `country_amounts`
  - `year_amounts`
- 每组字段固定为：
  - `payable_amount`
  - `official_paid_amount`
  - `client_received_amount`
  - `task_count`
- 前端在现有年费任务列表页展示三组 grouped amount summary

## Non-scope

- `success-rate`
- 图表 / 导出 / 新页面
- 新 schema / migration
- 修改既有任务列表分页或筛选语义

## Atomic Batch

1. `ANNRPT-AMOUNT-BE-01`
   - exact closure slice: extend annuity report summary contract and aggregation logic with grouped `client_amounts / country_amounts / year_amounts`
   - explicit non-closure: no frontend rendering, no success-rate, no chart/export
2. `ANNRPT-AMOUNT-FE-01`
   - exact closure slice: render grouped amount summaries on `AnnuityTaskList.vue` using backend summary contract
   - explicit non-closure: no backend aggregation logic, no success-rate, no chart/export
3. `ANNRPT-AMOUNT-QA-01`
   - exact closure slice: audit the exact grouped amount slice and evidence
   - explicit non-closure: no product-code changes
