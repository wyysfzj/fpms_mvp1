# RPT-ANN Success-Rate Implementation Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `resolved by prior semantics freeze`
- `be_fe_coupling`: `shared summary contract across API client and AnnuityTaskList page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`ANNRPT-SUCCESS-SPEC-01` 已冻结 `RPT-ANN` success-rate semantics，但当前 `GET /annuity/tasks` summary 仍未返回：

- `monitored_task_count`
- `on_time_paid_count`
- `late_paid_count`
- `success_rate`

因此下一步应只实现这组年费监视成功率指标，并在现有 `AnnuityTaskList.vue` 上展示，不新建报表页，也不吸收按客户/国别/年度拆分成功率。

## Assumptions

- `ANNRPT-SUCCESS-SPEC-01` 的 success-rate semantics 为当前权威
- grouped amount slice 已完成，不需重做
- 当前实现只扩展现有 `GET /annuity/tasks` report summary
- 不新增 schema / migration

## Scope

- 后端为 `GET /annuity/tasks` summary 新增 success-rate metrics
- 前端 `annuity` API client/types 接入新 summary 字段
- `AnnuityTaskList.vue` 展示 success-rate 相关指标
- 保持现有年费任务列表/筛选/金额汇总行为不回归

## Explicit Non-scope

- 不做按客户/国家/年度拆分 success-rate
- 不做图表 / 导出
- 不新建 `AnnuityReport.vue`
- 不修改 grouped amount semantics

## Metric Semantics

- `monitored_task_count`
  - count `AnnuityTask.client_instruction == "PAY"`
- `on_time_paid_count`
  - denominator 内任务中，存在可回投到同案同年度且 `paid_date <= due_date` 的 `GovPayment`
- `late_paid_count`
  - denominator 内任务中，不属于 `on_time_paid_count`
  - 且存在可回投到同案同年度且 `paid_date > due_date` 的 `GovPayment`
- `success_rate`
  - `on_time_paid_count / monitored_task_count`
  - denominator 为 `0` 时返回 `null`
- manual `GovPayment`
  - 若无 `fee_item_id -> FeeItem.year_no` lineage，不计入 success numerator / late counter

## Shared-file / Ownership Analysis

Serialized backend ownership:

- `backend/app/modules/annuity/service.py`
- `backend/app/modules/annuity/schemas.py`
- `backend/tests/test_annuity_report.py`

Serialized frontend ownership:

- `frontend/src/api/annuity.ts`
- `frontend/src/api/annuity.types.ts`
- `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`

## Batch Recommendation

- `ANNRPT-SUCCESS-BE-01`
  - extend summary contract and backend metric computation
- `ANNRPT-SUCCESS-FE-01`
  - render the new metrics on `AnnuityTaskList.vue`
- `ANNRPT-SUCCESS-QA-01`
  - audit evidence and exact closure

## Exact Closure Slice

- Implement success-rate summary metrics on the existing annuity report page and summary contract, nothing more
