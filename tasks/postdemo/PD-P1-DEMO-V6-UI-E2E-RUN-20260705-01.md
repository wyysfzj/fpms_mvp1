# PD-P1-DEMO-V6-UI-E2E-RUN-20260705-01

## Story Shape Classification

- shared_file_density: Medium. This task records demo run evidence and may create a runbook.
- prereq_dependency_density: High. It depends on V6 design/script and V6 cleanup/enrichment helper.
- be_fe_coupling: Medium. It exercises live Vue pages and live backend.
- evidence_cost: High. It requires visible browser execution, screenshots or traces when available, and task gate.
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Execute the V6 lifecycle demo through the live UI. Step 1 creates the V6 customer in `/clients/new`; Step 2 creates the V6 case in `/cases/new`; later steps run downstream enrichment, traverse the P1/P1.5 workflow, and write the successful step-by-step runbook.

## Explicit Non-Closure

Do not implement CPC/OA direct submit, RPA,扫码签名, 自动缴费, 龙虾邮件自动发送, or P2/P3 external integration. Do not delete real data or non-allowlisted records.

## Remaining Follow-Up Task IDs

None

## Allowed Files

- tasks/postdemo/PD-P1-DEMO-V6-UI-E2E-RUN-20260705-01.md
- docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md
- artifacts/PD-P1-DEMO-V6-UI-E2E-RUN-20260705-01/**

## Verification Commands

- cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:v6:cleanup
- cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:v6:enrich
- git diff --check
- ./scripts/task_validate.sh PD-P1-DEMO-V6-UI-E2E-RUN-20260705-01

## Evidence Path

- artifacts/PD-P1-DEMO-V6-UI-E2E-RUN-20260705-01/**

## Done Definition

- The user can observe the browser create the V6 customer and V6 case through UI.
- Each demo step has a Chinese Step Brief before UI input.
- Status changes are explicitly called out for case business status, legal status, work package/file status, and fee-node status.
- The V6 successful runbook is written to docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md.
- Required verification and evidence are complete.
