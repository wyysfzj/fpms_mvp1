# FPMS V8 Inherited Format-Letter Error Locator Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Keep the inherited format-letter retry proof stable after the independently accepted grant-review
panel introduced a second dismiss button on DocumentDetail. The test must dismiss only the
format-letter panel's displayed API error and preserve the same operation-id retry assertions.

## Exact closure

- Scope the existing `✕` locator to `.letter-handoff-panel .error-banner`.
- Run the exact affected Playwright spec with one worker.

## Non-closure

- No product/UI/runtime change, assertion weakening, skip or xfail.
- No change to request count, request body, retry identity or evidence-result assertions.
- No Row281 adoption, Row282/283 or release work.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-FORMAT-LETTER-ERROR-LOCATOR-TEST-ALIGNMENT-20260813-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-format-letter-in-source-ui.spec.ts`

## Verification

```text
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-format-letter-in-source-ui.spec.ts --workers=1
git diff --check -- <exact allowlist>
```

Independent High review with P0/P1/P2 `0/0/0` is required before Row281 consumes this alignment.
