# PD-P1-FILING-EVIDENCE-NOTE-I18N-20260704-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low

## chosen_runbook

`P0-frontend-heavy-story`

## Closure Slice

The filing-preparation demo page displays external-operation evidence notes in Simplified Chinese business language instead of raw `occurred_at=...; note=...` key/value text.

## Non-Closure

No backend storage/API changes, no lifecycle status changes, no CPC/OA direct submit, no RPA, no signature/scan automation, no automatic payment.

## Allowlist

- `frontend/src/modules/cases/pages/FilingPreparation.vue`
- `frontend/src/modules/cases/components/FilingPackageChecklist.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `artifacts/PD-P1-FILING-EVIDENCE-NOTE-I18N-20260704-01/**`

## Verification

- Targeted live E2E for filing preparation.
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit`
- `./scripts/task_validate.sh PD-P1-FILING-EVIDENCE-NOTE-I18N-20260704-01`

## Done Definition

- After recording import time, visible filing-preparation text contains `操作时间` and `说明`.
- Visible filing-preparation text does not contain raw `occurred_at=` or `note=` keys.

## Remaining Follow-Up Task IDs

- `PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01`
