# GF-POSTDRAFT-FE-01 — 授权费 post-draft 完成入口

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-postdraft.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在现有授权费任务看板中，为 `DRAFT_GENERATED` 行接入真实的 `mark_done` 完成入口，让 post-draft workflow 形成最小可达产品路径。
- Exact closure slice:
  - 更新 `frontend/src/api/grantFees.ts`
  - 更新 `frontend/src/api/grantFees.types.ts`
  - 更新 `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - 更新 `docs/superpowers/specs/2026-04-05-grant-fee-postdraft-design.md`
  - 更新 `docs/superpowers/plans/2026-04-05-grant-fee-postdraft.md`
- Explicit non-closure:
  - 不做任何 backend 代码修改
  - 不做 bill linkage
  - 不做 document/reminder linkage
  - 不做 detail/edit 或 batch action
- Remaining follow-up task ids:
  - `GF-POSTDRAFT-QA-01`
- Allowlist:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `docs/superpowers/specs/2026-04-05-grant-fee-postdraft-design.md`
  - `docs/superpowers/plans/2026-04-05-grant-fee-postdraft.md`
  - `tasks/postenhancement/frontend/GF-POSTDRAFT-FE-01.md`
  - `tasks/postenhancement/backend/GF-POSTDRAFT-QA-01.md`
- Verification:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh GF-POSTDRAFT-FE-01`

## Execution Checklist

- [ ] Add grant-fee state action client for `mark_done`
- [ ] Render row-level `标记完成` for `DRAFT_GENERATED`
- [ ] Refresh current list after successful completion
- [ ] Keep non-post-draft actions deferred
