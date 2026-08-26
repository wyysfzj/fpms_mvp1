# FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "api", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07.md
Chosen runbook: `P0-frontend-heavy-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`,
  Task 07 only, under the active lean overlay.
- Accepted Ordinal 06 HEAD: `74af5e066950890527c15a21e477c475c653d5c6`.

## Exact Closure Slice

Close only the visible normal-UI Stage 10 bill, customer receipt, and offset inputs needed for two
partial settlements of one SERVICE bill. Reuse the existing V6 session, billing pages, command
wrappers, endpoints, idempotency reconciliation, and authoritative server responses.

## Exact Behavior

1. Only during a validated V6 UI session, BillCreate visibly identifies one eligible locked SERVICE
   draft and accepts visible `bill_no`, `bill_date`, and `due_date`. Submission reuses
   `createDemoBill` and `/bills/demo-from-draft`; a GOV draft is never accepted as the SERVICE bill.
2. PaymentCreate visibly accepts and submits the selected bill, exact user-entered amount, `pay_no`,
   `pay_date`, CNY, `BANK_TRANSFER`, `bank_ref_no`, and remark. The narrow V6 path reuses
   `createDemoBankReceipt` and `/payments/demo-bank-receipts`; the wrapper must use the visible amount
   instead of silently replacing it with total bill amount or balance.
3. PaymentList visibly accepts the selected payment line, current bill, exact offset amount, and
   `offset_date`, and reuses `createDemoFullOffset` with `/offsets/demo-full`. Registering a receipt
   does not change bill balance; only a successful offset does.
4. First receipt and offset are exactly CNY 1,200.00 and yield authoritative
   `PARTIALLY_SETTLED` with visible balance 600.00. The second receipt amount may be populated only
   from a freshly read visible 600.00 bill balance; its offset yields `SETTLED` with balance 0.00.
5. Parsers accept and strictly validate `UNSETTLED`, `PARTIALLY_SETTLED`, and `SETTLED` balance
   invariants. Payment parsing validates the visible submitted amount, not the original bill total.
   Offset parsing validates both partial and final authoritative bill/line/receipt results.
6. Bill, payment, and offset each retain one independent APP-generated idempotency key. Existing
   GET-first/unknown-result reconciliation remains: commit-drop reads by key before at most one
   retry, exact replay returns the same object, and same-key payload drift remains 409/no-write.
7. Outside the validated V6 session, all standard endpoints, fields, response/error semantics, and
   normal forms remain unchanged. New visible text is Simplified Chinese and no presenter-facing raw
   internal-ID input is added.

## Explicit Non-Closure

- No backend/service/model/schema/migration/seed/source/rate/amount/state-machine/permission change;
  no new endpoint, alternate finance workflow, automatic offset, hidden demo control, raw-ID field,
  Stage 11 write, broad Playwright, release, or post-demo security task.
- Do not refactor adjacent billing lists/forms, change standard non-V6 payloads, infer a SERVICE
  obligation from GOV data, or absorb unrelated status translation/styling/cleanup.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07.md`
- `frontend/src/modules/billing/pages/BillCreate.vue`
- `frontend/src/modules/billing/pages/PaymentCreate.vue`
- `frontend/src/modules/billing/pages/PaymentList.vue`
- `frontend/src/api/billing.ts`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/tests/demo-v6-billing-ui-parity-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-billing-ui-parity-contract.mjs
node frontend/tests/demo-abc-finance-decoder.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/billing/pages/BillCreate.vue \
  src/modules/billing/pages/PaymentCreate.vue src/modules/billing/pages/PaymentList.vue \
  src/api/billing.ts src/modules/demo/demo.api.ts src/modules/demo/demo.contract.ts)
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python -m pytest -q \
  tests/test_demo_abc_unique_ar_bill.py tests/test_demo_abc_payment_offset.py \
  -k 'not test_demo_bill_requires_locked_draft_and_creates_no_rows and not test_demo_bill_is_exactly_once_and_billed_draft_cannot_unlock and not test_demo_bill_dates_are_explicit_and_ordered')
git diff --check
```

Baseline variance: the frozen `node frontend/tests/demo-abc-command-reconcile.mjs` is run and
recorded separately with expected rc 1. Its accepted-base file SHA-256 is
`811eb5a2c85a328f2a57d26f59a9e7e71b29549eacb90f143de316b53b0bd2ae`; it still requires the
unknown-command guard to be inlined in `demo.api.ts`, while the accepted base owns the exact guard
in `command-reconcile.ts`. This task must not duplicate that helper or modify the stale test. The new
executable contract must dynamically preserve bill/payment/offset reconciliation and drift behavior.

Backend baseline variance: all three tests in `test_demo_abc_unique_ar_bill.py` share the unchanged
`_locked_demo_draft` fixture, which still sends removed `item_code` to
`/fees/demo-service-obligations`; the accepted endpoint schema forbids that extra field with 422.
The test blob is identical at accepted base and task HEAD
(`d5da1191ec166829b2473d93cfbde2f3dda77570`). Their original rc 1 result remains recorded
separately; the frontend-only task must not change backend or stale tests. Every test in
`test_demo_abc_payment_offset.py` remains required by the adjusted focused command.

GREEN must dynamically prove SERVICE-only draft selection; all visible bill/payment/offset fields;
first `1200.00` receipt/offset to `PARTIALLY_SETTLED/600.00`; refreshed visible balance feeding only
the second `600.00`; final `SETTLED/0.00`; no balance change on receipt alone; three distinct
idempotency keys; commit-drop GET-first recovery, exact replay, drift zero-write; invalid or stale
visible projection zero mutation. Independent review binds the exact task range.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-JOURNEY-20260826-08`, blocked until this task is accepted.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, deferred until after the demo.

## Done Definition

Stage 10 executes twice through visible normal billing UI and ends with the one SERVICE bill settled
from 1,800.00 to 600.00 to 0.00, while authoritative finance/reconciliation semantics remain
unchanged. Focused frontend/backend tests, typecheck, scoped ESLint, diff/scope, independent zero-
finding review, and atomic evidence pass.

## Rollback

Run `git revert --no-edit <accepted-task-range>`. Ordinal 06 remains accepted; Ordinal 08 stays
blocked.
