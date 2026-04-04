# RPT-FEE Balance Implementation Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE balance-summary implementation after semantics freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`RPT-FEE` 已经完成 grouped aggregate 与 agent-income residual，但相对 `FPMS SPEC 2.0 9.4.2` 仍缺少 billed / received / unpaid 统计语义。`FEERPT-BALANCE-SPEC-01` 已冻结 authority：

- billed -> `T_Bill / T_BillItem`
- received -> `Bill.amount - Bill.balance`
- unpaid -> `Bill.balance`

下一步应把这组语义落成真实产品行为，继续复用 `GET /fees/drafts` 与 `FeeDraftList.vue`，而不是再新建第二个费报页面。

## Assumptions

- `FEERPT-BALANCE-SPEC-01` 是本 wave 的 authority
- in-scope lineage 仅包含：
  - `Bill.direction == "AR"`
  - 且 `BillItem.draft_id` 可回投到 fee-draft rows 的账单项
- 不可追溯到 `draft_id` 的手工账单项继续 deferred
- close 标准固定为：
  - 只有真实 API + FE summary block 存在，才允许该 residual capability 计入 closure

## Scope

- 后端为 `GET /fees/drafts` summary 新增：
  - `billed_amount`
  - `received_amount`
  - `unpaid_balance_amount`
  - `partially_received_bill_count`
- 前端在 `FeeDraftList.vue` 增加一组 billed / received / unpaid 摘要展示
- 更新 `fees.ts / fees.types.ts` 对应 summary contract
- 为上述语义补 targeted tests

## Explicit Non-scope

- 不做 time trend reporting
- 不做 service/gov/misc billed-received-balance breakdown
- 不做 chart / export
- 不做手工账单项 lineage 补齐
- 不更新 `RPT-FEE` 或 `#13` close decision

## Shared-file Ownership

### Backend shared files

- `backend/app/modules/fees/service.py`
- `backend/app/modules/fees/schemas.py`
- `backend/tests/test_fee_report.py`

### Frontend shared files

- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/modules/fees/pages/FeeDraftList.vue`

These files require serialized ownership:

1. BE balance summary implementation
2. FE contract wiring + page rendering
3. QA close

## Implementation Recommendation

### Backend closure slice

- Extend fee report summary builder to:
  - load in-scope draft ids
  - aggregate distinct AR bills reachable through `BillItem.draft_id`
  - compute:
    - `billed_amount = Σ Bill.amount`
    - `received_amount = Σ (Bill.amount - Bill.balance)`
    - `unpaid_balance_amount = Σ Bill.balance`
    - `partially_received_bill_count = count(0 < balance < amount)`
- Distinct bill counting is required because one bill can contain multiple fee items tied to the same or multiple drafts

### Frontend closure slice

- Extend fee summary types/mappers with the new four fields
- Render one narrow summary block on `FeeDraftList.vue`
- Keep all visible text in Simplified Chinese

## Test Strategy

### Backend

- Extend `backend/tests/test_fee_report.py`
- Add a focused scenario containing:
  - at least one settled bill
  - at least one partially received bill
  - at least one fully unpaid bill
  - one hand-made bill item without `draft_id` to ensure it is excluded

### Frontend

- Existing lint + typecheck coverage is sufficient for this slice

## Exact Closure Candidates

- `FEERPT-BALANCE-BE-01`
- `FEERPT-BALANCE-FE-01`
- `FEERPT-BALANCE-QA-01`

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- Execution should proceed as a serialized three-task wave: BE -> FE -> QA
