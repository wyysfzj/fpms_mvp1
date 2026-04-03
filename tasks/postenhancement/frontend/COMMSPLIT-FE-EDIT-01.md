# COMMSPLIT-FE-EDIT-01 — create/edit split consistency

- Source: `docs/superpowers/plans/2026-04-03-commission-split-fe-edit-consistency.md`
- Type: `page + component reuse`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在 `CaseCreate.vue` 中补齐与 `CaseEdit.vue` 等价的 `CaseAgentSplit` 录入能力，使 create/edit 两页在多代理 split 录入能力上达到一致。
- Exact closure slice:
  - 更新 `frontend/src/modules/cases/pages/CaseCreate.vue`
  - 如严格必要，可最小更新 `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
- Explicit non-closure:
  - 不改 `CaseDetail.vue`
  - 不改 settlement 页面
  - 不改 router/menu
  - 不改 backend semantics
- Remaining follow-up task ids:
  - `COMMSPLIT-FE-VIEW-01`
  - `COMMSPLIT-QA-08`
- Allowlist:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
  - `tasks/postenhancement/frontend/COMMSPLIT-FE-EDIT-01.md`
  - `tasks/postenhancement/frontend/COMMSPLIT-QA-08.md`
- Shared ownership files:
  - `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
- Verification:
  - `cd frontend && npm run lint -- src/modules/cases/pages/CaseCreate.vue src/modules/cases/components/CaseAgentSplitEditor.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh COMMSPLIT-FE-EDIT-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Reuse existing split editor instead of forking a new component
- [ ] Align create-page split validation with edit-page semantics
- [ ] Keep `second_agent_id` as context, not the primary split entry
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
