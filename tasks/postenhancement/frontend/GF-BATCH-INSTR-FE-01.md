# GF-BATCH-INSTR-FE-01 — grant-fee batch PAY / ABANDON page path

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-batch-instruction.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在授权费任务看板上补上多选与批量 `PAY / ABANDON` 用户路径，使 `SPEC 5.7.2` 的批量客户指示要求变成真实可用的页面行为。
- Exact closure slice:
  - 更新前端 API contract
  - 在 grant-fee 页面加入 selection
  - 提供批量 `PAY / ABANDON` 操作和成功后刷新
- Explicit non-closure:
  - 不做通知函生成
  - 不做 detail/edit
  - 不做 bill generation
  - 不做 batch draft generation
- Remaining follow-up task ids:
  - `GF-BATCH-INSTR-QA-01`
- Allowlist:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `cd frontend && npm run typecheck`

## Execution Checklist

- [ ] Add batch instruction API client and types
- [ ] Add row selection to the grant-fee table
- [ ] Replace placeholder batch state action with real PAY / ABANDON path
- [ ] Refresh worklist and clear selection after success
