# FPMS-DEMO-V6-UI-PARITY-GOV-PAYMENT-MONEY-20260827-08AK

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "api", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GOV-PAYMENT-MONEY-20260827-08AK.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Make the existing V6 visible official-payment command send the displayed planned amount as the
backend-required positive decimal string with exactly two fractional digits.

## Exact Behavior

- `createDemoGovPaymentCommand` preserves the existing payload and converts only `paid_amount` to
  an exact two-decimal string before POST.
- The Stage 09 visible value `50` is sent as `"50.00"`; existing string `"900.00"` remains
  `"900.00"`.
- No fee amount, source, status, endpoint, retry, idempotency, or evidence semantics change.

## Explicit Non-Closure

- No backend/schema/model/migration/seed change; no generic money utility, form redesign, endpoint
  relaxation, adjacent API cleanup, Stage 10/11 work, or broad test.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GOV-PAYMENT-MONEY-20260827-08AK.md`
- `frontend/src/api/govPayments.ts`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-GOV-PAYMENT-MONEY-20260827-08AK/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-fee-ui-parity-contract.mjs
(cd frontend && npx eslint src/api/govPayments.ts)
(cd frontend && npm run typecheck)
git diff --check -- frontend/src/api/govPayments.ts frontend/tests/demo-v6-fee-ui-parity-contract.mjs tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GOV-PAYMENT-MONEY-20260827-08AK.md
```

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-GOV-PAYMENT-MONEY-20260827-08AK/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Done Definition

The focused contract fails before the fix, passes after the minimal conversion, scoped lint,
typecheck, scope, independent zero-finding review, task gate, and atomic evidence pass.

## Rollback

Run `git revert --no-edit <accepted-task-sha>` and resume Task 08 from Stage 09.
