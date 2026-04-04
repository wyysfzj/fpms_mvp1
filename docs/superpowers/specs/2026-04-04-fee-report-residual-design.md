# RPT-FEE Residual Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `residual decomposition after implemented first-round slice`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-FEE` 当前不能再被诚实地描述为“未实现”，但也不能被直接判定为 full-spec 闭合。现有仓库已经具备第一轮费用统计报表产品切片：`GET /fees/drafts` 提供 report-style summary，`FeeDraftList.vue` 提供筛选、summary cards 和明细列表。但对照 `FPMS SPEC 2.0` `9.4.2`，当前 family 仍缺少 grouped dimensions、代理人收入语义、以及基于账单/收款状态的统计口径，因此下一步不应重做已完成的 first-round 实现，而应先冻结 residual map。

## Assumptions

- `FEERPT-BE-01` / `FEERPT-FE-01` / `FEERPT-QA-01` 的 first-round closure 继续有效
- `RPT-FEE` 的 first-round 权威产品切片固定为：
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/fees/service.py`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
- `FeeUnifiedQuery.vue` 与 `ExpenseList.vue` 是相关财务查询能力，但不自动等于 `RPT-FEE` first-round closure authority
- 关闭标准仍固定为：
  - 只有真实产品行为存在，才允许新增 residual capability 计入 closure

## Scope

- 对 `RPT-FEE` 做 strict residual capability map
- 明确 first-round already closed slice
- 明确相对 `FPMS SPEC 2.0 9.4.2` 仍缺的 grouped dimensions / metrics / source semantics
- 推荐一个最小 residual implementation slice

## Explicit Non-scope

- 不重做 `FEERPT-BE-01`
- 不重做 `FEERPT-FE-01`
- 不做任何费用统计产品实现补丁
- 不做图表 / 导出 / profit analysis

## Current Implemented Slice

### Existing product evidence

- `frontend/src/modules/fees/pages/FeeDraftList.vue`
- `backend/app/modules/fees/api.py`
- `backend/app/modules/fees/service.py`
- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `artifacts/FEERPT-BE-01/**`
- `artifacts/FEERPT-FE-01/**`
- `artifacts/FEERPT-QA-01/**`

### Already closed under first-round interpretation

- approved report filters:
  - `client_id`
  - `case_id`
  - `fee_type`
  - `currency`
  - `date_range`
  - `draft_status`
  - `bill_status`
- summary cards:
  - `total_draft_count`
  - `service_fee_amount`
  - `government_fee_amount`
  - `income_amount`
- detail list retained as report detail portion

## Residual Spec Gap vs `FPMS SPEC 2.0`

### Spec-required examples not yet closed

- 按客户、案件类型、国别统计服务费/官方费收入
- 按代理人统计其所负责案件带来的服务费收入
- 按时间段统计各种费用类型总额
- 统计未收金额（Balance 合计）

### Residual dimensions not yet represented as summary output

- `Client` grouped statistics
- `CaseType` grouped statistics
- `Country` grouped statistics
- `PrimaryAgent / SecondAgent` grouped income statistics
- `Year / Month` grouped time buckets

### Residual source semantics not yet closed

- 当前 first-round 以 `T_FeeDraft / T_FeeItem` 为主要 carrier
- spec `9.4.2` 明确推荐主数据来源：
  - `T_Bill / T_BillItem`
  - optional received-status filtering via:
    - `T_Offset`
    - `T_CaseReceipt`
- 因此当前 family 仍缺：
  - billed / received semantic split
  - `Balance`-based unpaid metric semantics

### Residual metrics not yet represented as summary output

- grouped service-fee totals by client / case type / country
- grouped government-fee totals by client / case type / country
- agent-attributed service income
- period-bucket totals
- unpaid amount / balance totals

## Residual Decomposition Recommendation

### Residual bucket A — grouped fee-income summaries

- by client totals
- by case-type totals
- by country totals

### Residual bucket B — agent-attributed service income

- by primary / secondary agent service-fee totals
- explicit ownership semantics required

### Residual bucket C — billed / received / unpaid semantics

- billed totals
- received/partially received filter semantics
- unpaid balance totals

### Residual bucket D — time trend reporting

- year/month grouped totals by fee family

## Recommended First Residual Slice

- `FEERPT-AGGREGATE-01`
- exact closure candidate:
  - extend the existing fee-report summary with grouped:
    - `client_amounts`
    - `case_type_amounts`
    - `country_amounts`
  - add FE presentation for those grouped summaries on `FeeDraftList.vue`

### Why this is recommended first

- It builds on the existing fee-report page instead of inventing a second report page
- It stays inside the current `fees` module ownership
- It is narrower than agent attribution and received/unpaid semantics
- It avoids pulling `billing` and `case_receipt` source semantics into the same first residual slice

## Residuals Explicitly Deferred

- agent-attributed service income
- billed / received / unpaid-balance semantics
- year/month trend reporting
- charts
- export
- cross-finance report shell

## SQLite / Phase Compatibility Assessment

- This residual mapping story is doc-only and compatible
- The recommended first residual slice appears achievable without schema change
- If billed / received / unpaid semantics later require cross-module carrier normalization, that must be assessed as a separate follow-up story, not absorbed here

## Risks / Blockers

- Treating `FeeUnifiedQuery` or `ExpenseList` as proof that `RPT-FEE` already matches spec `9.4.2`
- Treating fee-draft totals as equivalent to billed / received / unpaid report semantics
- Folding grouped aggregates, agent attribution, and unpaid-balance semantics into one next slice

## Exact Closure Slice Candidates

### Preferred

- `FEERPT-RESIDUAL-01`
  - freeze residual fee-report map and first residual implementation recommendation

### Explicit non-closure

- no product implementation
- no re-close of first-round `FEERPT-*`
- no chart/export/trend implementation

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task should be a doc-only residual mapping story before any new fee-report implementation slice.
