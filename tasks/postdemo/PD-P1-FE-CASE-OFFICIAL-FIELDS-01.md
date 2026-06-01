# PD-P1-FE-CASE-OFFICIAL-FIELDS-01 — Case official fields and new-case gates UI

## Exact Closure Slice

Update existing case create/edit/detail surfaces to maintain applicant/inventor official fields and show the new-case technical disclosure mandatory gate plus conditional commission instruction gate.

## Explicit Non-Closure

No backend code. No filing preparation page. No document conversion/upload overhaul. No unrelated case UI redesign.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-FILING-PREP-01`
- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `tasks/postdemo/PD-P1-FE-CASE-OFFICIAL-FIELDS-01.md`
- `artifacts/PD-P1-FE-CASE-OFFICIAL-FIELDS-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke: case create and case edit official field sections render with Simplified Chinese labels.
- `./scripts/task_validate.sh PD-P1-FE-CASE-OFFICIAL-FIELDS-01`

## Evidence Path

- `artifacts/PD-P1-FE-CASE-OFFICIAL-FIELDS-01/`

## Acceptance

- Applicant/inventor official fields are editable where case applicant/inventor data is already maintained.
- Stable official fields are not represented as filing-package补录.
- Technical disclosure and commission instruction gates are visible separately from official filing file roles.
