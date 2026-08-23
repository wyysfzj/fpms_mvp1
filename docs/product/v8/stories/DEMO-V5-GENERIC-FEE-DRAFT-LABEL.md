# Story DEMO-V5-GENERIC-FEE-DRAFT-LABEL

- Risk: `PROTECTED` because this changes customer-visible fee-draft presentation while
  preserving every stored and API fact.
- Outcome: a `GENERIC` fee draft is shown as “普通费用草稿” instead of “未知草单类型”.
- Authority: the customer's explicit approval on 2026-08-23 of this bounded V5 demo
  presentation correction.

## Exact paths

- `docs/product/v8/stories/DEMO-V5-GENERIC-FEE-DRAFT-LABEL.md`
- `frontend/src/constants/displayText.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-draft-obligation.spec.ts`

## Observable contract

- `getFeeDraftTypeText('GENERIC')` returns “普通费用草稿”.
- Unknown fee-draft types continue to return “未知草单类型”.
- No API, database, fee calculation, amount, obligation, draft workflow or other label changes.

## Verification

- RED then GREEN:
  `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-fee-draft-obligation.spec.ts --workers=1`
- Scoped ESLint for `frontend/src/constants/displayText.ts`.
- Frontend typecheck and scoped diff check for the three exact paths.
- Live browser verification on draft `077684a4-3c53-43b0-a933-62a4cb5b7ae7`.
- Independent High review of the exact commit with `P0/P1/P2 = 0/0/0`.

## Rollback

Revert the exact story commit. This restores only the prior `GENERIC` display label.
