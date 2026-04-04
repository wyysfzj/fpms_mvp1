# RPT-ANN Amount Semantics Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `semantics freeze before grouped amount implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-ANN` 在 residual mapping 后，最容易被误做假的能力是“按国别/客户/年份统计年费应缴/实缴情况”。当前 repo 同时存在：

- `T_AnnuityTask` 的年度应缴 carrier
- `T_GovPayment` 的官方实缴 carrier
- `T_CaseReceipt` 的客户实收 carrier

如果不先冻结年费金额统计的 source-of-truth，后续实现很容易在：

- 直接把 `PayList.total_amount` 当官方实缴
- 把 `AnnuityTask.gov_fee_amt + service_fee_amt` 当客户实收
- 把 `CaseReceipt` 和 `GovPayment` 混成单一“实缴”

之间随意切换，导致年费报表口径不一致。

## Assumptions

- `FPMS SPEC 2.0 9.4.3` 的 residual 语义包括：
  - 按国别 / 客户 / 年份统计年费应缴 / 实缴情况
- `RPT-ANN` 当前 authority 仍是：
  - `GET /annuity/tasks`
  - `AnnuityTaskList.vue`
- 本 wave 只冻结 grouped amount semantics，不做任何产品实现
- `success-rate` 继续 deferred，不在本 wave 中吸收

## Scope

- 冻结 `payable_amount` 的 authority
- 冻结 `official_paid_amount` 的 authority
- 冻结 `client_received_amount` 的 authority
- 冻结 `client / country / year` 三个维度的 grouping lineage
- 判断该 residual 当前是否可直接进入实现
- 推荐下一条 implementation slice

## Explicit Non-scope

- 不做任何 annuity 产品实现补丁
- 不做 success-rate semantics
- 不做图表 / 导出
- 不更新 `RPT-ANN` 或 `#13` close decision

## Current Carrier Evidence

- `backend/app/modules/annuity/models.py`
  - `AnnuityTask.year_no`
  - `AnnuityTask.client_id`
  - `AnnuityTask.gov_fee_amt`
  - `AnnuityTask.service_fee_amt`
  - `GovPayment.case_id`
  - `GovPayment.fee_item_id`
  - `GovPayment.paid_amount`
  - `GovPayment.paid_date`
- `backend/app/modules/billing/models.py`
  - `CaseReceipt.case_id`
  - `CaseReceipt.year_no`
  - `CaseReceipt.receivable_amt`
  - `CaseReceipt.received_amt`
- `backend/app/modules/annuity/service.py`
  - `list_annuity_tasks_report(...)`
  - `mark_pay_list_paid(...)`
  - gov payment persistence helpers
- `backend/app/modules/billing/service.py`
  - `create_case_receipt(...)`
  - case receipt list/get carriers

## Semantics Decision

### Payable source-of-truth

- `payable_amount` authority 采用：
  - `T_AnnuityTask.gov_fee_amt + T_AnnuityTask.service_fee_amt`
- 该值表示某年费任务在任务层面的应缴金额
- 第一轮 grouped amount reporting 以任务行为最小粒度，不要求必须已经生成 pay list 或账单

### Official paid source-of-truth

- `official_paid_amount` authority 采用：
  - `T_GovPayment.paid_amount`
- 只计入满足以下条件的 gov payment rows：
  - 关联到 annuity fee item / annuity pay-list lineage
  - `paid_date` 非空或 status 属于 `PAID/RECORDED`
- `PayList.total_amount` 仅作为 pay-list header 投影
  - 不作为 grouped official-paid 统计的第一权威

### Client received source-of-truth

- `client_received_amount` authority 采用：
  - `T_CaseReceipt.received_amt`
- 只计入：
  - `CaseReceipt.year_no` 非空
  - 且能代表 annuity year-specific receipt lineage 的 rows
- `GovPayment.paid_amount` 不能自动替代客户实收
  - 官方实缴与客户实收在财务语义上不同

### Grouping lineage

- `client` 维度：
  - 直接使用 `AnnuityTask.client_id`
- `year` 维度：
  - 直接使用 `AnnuityTask.year_no`
  - `GovPayment` / `CaseReceipt` 需回投到相同 `year_no`
- `country` 维度：
  - 通过 `AnnuityTask.case_id -> Case.to_country / from_country`
- 第一轮 grouped amount implementation 必须以 `AnnuityTask` 为主表，再左联：
  - `GovPayment`
  - `CaseReceipt`
  的同年 / 同案 lineage

### Metric separation

- `payable_amount`
  - 来自 annuity task layer
- `official_paid_amount`
  - 来自 gov payment layer
- `client_received_amount`
  - 来自 case receipt layer
- 这三者不得在同一个 source 上互相替代

## Implementation Readiness Judgment

- grouped annuity amount summaries 在当前 carrier 下可直接进入实现
- 不需要新增 schema / migration
- 但必须单独作为一个 grouped amount implementation slice，不能与 success-rate semantics 混做

## Recommended Next Slice

- `ANNRPT-AMOUNT-01`
- exact closure candidate:
  - extend `GET /annuity/tasks` summary with grouped:
    - `client_amounts`
    - `country_amounts`
    - `year_amounts`
  - each row contains:
    - `payable_amount`
    - `official_paid_amount`
    - `client_received_amount`
    - `task_count`
  - render those grouped summaries on `AnnuityTaskList.vue`

## Explicitly Deferred

- success-rate semantics
- chart / export
- predictive monitoring analytics
- pay-list header reporting as a separate family

## Risks

- 把 `PayList.total_amount` 错当成官方实缴第一权威
- 把 `GovPayment.paid_amount` 错当成客户实收
- 未经 lineage 回投就把任意 `CaseReceipt` 行吸入年费报表
- 在同一条 story 里混入 success-rate

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- 但必须先以本语义冻结作为 authority，再进入 `ANNRPT-AMOUNT-01`
