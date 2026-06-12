# PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01 — Applicant total POA UI

## Exact Closure Slice

Add “总委托书备案编号” maintenance to the existing applicant masterdata list/dialog so staff can maintain the applicant/customer-level official number once and reuse it in cases.

## Explicit Non-Closure

No backend code. No case page redesign. No official workflow page changes. No CPC/OA direct submit.

## Remaining Follow-Up Task IDs

- `PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01`

## Allowed Files

- `frontend/src/api/masterdata.ts`
- `frontend/src/api/masterdata.types.ts`
- `frontend/src/modules/settings/pages/ApplicantList.vue`
- `tasks/postdemo/PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01.md`
- `artifacts/PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01/**`

## Verification Commands

- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke or component route smoke showing the field label in Simplified Chinese.
- `./scripts/task_validate.sh PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01`

## Acceptance

- Applicant table and edit/create dialog show `总委托书备案编号`.
- Create/update payloads include the value.
- Empty value remains optional because customers/applicants are not always assigned a total POA.
