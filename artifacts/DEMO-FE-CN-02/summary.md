# DEMO-FE-CN-02 Summary

## Task
- `tasks/dmmo/DEMO-FE-CN-02.md` as defined by `tasks/dmmo/DEMO_CN_UI.md`

## Scope
- `frontend/src/modules/cases/pages/CaseEdit.vue`

## Changes
- Replaced the hard-coded legal-status options with a shared Chinese-label-driven options list.
- Added explicit handling for workflow-driven statuses:
  - `ACCEPTED`
  - `GRANT_PENDING`
- Workflow-driven statuses now render as Simplified Chinese read-only options in the edit form.
- Added a Chinese hint explaining that workflow/document-driven statuses are display-only in the edit page.
- Prevented read-only workflow statuses from being sent back during save, reducing contract mismatch risk when editing other fields.

## Verification
- `npm run lint` -> `0`
- `npm run typecheck` -> `0`
- `npm run build` -> `0`

## Runtime Expectation
- Case edit legal-status selector is fully Simplified Chinese.
- If a case currently sits in a workflow-driven status such as `GRANT_PENDING`, the page shows a Chinese read-only option instead of exposing an inconsistent editable English/raw-code state.
