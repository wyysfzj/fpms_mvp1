# DEMO-FE-CN-01 Summary

## Task
- `tasks/dmmo/DEMO-FE-CN-01.md` as defined by `tasks/dmmo/DEMO_CN_UI.md`

## Scope
- `frontend/src/constants/displayText.ts`
- `frontend/src/constants/workflow.ts`

## Changes
- Added missing Chinese labels for case statuses:
  - `ACCEPTED`
  - `PENDING`
  - `GRANT_PENDING`
  - `WITHDRAWN`
  - `ABANDONED`
  - `EXPIRED`
- Added workflow mappings for those statuses so case list, case detail, and stepper no longer fall back to raw English codes.
- Updated case-status tag classification so the newly mapped statuses render with stable visual grouping.

## Verification
- `npm run lint` -> `0`
- `npm run typecheck` -> `0`
- `npm run build` -> `0`

## Runtime Expectation
- Case legal status now displays Simplified Chinese instead of raw English codes such as `GRANT_PENDING`.
- Shared rendering paths using `getCaseStatusText()` / `getCaseWorkflow()` no longer leak English for the covered statuses.
