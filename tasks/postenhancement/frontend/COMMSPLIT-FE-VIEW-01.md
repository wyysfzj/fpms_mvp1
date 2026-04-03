# COMMSPLIT-FE-VIEW-01 — case detail split viewing

- Source: `docs/superpowers/plans/2026-04-03-commission-split-fe-view-detail.md`
- Type: `page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在 `CaseDetail.vue` 中补齐只读的 `代理人分摊` 展示，使 detail 页能够以 `agent_splits` 作为多代理 split 的主要可见载体。
- Exact closure slice:
  - 更新 `frontend/src/modules/cases/pages/CaseDetail.vue`
- Explicit non-closure:
  - 不做编辑能力
  - 不做 settlement read-only exposure
  - 不做 list 页面展示
  - 不做 router/menu changes
  - 不做 backend/API/types changes
- Remaining follow-up task ids:
  - `COMMSPLIT-QA-09`
- Allowlist:
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `tasks/postenhancement/frontend/COMMSPLIT-FE-VIEW-01.md`
  - `tasks/postenhancement/frontend/COMMSPLIT-QA-09.md`
- Verification:
  - `cd frontend && npm run lint -- src/modules/cases/pages/CaseDetail.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh COMMSPLIT-FE-VIEW-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add a Simplified Chinese `代理人分摊` read-only block
- [ ] Render `agent / role / share_ratio`
- [ ] Keep `primary_agent_id / second_agent_id` visible as context only
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files if needed
