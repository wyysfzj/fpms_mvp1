# Module 6 FR-COM-07 提成结算报表导出 Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md` 仍将 Module 6 的 residual 标记为：`FR-COM-07` 提成结算报表已具备真实查询和统计能力，但缺少导出闭环。当前需要在不扩展结算批次管理、不引入打印链路的前提下，为现有提成结算报表补齐真实 export contract 与 frontend user path。

## Scope

- 为现有 `GET /api/v1/commission/reports/settlement` 报表补齐导出 endpoint
- 复用现有报表筛选条件与聚合结果
- 在 `CommissionSettlement.vue` 提供真实导出入口
- 增加 targeted backend tests
- 生成 QA close-audit evidence

## Explicit Non-scope

- 不做打印
- 不做结算批次 CRUD 调整
- 不做结算明细生成逻辑变更
- 不做新的统计口径
- 不做 final audit / review close update

## Current Product Evidence

- backend report contract:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- frontend report page:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
- tests:
  - `backend/tests/test_commission_report.py`

## Closure Standard

- backend export endpoint exists and reuses truthful report filters
- frontend export button exists and triggers a real file download path
- targeted tests cover successful export and permission semantics
- no part of print or unrelated commission behavior is silently absorbed

## Exact Closure Slices

- `COMMRPT-EXPORT-BE-01`
  - 提供提成结算报表导出 endpoint 与 xlsx payload
- `COMMRPT-EXPORT-FE-01`
  - 接入提成结算报表导出入口与下载 user path
- `COMMRPT-EXPORT-QA-01`
  - 审计 evidence、scope、task gates
- `COMMRPT-CLOSE-01`
  - 如实现完成后更新 final audit 中 Module 6 residual 结论

## Shared-file / Ownership Notes

- backend shared files:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
  - new `backend/app/modules/commission/export_excel.py`
  - `backend/tests/test_commission_report.py`
- frontend shared files:
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- close-audit docs:
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
