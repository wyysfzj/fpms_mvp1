# COMMRPT-EXPORT-FE-01 — commission settlement report export user path

- Source: `docs/superpowers/plans/2026-04-06-commission-report-export.md`
- Type: `frontend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在现有提成结算报表页接入真实导出按钮和文件下载路径，复用现有筛选条件调用 backend export endpoint。
- Exact closure slice:
  - 新增 commission report export API client
  - 在 `CommissionSettlement.vue` 增加导出按钮并下载 xlsx
- Explicit non-closure:
  - 不做 backend endpoint
  - 不做打印
  - 不调整结算批次创建/生成明细区域
- Remaining follow-up task ids:
  - `COMMRPT-EXPORT-QA-01`
- Allowlist:
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/commission.ts src/api/commission.types.ts src/modules/commission/pages/CommissionSettlement.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh COMMRPT-EXPORT-FE-01`

## Execution Checklist

- [ ] Add export client returning blob
- [ ] Add export button with Simplified Chinese UI text
- [ ] Download file using current report filters
