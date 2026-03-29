# CASEFLD-FE-DETAIL-01 — 案卷缺失字段详情展示补齐

- Source: `docs/superpowers/plans/2026-03-29-case-missing-fields-prereq.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在 `CaseDetail.vue` 展示 15 个缺失字段，并对齐 cases API/types contract。
- Exact closure slice:
  - 更新 `frontend/src/api/cases.ts`
  - 更新 `frontend/src/api/cases.types.ts`
  - 更新 `frontend/src/modules/cases/pages/CaseDetail.vue`
- Explicit non-closure:
  - 不改 create/edit
  - 不改列表页
  - 不加搜索/筛选/导入导出
- Remaining follow-up task ids:
  - `CASEFLD-QA-01`
- Allowlist:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
- Shared ownership files:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
- Verification:
  - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseDetail.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh CASEFLD-FE-DETAIL-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement minimal detail display only
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
