# COMMRPT-EXPORT-BE-01 — commission settlement report export endpoint

- Source: `docs/superpowers/plans/2026-04-06-commission-report-export.md`
- Type: `backend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为现有提成结算报表增加真实导出 endpoint，复用现有筛选条件和报表查询 authority，输出 xlsx 文件供前端下载。
- Exact closure slice:
  - 新增 commission settlement report export endpoint
  - 复用现有 `CommissionReport.Read` 权限
  - 增加 targeted backend tests
- Explicit non-closure:
  - 不做 frontend 导出按钮
  - 不做打印
  - 不修改结算批次/明细生成逻辑
- Remaining follow-up task ids:
  - `COMMRPT-EXPORT-FE-01`
  - `COMMRPT-EXPORT-QA-01`
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/commission/export_excel.py`
  - `backend/tests/test_commission_report.py`
- Verification:
  - `python3 -m ruff check backend/app/modules/commission/api.py backend/app/modules/commission/service.py backend/app/modules/commission/export_excel.py backend/tests/test_commission_report.py`
  - `cd backend && pytest -q tests/test_commission_report.py`
  - `./scripts/task_validate.sh COMMRPT-EXPORT-BE-01`

## Execution Checklist

- [ ] Add export endpoint using existing settlement report filters
- [ ] Produce xlsx payload with summary / grouped totals / details
- [ ] Cover 200 and permission semantics in targeted tests
