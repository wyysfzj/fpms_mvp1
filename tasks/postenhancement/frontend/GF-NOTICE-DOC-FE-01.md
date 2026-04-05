# GF-NOTICE-DOC-FE-01 — grant-fee real notice generation page path

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-notice-document-implementation.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在授权费任务看板上补上真实 batch “生成通知函” 用户路径，使选中行可以生成真实通知文书并刷新内部通知状态。
- Exact closure slice:
  - 更新前端 API contract
  - 在 grant-fee 页面加入真实批量“生成通知函”
  - 成功后刷新并清空选择
- Explicit non-closure:
  - 不做 document detail page
  - 不做 dispatch UI
  - 不做 reminder generation
  - 不做 bill linkage
- Remaining follow-up task ids:
  - `GF-NOTICE-DOC-QA-01`
- Allowlist:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `cd frontend && npm run typecheck`

## Execution Checklist

- [ ] Add batch notice-generation API client and types
- [ ] Add real batch “生成通知函” entry on the grant-fee page
- [ ] Refresh worklist and clear selection after success
- [ ] Keep all user-facing text in Simplified Chinese
