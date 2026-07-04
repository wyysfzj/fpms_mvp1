# PD-P1-CASE-EDIT-GRANT-FIELDS-I18N-20260704-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

`P0-frontend-heavy-story`

## Closure Slice

The case edit page explicitly displays and saves P1 grant, annuity-monitoring, and customer fee-reduction fields with Simplified Chinese business labels, so the demo can show `0.85`, grant dates/numbers, valid-until, first annuity year, and fee monitoring without blank or misleading controls.

## Non-Closure

No backend schema changes, no lifecycle transition changes, no grant-fee/annuity generation changes.

## Allowlist

- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/api/cases.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `artifacts/PD-P1-CASE-EDIT-GRANT-FIELDS-I18N-20260704-01/**`

## Verification

- Targeted Playwright assertion for the case edit page fields, if stable after task 1.
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `./scripts/task_validate.sh PD-P1-CASE-EDIT-GRANT-FIELDS-I18N-20260704-01`

## Done Definition

- Case edit shows customer fee-reduction value as `0.85`, not a blank unmatched select option.
- Grant and annuity-monitoring fields are part of the explicit reactive form model.
- User-visible labels remain Simplified Chinese.

## Remaining Follow-Up Task IDs

- `PD-P1-WORKFLOW-DEMO-I18N-RECEIPT-20260704-01`
- `PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01`
