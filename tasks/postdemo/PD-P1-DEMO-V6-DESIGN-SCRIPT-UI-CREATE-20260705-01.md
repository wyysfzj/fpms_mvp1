# PD-P1-DEMO-V6-DESIGN-SCRIPT-UI-CREATE-20260705-01

## Story Shape Classification

- shared_file_density: Medium. This task edits the shared lifecycle demo design and script documents only.
- prereq_dependency_density: Low. It depends on the V5 demo result and current V6 user correction.
- be_fe_coupling: Low. No product code is changed.
- evidence_cost: Low. Verification is document grep, diff check, and task gate.
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Update the P1 lifecycle demo design and script so V6 starts with live UI customer creation at `/clients/new`, then live UI case creation at `/cases/new`, and only allows downstream enrichment after those UI-created records exist.

## Explicit Non-Closure

Do not write product code, seed helpers, UI E2E tests, CPC/OA direct submit, RPA,扫码签名, 自动缴费, or 龙虾邮件自动发送.

## Remaining Follow-Up Task IDs

- PD-P1-DEMO-V6-CLEANUP-ENRICHMENT-20260705-01
- PD-P1-DEMO-V6-UI-E2E-RUN-20260705-01

## Allowed Files

- tasks/postdemo/PD-P1-DEMO-V6-DESIGN-SCRIPT-UI-CREATE-20260705-01.md
- docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md
- docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md
- artifacts/PD-P1-DEMO-V6-DESIGN-SCRIPT-UI-CREATE-20260705-01/**

## Verification Commands

- rg -n "V6|/clients/new|/cases/new|现场创建|后置 enrichment|案件业务状态|法律状态|工作包/文件状态|费用节点状态" docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md
- git diff --check
- ./scripts/task_validate.sh PD-P1-DEMO-V6-DESIGN-SCRIPT-UI-CREATE-20260705-01

## Evidence Path

- artifacts/PD-P1-DEMO-V6-DESIGN-SCRIPT-UI-CREATE-20260705-01/**

## Done Definition

- V6 section exists in both design and script documents.
- V6 explicitly states that customer and case are created through UI during the demo.
- V6 enrichment is documented as downstream-only and must not create or overwrite customer or case base fields.
- Verification commands pass and evidence is finalized.
