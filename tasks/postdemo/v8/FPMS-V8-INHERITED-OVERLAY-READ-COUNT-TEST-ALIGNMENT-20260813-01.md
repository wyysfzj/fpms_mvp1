# FPMS V8 Inherited Overlay Read Count Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Make the inherited gate/warning UI proof deterministic across the accepted CaseDetail canonical
route replacement. Whether Vue preserves or remounts the overlay component, every observed
overlay request must be the same read-only initial-page request, there may be at most the two
mounts, and no mutation may occur.

## Exact closure

- Record overlay GET URLs instead of only a scalar count.
- Require one or two reads, one unique URL, and exact initial cursor/limit/no revision parameters.
- Preserve all 29 identities, warnings, provenance, reference-only UI and zero-mutation assertions.

## Non-closure

- No product/router/UI change, skip, xfail or retry behavior.
- No acceptance of a distinct cursor, revision or mutation request.
- No Row281 adoption, Row282/283 or release work.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-OVERLAY-READ-COUNT-TEST-ALIGNMENT-20260813-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`

## Verification

```text
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-gates-warnings.spec.ts --workers=1
git diff --check -- <exact allowlist>
```

Independent High review with P0/P1/P2 `0/0/0` is required before Row281 consumes this alignment.
