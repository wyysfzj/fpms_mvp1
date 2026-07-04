# PD-P1-WORKFLOW-DEMO-I18N-RECEIPT-20260704-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

`P0-frontend-heavy-story`

## Closure Slice

P1 workflow/document/fee demo pages translate visible internal codes into Simplified Chinese business language and show recorded OA receipt metadata after saving.

## Non-Closure

No backend schema migration, no direct official submit, no RPA, no automatic payment.

## Allowlist

- `frontend/src/modules/cases/pages/FilingPreparation.vue`
- `frontend/src/modules/cases/components/FilingPackageChecklist.vue`
- `frontend/src/modules/documents/pages/OAReplyPackage.vue`
- `frontend/src/modules/documents/components/AttachmentList.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/pages/DocumentEdit.vue`
- `frontend/src/modules/officialWorkflows/components/FeeLinkagePanel.vue`
- `frontend/src/modules/officialWorkflows/components/ReceiptArchivePanel.vue`
- `frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue`
- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `artifacts/PD-P1-WORKFLOW-DEMO-I18N-RECEIPT-20260704-01/**`

## Verification

- Targeted DOM/text scan or Playwright assertion covering demo pages.
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `./scripts/task_validate.sh PD-P1-WORKFLOW-DEMO-I18N-RECEIPT-20260704-01`

## Done Definition

- Demo-visible internal codes listed in the previous walkthrough are translated or hidden behind Chinese labels.
- Override labels are Simplified Chinese.
- Receipt metadata saved by the user is visible in the receipt gate area after refresh.

## Remaining Follow-Up Task IDs

- `PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01`
