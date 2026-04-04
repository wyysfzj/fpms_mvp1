# RPT-ANN Success Semantics Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `semantics freeze before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`FPMS SPEC 2.0 9.4.3` 要求 `年费监视项目成功率（监视案件中按时缴费比例）`。当前 repo 已具备：

- `T_AnnuityTask.due_date / year_no / client_instruction / status`
- `T_GovPayment.paid_date / paid_amount / fee_item_id`
- `T_FeeItem.year_no`

但如果不先冻结 authority，后续实现会在以下几种不一致口径之间摇摆：

- 把所有年费任务都计入分母
- 只把客户明确指示 `PAY` 的任务计入分母
- 把 `ABANDON/DEFER` 算失败
- 把没有 `fee_item_id -> year_no` lineage 的手工 `GovPayment` 算成功

因此本 wave 先只冻结 success-rate semantics，不做任何产品实现。

## Assumptions

- `ANNRPT-AMOUNT-01` 已完成 grouped amount residual，不影响 success-rate authority
- success-rate 的“成功”在第一轮只指：
  - 官方按时缴费成功
  - 不等同于客户付款成功
- `CaseReceipt` 不是第一轮 success-rate 的 numerator authority
  - 它属于 client-received 语义，已经由 grouped amount slice 处理

## Scope

- 冻结 denominator（哪些 annuity tasks 进入监视分母）
- 冻结 numerator（哪些 tasks 算按时缴费成功）
- 冻结 `on-time` 判断
- 冻结 manual gov payment / missing lineage rows 的处理
- 判断该 residual 是否能在当前 carrier 下直接进入实现

## Explicit Non-scope

- 不做任何 annuity 产品实现补丁
- 不做 grouped amount 重做
- 不做 chart / export
- 不更新 `RPT-ANN` 或 `#13` close decision

## Current Carrier Evidence

- `backend/app/modules/annuity/models.py`
  - `AnnuityTask.due_date`
  - `AnnuityTask.year_no`
  - `AnnuityTask.client_instruction`
  - `AnnuityTask.status`
  - `GovPayment.paid_date`
  - `GovPayment.paid_amount`
  - `GovPayment.fee_item_id`
- `backend/app/modules/fees/models.py`
  - `FeeItem.year_no`
- `backend/app/modules/annuity/service.py`
  - `register_gov_payment(...)`
  - `add_manual_gov_payment(...)`

## Semantics Decision

### Denominator

- 第一轮 denominator 采用：
  - 所有 `AnnuityTask` rows
  - 且 `client_instruction = "PAY"`
- 以下情况不计入 denominator：
  - `client_instruction = "ABANDON"`
  - `client_instruction = "DEFER"`
  - `client_instruction` 为空或未明确支付

理由：
- spec 的 wording 是“监视案件中按时缴费比例”
- 在当前 carrier 下，最稳定的“进入缴费监视”的明确信号是客户支付指示 `PAY`
- `ABANDON/DEFER` 不属于应按时缴费的成功/失败样本

### Numerator

- 第一轮 numerator 采用：
  - denominator 内的 annuity task
  - 且存在可回投到同案同年度的 `GovPayment`
  - 且 `GovPayment.paid_date <= AnnuityTask.due_date`

### Year Lineage Authority

- `GovPayment` 回投到 annuity task year 的 authority 采用：
  - `GovPayment.fee_item_id -> FeeItem.year_no`
- 若 `GovPayment.fee_item_id` 为空，或无法解析到 `FeeItem.year_no`：
  - 第一轮不计入 numerator
  - 也不用于改变 denominator

理由：
- `GovPayment` 本身没有 `year_no`
- success-rate 是 task-year 级指标，必须有稳定的 year lineage
- 手工历史支付没有稳定 year lineage 时，不能诚实计入“某年度按时缴费成功”

### On-time Rule

- `paid_date <= due_date` 记为按时成功
- `paid_date > due_date` 记为 late-paid，不计入 numerator
- 无 `paid_date` 不计入 numerator

### Status Interaction

- `AnnuityTask.status` 第一轮不作为 denominator 主 authority
- 仅用于防止明显终态污染：
  - `CANCELLED / ABANDONED` 若与 `client_instruction=PAY` 冲突，则以 `client_instruction` 优先，后续实现记录为数据异常容忍
- 第一轮不单独把 `DONE` 视为 success 证据
  - 真正 success 仍要求 `GovPayment.paid_date` lineage

## Implementation Readiness Judgment

- 该 residual 可在当前 carrier 下直接进入实现
- 不需要 schema / migration
- 但实现必须显式排除：
  - 无 `fee_item -> year_no` lineage 的 manual gov payments

## Recommended Next Slice

- `ANNRPT-SUCCESS-01`
- exact closure candidate:
  - 在 `/annuity/tasks` summary 增加：
    - `monitored_task_count`
    - `on_time_paid_count`
    - `late_paid_count`
    - `success_rate`
  - 在 `AnnuityTaskList.vue` 展示这些 success-rate metrics

## Explicitly Deferred

- 按客户 / 国别 / 年度拆分 success-rate
- chart / export
- 把 manual historical payments 补齐 year lineage

## Risks

- 把 `CaseReceipt` 错用为 success numerator
- 把所有 `OPEN` task 自动纳入 denominator
- 把无 `fee_item_id` 的 manual `GovPayment` 误当成 task-year success evidence

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- 但必须先以本语义冻结作为 authority，再进入 `ANNRPT-SUCCESS-01`
