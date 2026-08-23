# Story DEMO-V5-DOCUMENT-ACTIVITY-LABELS

- Status: `READY_FOR_REVIEW`
- Risk: `PROTECTED` because this changes customer-visible evidence-lineage presentation while
  preserving every stored and API fact.
- Outcome: the V5 customer case page shows Simplified Chinese activity labels in the document
  evidence lane and never exposes the raw `activity_type` value there.
- Authority: `DEC-CUSTOMER-DEMO-PRESENTATION-BOUNDARY-20260822` plus the customer's explicit
  approval on 2026-08-23 of the bounded `DocumentEvidenceLane` remediation.
- Catalog IDs: none; this is a local V5 customer-presentation correction.
- Dependency: customer-demo candidate `6de62bf52b63c47336b2dc5ac8362bce4e9a2f69`.

## Closure

- Translate the activity types exercised by the V5 lifecycle into customer-readable Simplified
  Chinese at render time.
- Use a neutral Chinese fallback for an unknown activity type instead of exposing its raw value.
- Preserve all activity values returned by the lifecycle-overlay API.

## Non-goals

- No backend, API, database, lifecycle, deadline, fee, evidence, permission or security change.
- No translation or redesign of roles, version states, review states, package facts, receipts,
  tasks, other lanes or other pages.
- No shared label registry, i18n framework, refactor, retry behavior or adjacent cleanup.

## Owned paths

- `docs/product/v8/stories/DEMO-V5-DOCUMENT-ACTIVITY-LABELS.md`
- `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`

## Verification

- RED then GREEN:
  `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-overlay-document-lane.spec.ts --workers=1`
- Scoped ESLint:
  `cd frontend && npx eslint src/modules/cases/components/DocumentEvidenceLane.vue --max-warnings 0`
- Scoped diff check for the three owned paths.
- Live browser verification on case `CYIP-CN-INV-20260823-01`: Chinese activity labels are visible,
  raw activity codes are absent, central lifecycle facts remain unchanged, and no `Network Error`
  occurs on reload.
- Independent High review of the exact commit with `P0/P1/P2 = 0/0/0`.

## Rollback

Revert the exact story commit. This restores only the prior activity-label presentation and does
not mutate API or database facts.

## Candidate evidence

- RED: the focused Playwright test failed because the Chinese activity label was absent; the
  unknown-value tranche separately failed while the raw enum was still rendered.
- GREEN: both focused Playwright cases passed; scoped ESLint, frontend typecheck and scoped diff
  check returned zero.
- Live V5 case: 41 activity rows rendered, zero raw activity-type rows, all four central lifecycle
  facts remained visible, and no `Network Error` or loading failure was present after reload.
