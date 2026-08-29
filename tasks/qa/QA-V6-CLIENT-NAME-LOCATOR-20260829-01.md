# QA-V6-CLIENT-NAME-LOCATOR-20260829-01

Status: READY / CONTRACT FROZEN
Risk-Tier: MEDIUM
Closure-Tags: ["ui"]
Task-Path: tasks/qa/QA-V6-CLIENT-NAME-LOCATOR-20260829-01.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Scope the existing strict V6 Stage 01 customer-name visibility assertion to the customer detail
`基本信息` panel so the new breadcrumb copy does not create a Playwright strict-mode collision.

## Explicit Non-Closure

- No product, breadcrumb, customer, API, seed, runbook value, or business assertion change.
- No removal or weakening of the customer-name visibility assertion.
- No other strict locator cleanup.

## Allowed Files

- `tasks/qa/QA-V6-CLIENT-NAME-LOCATOR-20260829-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- `artifacts/QA-V6-CLIENT-NAME-LOCATOR-20260829-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
npx tsc --noEmit
```

```bash
git diff --check
```

After commit, rerun the complete strict V6 Stage 00–11 journey once.

## Stop Conditions

Stop if the change requires product code, changes the expected customer name, or weakens the
ordinary-UI strict journey.

## Remaining Follow-Up Task IDs

None.

## Evidence Path

`artifacts/QA-V6-CLIENT-NAME-LOCATOR-20260829-01/`
