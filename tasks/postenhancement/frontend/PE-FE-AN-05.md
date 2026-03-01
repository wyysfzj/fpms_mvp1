# PE-FE-AN-05 — 官费清单 + 缴费登记页面。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：官费清单 + 缴费登记页面。
- Allowlist:
  - `frontend/src/api/govPayments.ts` (new)
  - `frontend/src/api/govPayments.types.ts` (new)
  - `frontend/src/modules/annuity/pages/PayList.vue` (new)
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue` (new)
- 依赖：PE-BE-AN-06, PE-BE-AN-07
- 验收：清单可查、缴费可录、状态可见。
- 验证：`npm run lint && npm run typecheck`

---

## FE-B2 — Dunning / Bad Debt

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
