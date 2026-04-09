# FEZH-LONGTAIL-PAGES-01 — tail-page mixed English label cleanup

- Source: `docs/superpowers/plans/2026-04-09-fe-chinese-cleanup.md`
- Type: `frontend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 清理已审计长尾页面中的 mixed Chinese + English 用户可见标签，使其统一为自然简体中文。
- Exact closure slice:
  - `ExpenseCreate.vue` mixed `ID` labels/placeholders normalized to Chinese-facing wording
  - `ExpenseList.vue` mixed `ID` labels/placeholders normalized to Chinese-facing wording
- Explicit non-closure:
  - 不扩展到新的页面 inventory
  - 不做核心高可见页面 cleanup
  - 不做 backend / API contract 改动
- Remaining follow-up task ids:
  - `FEZH-QA-CLOSE-01`
- Allowlist:
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
  - `frontend/src/constants/labels.zh.ts`
- Verification:
  - frontend lint
  - typecheck
  - grep for residual mixed `ID` labels on allowlist

## Execution Checklist

- [ ] Normalize user-visible mixed `ID` labels to Chinese wording
- [ ] Keep technical values in code only, not in rendered UI copy
