# FEZH-SHARED-TEXT-01 — shared display text and Chinese mapper normalization

- Source: `docs/superpowers/plans/2026-04-09-fe-chinese-cleanup.md`
- Type: `frontend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 统一共享显示文本与枚举/状态中文映射入口，避免页面直接裸露英文技术值。
- Exact closure slice:
  - shared display text / common Chinese mapper normalized
  - page tasks can consume frozen mapper outputs
- Explicit non-closure:
  - 不做核心页面清理
  - 不做长尾页面清理
  - 不做 backend / API contract 改动
- Remaining follow-up task ids:
  - `FEZH-CORE-PAGES-01`
  - `FEZH-LONGTAIL-PAGES-01`
  - `FEZH-QA-CLOSE-01`
- Allowlist:
  - `frontend/src/constants/displayText.ts`
  - `frontend/src/constants/labels.zh.ts`
- Verification:
  - frontend lint
  - typecheck

## Execution Checklist

- [ ] Normalize shared Chinese display text entry points
- [ ] Add only mapper/label changes needed by approved page waves
