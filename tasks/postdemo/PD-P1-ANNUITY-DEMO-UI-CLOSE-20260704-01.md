# PD-P1-ANNUITY-DEMO-UI-CLOSE-20260704-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

`P0-frontend-heavy-story`

## Closure Slice

Close the P1 demo annuity UI gap: the annuity generation dialog resolves a typed case number to the real case id before submit, and case pages label `first_annuity_year` as a patent-year sequence instead of an ambiguous calendar year.

## Non-Closure

No backend schema changes, no annuity service algorithm changes, no fee draft generation changes, no automatic payment.

## Allowlist

- `frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `artifacts/PD-P1-ANNUITY-DEMO-UI-CLOSE-20260704-01/**`

## Verification

- Visible browser check of annuity generation dialog with `P1E2E-LIVE`.
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `./scripts/task_validate.sh PD-P1-ANNUITY-DEMO-UI-CLOSE-20260704-01`

## Done Definition

- Typing `P1E2E-LIVE` in the generation dialog results in a real case id submit, not a no-op string submit.
- Case UI labels explain the value as `首年年费序号（第几年）`.

## Remaining Follow-Up Task IDs

None.
