# FPMS-DEMO-V6-UI-PARITY-SERVICE-BILL-ITEMS-20260827-08AL

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "api", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-BILL-ITEMS-20260827-08AL.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Accept the current V6 adjusted SERVICE draft's complete one-or-more-line bill projection while
preserving strict SERVICE-only domain purity and exact item-total equality with the bill.

## Exact Behavior

- `parseDemoBillDetail` accepts one or more bill items instead of requiring exactly one.
- Every item remains a valid identified `SERVICE` item with a fee code and two-decimal amount.
- The sum of all item amounts must equal the bill amount; GOV or mixed-domain items still fail.

## Explicit Non-Closure

- No backend/schema/model/migration/seed change; no GOV billing; no parser relaxation outside bill
  item cardinality; no generic finance abstraction, page redesign, Stage 11, or broad test.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-BILL-ITEMS-20260827-08AL.md`
- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-SERVICE-BILL-ITEMS-20260827-08AL/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-fee-ui-parity-contract.mjs
(cd frontend && npx eslint src/modules/demo/demo.contract.ts)
(cd frontend && npm run typecheck)
git diff --check -- frontend/src/modules/demo/demo.contract.ts frontend/tests/demo-v6-fee-ui-parity-contract.mjs tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-BILL-ITEMS-20260827-08AL.md
```

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-SERVICE-BILL-ITEMS-20260827-08AL/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Done Definition

The focused contract proves multi-line equality and mismatch rejection, lint/typecheck/scope pass,
and independent zero-finding review accepts the exact minimal range.

## Rollback

Run `git revert --no-edit <accepted-task-range>` and resume Task 08 from Stage 10.
