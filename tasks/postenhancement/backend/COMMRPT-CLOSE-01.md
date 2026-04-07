# COMMRPT-CLOSE-01 — commission report export close audit

- Source: `docs/superpowers/plans/2026-04-06-commission-report-export.md`
- Type: `close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 基于已提交的提成结算报表导出实现，刷新 final audit 中 Module 6 `FR-COM-07` residual 结论。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - 生成 `artifacts/COMMRPT-CLOSE-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不更新 refresh review
  - 不做其他模块 close decision
- Remaining follow-up task ids:
  - `COMMRPT-QA-CLOSE-01`
- Allowlist:
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-06-commission-report-export-design.md`
  - `docs/superpowers/plans/2026-04-06-commission-report-export.md`
  - `tasks/postenhancement/backend/COMMRPT-CLOSE-01.md`
  - `tasks/postenhancement/backend/COMMRPT-QA-CLOSE-01.md`
- Verification:
  - `./scripts/task_validate.sh COMMRPT-CLOSE-01`

## Execution Checklist

- [ ] Confirm export endpoint and frontend user path are committed product behavior
- [ ] Refresh Module 6 final-audit residual wording accordingly
