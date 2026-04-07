# COMMRPT-EXPORT-QA-01 — commission settlement report export QA

- Source: `docs/superpowers/plans/2026-04-06-commission-report-export.md`
- Type: `qa`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `COMMRPT-EXPORT-BE-01` 与 `COMMRPT-EXPORT-FE-01` 的 evidence、scope 与 task gates，确认本 wave 只关闭导出闭环。
- Exact closure slice:
  - 审核 implementation evidence
  - 生成 `artifacts/COMMRPT-EXPORT-QA-01/**`
- Explicit non-closure:
  - 不做产品实现
  - 不做打印
  - 不做 final audit 更新
- Remaining follow-up task ids:
  - `COMMRPT-CLOSE-01`
- Allowlist:
  - `artifacts/COMMRPT-EXPORT-BE-01/**`
  - `artifacts/COMMRPT-EXPORT-FE-01/**`
  - `artifacts/COMMRPT-EXPORT-QA-01/**`
  - `tasks/postenhancement/backend/COMMRPT-EXPORT-QA-01.md`
- Verification:
  - `./scripts/task_validate.sh COMMRPT-EXPORT-QA-01`

## Execution Checklist

- [ ] Confirm backend export endpoint exists and is tested
- [ ] Confirm frontend export button exists and triggers real download path
- [ ] Confirm no print or unrelated commission slice was absorbed
