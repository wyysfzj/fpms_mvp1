# RPT-ANN Residual Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `residual decomposition after implemented first-round slice`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-ANN` 当前不能再诚实地描述为“未实现”，但也不能直接判定为 full-spec 闭合。现有仓库已经具备第一轮年费统计报表产品切片：`GET /annuity/tasks` 提供 report-style summary，`AnnuityTaskList.vue` 提供筛选、summary cards、分布统计和明细列表。但对照 `FPMS SPEC 2.0` `9.4.3`，当前 family 仍缺少：

- 按国别 / 客户 / 年份的年费应缴 / 实缴统计
- 基于 `T_GovPayment` 与 `T_CaseReceipt` 的支付 / 收款视角
- 年费监视项目成功率语义

因此下一步不应重做已完成的 first-round annuity task report，而应先冻结 residual map。

## Assumptions

- `ANNRPT-BE-01` / `ANNRPT-FE-01` / `ANNRPT-QA-01` 的 first-round closure 继续有效
- `RPT-ANN` 的 first-round 权威产品切片固定为：
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
- `PayList.vue`、`PayListDetail.vue`、`GovPaymentCreate.vue` 是相关年费支付能力，但不自动等于 `RPT-ANN` full-family closure authority
- 关闭标准仍固定为：
  - 只有真实产品行为存在，才允许新增 residual capability 计入 closure

## Scope

- 对 `RPT-ANN` 做 strict residual capability map
- 明确 first-round already closed slice
- 明确相对 `FPMS SPEC 2.0 9.4.3` 仍缺的 grouped dimensions / metrics / source semantics
- 推荐一个最小 residual implementation slice

## Explicit Non-scope

- 不重做 `ANNRPT-BE-01`
- 不重做 `ANNRPT-FE-01`
- 不做任何年费统计产品实现补丁
- 不做图表 / 导出 / 预测分析

## Current Implemented Slice

### Existing product evidence

- `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `frontend/src/api/annuity.ts`
- `frontend/src/api/annuity.types.ts`
- `artifacts/ANNRPT-BE-01/**`
- `artifacts/ANNRPT-FE-01/**`
- `artifacts/ANNRPT-QA-01/**`

### Already closed under first-round interpretation

- approved report filters:
  - `client_id`
  - `case_id`
  - `country`
  - `annuity_year`
  - `task_status`
  - `payment_status` as minimal/no-op-compatible field
  - `date_range`
  - `notice_status`
- summary cards:
  - `total_task_count`
  - `open_task_count`
  - `done_task_count`
  - `overdue_task_count`
- distributions:
  - `status_counts`
  - `year_counts`
- existing detail list retained as the detail portion of the report

## Residual Spec Gap vs `FPMS SPEC 2.0`

### Spec-required examples not yet closed

- 按国别 / 客户 / 年份统计年费应缴 / 实缴情况
- 年费监视项目成功率（监视案件中按时缴费比例）

### Residual dimensions not yet represented as summary output

- `Country` grouped payment statistics
- `Client` grouped payment statistics
- `Year` grouped payable / paid / received amounts

### Residual source semantics not yet closed

- 当前 first-round 主要以 `T_AnnuityTask` 为 carrier
- spec `9.4.3` 明确推荐主数据来源：
  - `T_AnnuityTask`
  - `T_GovPayment`
  - `T_CaseReceipt`
- 因此当前 family 仍缺：
  - 年费应缴金额 authority
  - 官方实缴金额 authority
  - 客户实收金额 authority
  - “成功率” 的分子 / 分母 / 是否按时口径

### Residual metrics not yet represented as summary output

- grouped payable totals
- grouped official paid totals
- grouped client received totals
- monitoring success rate

## Residual Decomposition Recommendation

### Residual bucket A — grouped annuity payable / paid summaries

- by client totals
- by country totals
- by year totals

### Residual bucket B — monitoring success-rate semantics

- numerator / denominator
- on-time definition
- abandoned / terminated inclusion rules

### Residual bucket C — payment-status truth semantics

- relationship between:
  - `AnnuityTask.status`
  - `GovPayment.status / paid_date / paid_amount`
  - `CaseReceipt.received_amt`

## Recommended First Residual Slice

- `ANNRPT-AMOUNT-SPEC-01`
- exact closure candidate:
  - freeze `payable / official-paid / client-received` source semantics
  - decide whether grouped client/country/year amount summaries can directly enter implementation

### Why this is recommended first

- It directly addresses the main spec gap in `9.4.3`
- It is narrower and less ambiguous than “success rate”
- It avoids mixing grouped financial amounts and monitoring-success semantics into one first residual slice

## Residuals Explicitly Deferred

- monitoring success-rate implementation
- chart / export
- predictive payment forecasting
- cross-page pay-list analytics shell

## SQLite / Phase Compatibility Assessment

- This residual mapping story is doc-only and compatible
- The recommended first residual slice appears achievable without schema change
- If later success-rate semantics require new state derivation beyond current carriers, that must be assessed as a separate follow-up story

## Risks / Blockers

- Treating `AnnuityTaskList.vue` status/year summary as proof that `RPT-ANN` already matches spec `9.4.3`
- Treating `PayList` or `GovPayment` operational pages as automatic proof of annuity-report closure
- Folding grouped payment summaries and success-rate semantics into one next slice

## Exact Closure Slice Candidates

### Preferred

- `ANNRPT-RESIDUAL-01`
  - freeze residual annuity-report map and first residual implementation recommendation

### Explicit non-closure

- no product implementation
- no re-close of first-round `ANNRPT-*`
- no chart/export/success-rate implementation

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task should be a doc-only residual mapping story before any new annuity-report implementation slice.
