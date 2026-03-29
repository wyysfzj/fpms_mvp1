# CASEFLD-FE-FORM-01 — 案卷缺失字段创建/编辑表单补齐

- Source: `docs/superpowers/plans/2026-03-29-case-missing-fields-prereq.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在 `CaseCreate.vue` 与 `CaseEdit.vue` 补齐 15 字段的录入/编辑 UI，并对齐 cases API/types contract。
- Exact closure slice:
  - 更新 `frontend/src/api/cases.ts`
  - 更新 `frontend/src/api/cases.types.ts`
  - 更新 `frontend/src/modules/cases/pages/CaseCreate.vue`
  - 更新 `frontend/src/modules/cases/pages/CaseEdit.vue`
- Explicit non-closure:
  - 不改详情页
  - 不改列表页
  - 不加搜索/筛选/导入导出
- Remaining follow-up task ids:
  - `CASEFLD-FE-DETAIL-01`
  - `CASEFLD-QA-01`
- Allowlist:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
- Shared ownership files:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
- Verification:
  - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseCreate.vue src/modules/cases/pages/CaseEdit.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh CASEFLD-FE-FORM-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement minimal UI + API mapping only
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
