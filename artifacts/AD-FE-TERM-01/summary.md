# AD-FE-TERM-01 Summary

## Task
- `tasks/afterdemon/AD-FE-TERM-01.md` as defined by `tasks/afterdemon/AFTERDEMO-TERM-ALIGNMENT_PLAN.md`

## Scope
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/src/modules/cases/components/CaseClaimsTab.vue`

## Changes
- Changed the case-detail tab label from `权利要求` to `申请人/发明人` through the shared Chinese label table.
- Updated the related placeholder copy so it no longer refers to claim content.
- Added a matching top-level title in the tab content to keep the visible page title aligned with the tab name.

## Verification
- `npm run lint` -> `0`
- `npm run typecheck` -> `0`
- `npm run build` -> `0`

## Runtime Expectation
- The case detail tab no longer mislabels applicant/inventor information as claims.
- Visible terminology in the touched scope is Simplified Chinese and matches the actual business object shown on screen.
