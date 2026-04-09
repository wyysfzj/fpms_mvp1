# FEZH-CLEANUP-SPEC-01 — FE user-visible English residue cleanup batch freeze

- Source: `docs/superpowers/plans/2026-04-09-fe-chinese-cleanup.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 FE 中文化专项的 batch decomposition、shared-file ownership 和 close boundary。
- Exact closure slice:
  - 新增 FE cleanup spec/plan
  - 新增 implementation batch manifest
  - 生成 `artifacts/FEZH-CLEANUP-SPEC-01/**`
- Explicit non-closure:
  - 不做任何 FE 页面修改
  - 不做 backend / API contract 改动
- Remaining follow-up task ids:
  - `FEZH-SHARED-TEXT-01`
  - `FEZH-CORE-PAGES-01`
  - `FEZH-LONGTAIL-PAGES-01`
  - `FEZH-QA-CLOSE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-09-fe-chinese-cleanup-design.md`
  - `docs/superpowers/plans/2026-04-09-fe-chinese-cleanup.md`
  - `tasks/postenhancement/backend/FEZH-CLEANUP-SPEC-01.md`
  - `tasks/postenhancement/frontend/FEZH-SHARED-TEXT-01.md`
  - `tasks/postenhancement/frontend/FEZH-CORE-PAGES-01.md`
  - `tasks/postenhancement/frontend/FEZH-LONGTAIL-PAGES-01.md`
  - `tasks/postenhancement/backend/FEZH-QA-CLOSE-01.md`
- Verification:
  - `./scripts/task_validate.sh FEZH-CLEANUP-SPEC-01`

## Execution Checklist

- [ ] Freeze shared display-text ownership
- [ ] Freeze core-page cleanup slice
- [ ] Freeze long-tail cleanup slice
- [ ] Freeze QA close-audit slice
