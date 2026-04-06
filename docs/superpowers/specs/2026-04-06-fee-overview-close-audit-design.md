# P2 #16 费用综合查询 Product Close Audit Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `close-audit after committed product slices`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#16 费用综合查询` 在 `FEOVERVIEW-UPPER-BE-01`、`FEOVERVIEW-LOWER-BE-01`、`FEOVERVIEW-FE-01` 和 `FEOVERVIEW-UPPER-FEETYPE-*` 完成后，已经具备重新进行 strict close-audit 的条件。当前需要根据 `FPMS SPEC 2.0` §5.11 的真实产品实现，判断该条目是否还能诚实保留为“first-round unified query”，还是应该基于真实双表页与上下半表 API 更新为严格闭合。

## Scope

- 复核 `#16` 与 `SPEC 2.0` §5.11 的 product parity
- 更新 refresh review 中 `#16` 的 evidence 与 close rationale
- 更新 final audit ledger 中 Module 4 对 `5.11` 的 residual 结论

## Explicit Non-scope

- 不新增任何 billing 产品实现
- 不修改 `priority-ranked-mitigation-ledger.md`
- 不扩展到 `SPEC 5.10.2`
- 不实现 export/print

## Audit Basis

- `FPMS SPEC 2.0` §5.11.1：
  - 查询条件包含 `案卷号 / 申请号 / 专利号 / 客户 / 申请人`
  - 上半表 `费用类型`
  - 下半表 `费用类型`
- `FPMS SPEC 2.0` §5.11.2：
  - 上半表 authority 必须是 `T_GovPayment`
  - 结果字段应来自 `T_GovPayment + T_PayList + T_FeeItem + T_Case`
- `FPMS SPEC 2.0` §5.11.3：
  - 下半表 authority 必须是 `T_CaseReceipt`
  - 结果字段应来自 `T_CaseReceipt + T_Case`

## Current Product Evidence

- upper pane backend:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/tests/test_fee_overview_upper_api.py`
- lower pane backend:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/tests/test_fee_overview_lower_api.py`
- dual-pane frontend:
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/constants/menu.ts`
  - `frontend/src/modules/billing/pages/FeeUnifiedQuery.vue`
- committed implementation evidence:
  - `artifacts/FEOVERVIEW-UPPER-BE-01`
  - `artifacts/FEOVERVIEW-LOWER-BE-01`
  - `artifacts/FEOVERVIEW-FE-01`
  - `artifacts/FEOVERVIEW-UPPER-FEETYPE-BE-01`
  - `artifacts/FEOVERVIEW-UPPER-FEETYPE-FE-01`

## Close Decision Rule

- If committed product behavior now covers:
  - dual-pane fee overview page
  - upper pane `T_GovPayment` endpoint
  - lower pane `T_CaseReceipt` endpoint
  - first-round truthful `fee_type` semantics on the upper pane
- then `#16` and final-audit `5.11` residual should be updated to `Closed`.

## Exact Closure Slice

- `FEOVERVIEW-CLOSE-01`
  - refresh `#16` and Module 4 `5.11` final-audit decision based on committed product evidence

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
