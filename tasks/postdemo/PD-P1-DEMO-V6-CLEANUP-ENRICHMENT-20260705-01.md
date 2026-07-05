# PD-P1-DEMO-V6-CLEANUP-ENRICHMENT-20260705-01

## Story Shape Classification

- shared_file_density: Medium. This task edits the shared Playwright demo helper and package scripts.
- prereq_dependency_density: Medium. Enrichment requires the UI-created V6 customer and case to exist.
- be_fe_coupling: Low. This task changes test support code, not product UI.
- evidence_cost: Medium. It requires red/green helper verification and typecheck.
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement safe V6 demo cleanup and downstream enrichment helpers. Cleanup may delete only explicit V6 demo fixture identifiers. Enrichment must fail before the UI-created V6 customer and case exist, then read those records and create only downstream demo work packages, documents, attachments, fee drafts, pay-lists, grant-fee tasks, annuity tasks, and task records.

## Explicit Non-Closure

Do not precreate or overwrite the V6 customer, V6 case, V6 case applicants, V6 case inventors, customer base fields, case base fields, CPC/OA direct submit, RPA,扫码签名, 自动缴费, or 龙虾邮件自动发送.

## Remaining Follow-Up Task IDs

- PD-P1-DEMO-V6-UI-E2E-RUN-20260705-01

## Allowed Files

- tasks/postdemo/PD-P1-DEMO-V6-CLEANUP-ENRICHMENT-20260705-01.md
- FPMS_Automation_Skeleton_Pack/playwright_ts/package.json
- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py
- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts
- artifacts/PD-P1-DEMO-V6-CLEANUP-ENRICHMENT-20260705-01/**

## Verification Commands

- cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit
- cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run test:pd-p1:v6
- git diff --check
- ./scripts/task_validate.sh PD-P1-DEMO-V6-CLEANUP-ENRICHMENT-20260705-01

## Evidence Path

- artifacts/PD-P1-DEMO-V6-CLEANUP-ENRICHMENT-20260705-01/**

## Done Definition

- V6 cleanup command exists and only targets explicit V6 demo IDs.
- V6 enrichment command exists and refuses to run without UI-created customer and case.
- V6 enrichment leaves customer and case base fields unchanged.
- Targeted verification passes and evidence is finalized.
