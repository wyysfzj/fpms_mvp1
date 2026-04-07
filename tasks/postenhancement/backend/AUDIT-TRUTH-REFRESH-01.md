# AUDIT-TRUTH-REFRESH-01 — final audit ledger truth refresh

- Source: `docs/superpowers/plans/2026-04-07-final-audit-truth-refresh.md`
- Type: `close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 基于已提交产品证据刷新 final audit ledger，去除已闭合 residual，并把仍未闭合的 residual 缩到真实剩余范围。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - 生成 `artifacts/AUDIT-TRUTH-REFRESH-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - 不更新 `docs/priority-ranked-mitigation-ledger.md`
  - 不新增 residual implementation
- Remaining follow-up task ids:
  - `AUDIT-QA-TRUTH-REFRESH-01`
- Allowlist:
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-07-final-audit-truth-refresh-design.md`
  - `docs/superpowers/plans/2026-04-07-final-audit-truth-refresh.md`
  - `tasks/postenhancement/backend/AUDIT-TRUTH-REFRESH-01.md`
  - `tasks/postenhancement/backend/AUDIT-QA-TRUTH-REFRESH-01.md`
- Verification:
  - `./scripts/task_validate.sh AUDIT-TRUTH-REFRESH-01`

## Execution Checklist

- [ ] Remove stale Module 2 residual for `has_attachment`
- [ ] Remove stale Module 3 residual for list-level export/print
- [ ] Keep Module 4 limited to truthful remaining residuals only
- [ ] Keep Module 6 closed with export evidence
- [ ] Refresh inherited Module 8 residual summary
- [ ] Refresh final remaining-gap list and final judgment
