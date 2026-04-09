# FEZH-CORE-PAGES-01 — high-visibility English residue cleanup

- Source: `docs/superpowers/plans/2026-04-09-fe-chinese-cleanup.md`
- Type: `frontend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 清理高可见核心页面上的英文状态、枚举值和英文列标题。
- Exact closure slice:
  - `CaseFeesTab.vue` no longer exposes raw English status to users
  - `CommissionRuleList.vue` no longer exposes `ID` header or raw English enum/type values to users
- Explicit non-closure:
  - 不做长尾页面 mixed `ID` 标签清理
  - 不扩展到 allowlist 外页面
  - 不做 backend / API contract 改动
- Remaining follow-up task ids:
  - `FEZH-LONGTAIL-PAGES-01`
  - `FEZH-QA-CLOSE-01`
- Allowlist:
  - `frontend/src/modules/cases/components/CaseFeesTab.vue`
  - `frontend/src/modules/commission/pages/CommissionRuleList.vue`
  - `frontend/src/constants/displayText.ts`
  - `frontend/src/constants/labels.zh.ts`
- Verification:
  - frontend lint
  - typecheck
  - grep for residual English on allowlist

## Execution Checklist

- [ ] Replace raw status text exposure with Chinese mapper/rendering
- [ ] Replace English column headers with Chinese labels
- [ ] Replace raw type/enum exposure with Chinese display text
