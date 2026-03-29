# BADDEBT-QA-01 Evidence Summary

## Story Status

- Story: `Priority P1 #6 / Billing Bad-Debt Workflow`
- chosen_runbook: `P0-prereq-heavy-story`
- Final story status: `PASS`
- Residual gap inside approved interpretation: `None`

## Item-to-Slice Ledger

- `BADDEBT-DB-01`
  - Closure: 坏账主凭证与回收记录持久化 + `Bill.bad_debt_status/substatus`
  - Gate: `PASS`
  - Evidence: `artifacts/BADDEBT-DB-01/results.jsonl`, `artifacts/BADDEBT-DB-01/summary.md`

- `BADDEBT-BE-BILL-01`
  - Closure: `GET /bills/{bill_id}` 只读坏账链路 contract
  - Gate: `PASS`
  - Evidence: `artifacts/BADDEBT-BE-BILL-01/results.jsonl`, `artifacts/BADDEBT-BE-BILL-01/summary.md`

- `BADDEBT-BE-ACT-01`
  - Closure: 手工标记坏账 + 部分收款后坏账结转
  - Gate: `PASS`
  - Evidence: `artifacts/BADDEBT-BE-ACT-01/results.jsonl`, `artifacts/BADDEBT-BE-ACT-01/summary.md`

- `BADDEBT-BE-REC-01`
  - Closure: 回收坏账写动作 + 多次部分回收约束
  - Gate: `PASS`
  - Evidence: `artifacts/BADDEBT-BE-REC-01/results.jsonl`, `artifacts/BADDEBT-BE-REC-01/summary.md`

- `BADDEBT-FE-BILL-01`
  - Closure: 账单详情页坏账操作区 + 主凭证/回收记录展示
  - Gate: `PASS`
  - Evidence: `artifacts/BADDEBT-FE-BILL-01/results.jsonl`, `artifacts/BADDEBT-FE-BILL-01/summary.md`

- `BADDEBT-BE-RPT-01`
  - Closure: `GET /bills` 坏账状态筛选 + 坏账核心汇总 contract
  - Gate: `PASS`
  - Evidence: `artifacts/BADDEBT-BE-RPT-01/results.jsonl`, `artifacts/BADDEBT-BE-RPT-01/summary.md`

- `BADDEBT-FE-RPT-01`
  - Closure: `BillList.vue` 坏账状态筛选 + 汇总展示
  - Gate: `PASS`
  - Evidence: `artifacts/BADDEBT-FE-RPT-01/results.jsonl`, `artifacts/BADDEBT-FE-RPT-01/summary.md`

## Planning Correction Recorded

- Execution discovered that `frontend/src/modules/billing/pages/BillingReport.vue` does not exist.
- The plan was corrected in `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`.
- `BADDEBT-FE-RPT-01` was narrowed to the existing `frontend/src/modules/billing/pages/BillList.vue` surface.
- This correction did not change story shape or runbook, and did not expand scope.

## Coverage Decision

- Approved interpretation closed:
  - `AR` 账单坏账标记/结转
  - 坏账主凭证
  - 多次部分回收
  - 账单详情查看坏账链路
  - 账单列表坏账筛选与核心汇总

- Explicitly out of scope and still deferred:
  - 坏账冲回
  - 历史补录/迁移
  - 自动逾期坏账
  - `AR` 之外对象
  - 独立坏账工作台/专门报表页

## Verification

- `./scripts/task_validate.sh BADDEBT-DB-01` -> `PASS`
- `./scripts/task_validate.sh BADDEBT-BE-BILL-01` -> `PASS`
- `./scripts/task_validate.sh BADDEBT-BE-ACT-01` -> `PASS`
- `./scripts/task_validate.sh BADDEBT-BE-REC-01` -> `PASS`
- `./scripts/task_validate.sh BADDEBT-FE-BILL-01` -> `PASS`
- `./scripts/task_validate.sh BADDEBT-BE-RPT-01` -> `PASS`
- `./scripts/task_validate.sh BADDEBT-FE-RPT-01` -> `PASS`
- All referenced `artifacts/<TASK-ID>/results.jsonl` files exist.
