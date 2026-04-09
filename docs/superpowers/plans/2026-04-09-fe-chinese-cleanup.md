# FE Chinese Cleanup Plan

- date: `2026-04-09`
- design: `docs/superpowers/specs/2026-04-09-fe-chinese-cleanup-design.md`

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend-only cleanup story`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

### Wave 1

- `FEZH-CLEANUP-SPEC-01`
  - owner: `main thread`
  - exact closure slice:
    - freeze FE 中文化专项的 decomposition authority、batch manifest、shared-file ownership
  - explicit non-closure:
    - no frontend product code
    - no backend changes

### Wave 2

- `FEZH-SHARED-TEXT-01`
  - owner: `main thread`
  - exact closure slice:
    - normalize shared display text / common Chinese mapper for visible enum-status-label usage
  - explicit non-closure:
    - no page-specific cleanup outside allowlist
    - no backend changes

### Wave 3

- `FEZH-CORE-PAGES-01`
  - owner: `main thread`
  - exact closure slice:
    - clear confirmed English residue on high-visibility core pages
  - explicit non-closure:
    - no long-tail page cleanup
    - no shared constants refactor outside allowlist

### Wave 4

- `FEZH-LONGTAIL-PAGES-01`
  - owner: `main thread`
  - exact closure slice:
    - normalize mixed Chinese + English user-visible labels on audited tail pages
  - explicit non-closure:
    - no new page inventory expansion beyond allowlist
    - no backend changes

### Wave 5

- `FEZH-QA-CLOSE-01`
  - owner: `main thread`
  - exact closure slice:
    - audit FE cleanup evidence, run task gates, confirm no real residual remains inside approved cleanup interpretation
  - explicit non-closure:
    - no page edits
    - no backend changes

## Serialized Shared-file Decisions

- `frontend/src/constants/displayText.ts` and `frontend/src/constants/labels.zh.ts` are serialized to `FEZH-SHARED-TEXT-01`
- `FEZH-CORE-PAGES-01` starts only after shared display text decisions are frozen
- `FEZH-LONGTAIL-PAGES-01` starts only after `FEZH-CORE-PAGES-01` finishes if it needs the same shared labels/constants
- `FEZH-QA-CLOSE-01` is evidence-only and does not edit product files

## Allowlist Intent

- `FEZH-SHARED-TEXT-01`
  - `frontend/src/constants/displayText.ts`
  - `frontend/src/constants/labels.zh.ts`
- `FEZH-CORE-PAGES-01`
  - `frontend/src/modules/cases/components/CaseFeesTab.vue`
  - `frontend/src/modules/commission/pages/CommissionRuleList.vue`
- `FEZH-LONGTAIL-PAGES-01`
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
- `FEZH-QA-CLOSE-01`
  - evidence/artifact files only

## Verification

- `cd frontend && npm run lint -- <task allowlist>`
- `cd frontend && npm run typecheck`
- `rg -n "LOCKED|NORMAL|ANNUITY_FEE|\\bID\\b|用户ID|部门ID" <task allowlist>`
- `./scripts/task_validate.sh FEZH-CLEANUP-SPEC-01`
- `./scripts/task_validate.sh FEZH-SHARED-TEXT-01`
- `./scripts/task_validate.sh FEZH-CORE-PAGES-01`
- `./scripts/task_validate.sh FEZH-LONGTAIL-PAGES-01`
- `./scripts/task_validate.sh FEZH-QA-CLOSE-01`
