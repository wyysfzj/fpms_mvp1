# FE-GRANT-FEE-PREVIEW-VIEWPORT-20260829-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "ui"]
Task-Path: tasks/frontend/FE-GRANT-FEE-PREVIEW-VIEWPORT-20260829-01.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Keep the existing authorization official-fee preview dialog and all of its source, line,
total, and read-only audit facts usable at the strict V6 1280x720 viewport. The dialog body
may scroll, but the existing `确认官费并生成草单` footer action must remain visible and be the
topmost hit target at its center point.

## Explicit Non-Closure

- No backend, API, database, fee amount, fee source, calculation, confirmation, draft,
  idempotency, or lifecycle behavior change.
- No removal or weakening of preview/audit content or strict Stage 07 assertions.
- No unrelated dialog, page, navigation, runbook, seed, or Demo input change.
- No retry or second product fix if the fresh strict journey reveals another failure.

## Allowed Files

- `tasks/frontend/FE-GRANT-FEE-PREVIEW-VIEWPORT-20260829-01.md`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-grant-official-fee-preview-viewport.spec.ts`
- `artifacts/FE-GRANT-FEE-PREVIEW-VIEWPORT-20260829-01/**`

## Observable Acceptance

1. At 1280x720, the official-fee preview dialog is visible and contained by the viewport.
2. Its body is independently scrollable when content exceeds the available height.
3. The existing confirm button is visible and `document.elementFromPoint()` at its center
   resolves to the button or one of its descendants.
4. Existing preview facts remain visible/readable by scrolling and the strict V6 Stage 07
   confirmation continues to use the ordinary UI and real API.
5. A fresh strict Stage 00-11 run from the final clean commit produces a PASS receipt with
   zero recorded network and console errors.

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
npx playwright test src/tests/v8-grant-official-fee-preview-viewport.spec.ts --workers=1
```

```bash
cd frontend
npm run typecheck
npx eslint src/modules/grantFees/pages/GrantFeeTaskList.vue --max-warnings 0
```

```bash
python3 scripts/run_demo_integrated_a_rehearsal.py --strict-ui \
  --profile TECHNICAL_REHEARSAL --artifact <fresh-absolute-artifact-path> --runs 1
```

## Stop Conditions

Stop without broadening scope if the fix requires fee/business changes, removal of audit
facts, modification of the strict Stage 07 assertion, or if the fresh strict run reaches a
different failure.

## Remaining Follow-Up Task IDs

None.

## Evidence Path

`artifacts/FE-GRANT-FEE-PREVIEW-VIEWPORT-20260829-01/`
