# FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "api", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06.md
Chosen runbook: `P0-frontend-heavy-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`,
  Task 06 only, under the active lean overlay.
- Accepted Ordinal 05 HEAD: `71fa8b8ac2ea9813e364aa7c15ffcda43bf91eaf`.

## Exact Closure Slice

Close only the remaining visible normal-UI Stage 07–09 inputs: expose the existing demo service-fee
obligation command on the current case fees page during a validated V6 UI session, and add safe
navigation after each official-payment registration. Reuse all existing grant preview/confirm,
PAY, draft, adjustment, lock, official pay-list, and payment-registration behavior.

## Exact Behavior

1. Stage 07 continues through the existing grant task preview and confirm controls without changes
   to its endpoint, source, amount, digest, confirmation, or lifecycle semantics.
2. Only while `isDemoUiSessionActive()` and `getDemoUiSession()` return the validated V6 session
   tuple, the current case fees page shows `生成服务费义务`. Clicking it first reads the validated
   demo service item, then calls the existing `createDemoServiceObligation` exactly once with the
   visible current case, returned item code, and one retained idempotency key. Outside that session
   the control is absent and the standard case-fees behavior is unchanged.
3. A successful create/reuse result must exactly match the visible case and validated service item,
   is shown in Simplified Chinese without asking the presenter for internal IDs, and refreshes the
   existing lifecycle overlay/draft view. Missing session, mismatched result, duplicate click while
   pending, or invalid service-item/result projection fails closed without a second mutation.
4. PAY, service/GOV draft creation, service adjustment, draft lock, pay-list creation, and existing
   official payment semantics remain on their current normal pages and existing endpoints.
5. After a successful official-payment registration, the existing result area exposes
   `登记下一行` only when the current pay-list context has another registrable row, plus
   `返回当前清单`. Navigation carries only the already-bound route context; it does not ask for or
   display internal IDs and does not issue a mutation.
6. Existing response, permission, recovery/replay, fee source, amount, adjustment, lock, and
   GovPayment semantics remain unchanged. New visible text is Simplified Chinese.

## Explicit Non-Closure

- No backend/service/model/schema/migration/seed/source/rate/amount/state-machine/permission change;
  no new endpoint, generic command framework, hidden control page, raw-ID input, Stage 10 billing,
  payment/offset parser change, Stage 11, broad Playwright, release, or post-demo security task.
- Do not refactor adjacent fee pages, redesign existing forms, add automatic multi-row payment, or
  absorb unrelated status translation/styling/cleanup.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06.md`
- `frontend/src/modules/cases/components/CaseFeesTab.vue`
- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-fee-ui-parity-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/cases/components/CaseFeesTab.vue \
  src/modules/annuity/pages/PayListDetail.vue src/modules/annuity/pages/GovPaymentCreate.vue \
  src/modules/demo/demo.api.ts)
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python -m pytest -q \
  tests/test_demo_v6_fee_ui_contract.py tests/test_demo_v6_gov_payment.py \
  tests/test_demo_v6_grant_official_fee.py)
git diff --check
```

Baseline variance: the frozen `node frontend/tests/demo-abc-command-reconcile.mjs` is run and
recorded separately with expected rc 1. Its test blob is identical at accepted base and task HEAD
(`811eb5a2c85a328f2a57d26f59a9e7e71b29549eacb90f143de316b53b0bd2ae`), but it still requires the
unknown-command guard to be inlined in `demo.api.ts`; the accepted base already owns that exact
guard in `command-reconcile.ts`. This task must not duplicate the helper or modify the non-allowlisted
stale test. The new executable contract remains responsible for proving that the Stage 08 wrapper
does not weaken existing reconciliation behavior.

GREEN must dynamically prove session-only visibility, GET-before-single-POST service-obligation
creation, exact case/item/result binding, pending double-click suppression, invalid/mismatched
zero-second-mutation behavior, unchanged command reconciliation, and mutation-free next-row/current-
list navigation. Independent review binds the exact task range.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07`, blocked until this task is accepted.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, deferred until after the demo.

## Done Definition

Stages 07–09 run through visible normal UI with one validated-session service-obligation entry and
safe official-payment navigation, while all authoritative fee semantics remain unchanged. Focused
frontend/backend tests, typecheck, scoped ESLint, diff/scope, independent zero-finding review, and
atomic evidence pass.

## Rollback

Run `git revert --no-edit <accepted-task-range>`. Ordinal 05 remains accepted; Ordinal 07 stays
blocked.
