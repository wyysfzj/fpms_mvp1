# PD-P1-DEMO-V6-UI-CHINESE-CODE-FIX-20260705-01

## Story Shape Classification

- shared_file_density: Medium. The task touches existing P1 demo UI components and one live backend E2E spec.
- prereq_dependency_density: Medium. It depends on the V6 demo run exposing visible internal status codes.
- be_fe_coupling: Low. The fix is frontend display mapping only; backend contracts stay unchanged.
- evidence_cost: Medium. It requires targeted Playwright regression, typecheck, and task gate.
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Replace visible internal codes found during the V6 demo with Simplified Chinese display text on the OA reply, fee linkage, and letter handoff demo surfaces, and lock the behavior with targeted live-backend E2E assertions where the fixture cleanup allows.

## Explicit Non-Closure

Do not change backend APIs, database schema, fixture data, fee calculation, CPC/OA direct submit, RPA, automatic signature, automatic payment, or email sending.

## Remaining Follow-Up Task IDs

None

## Allowed Files

- tasks/postdemo/PD-P1-DEMO-V6-UI-CHINESE-CODE-FIX-20260705-01.md
- frontend/src/modules/documents/pages/OAReplyPackage.vue
- frontend/src/modules/officialWorkflows/components/FeeLinkagePanel.vue
- frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue
- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts
- artifacts/PD-P1-DEMO-V6-UI-CHINESE-CODE-FIX-20260705-01/**

## Verification Commands

- cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/pd-p1.live-backend.spec.ts -g "OA答复包文件角色|费用联动"
- cd frontend && npm run typecheck
- git diff --check
- ./scripts/task_validate.sh PD-P1-DEMO-V6-UI-CHINESE-CODE-FIX-20260705-01

## Evidence Path

- artifacts/PD-P1-DEMO-V6-UI-CHINESE-CODE-FIX-20260705-01/**

## Done Definition

- OA reply status `REPLY_DOCUMENT_LINKED` is displayed in Chinese.
- Fee linkage value `PARTIAL` is displayed in Chinese.
- Letter handoff attachment role `SOURCE_OFFICIAL_DOCUMENT` is displayed in Chinese.
- Targeted E2E assertions fail before the fix and pass after the fix.
- Required evidence artifacts and task gate are complete.
