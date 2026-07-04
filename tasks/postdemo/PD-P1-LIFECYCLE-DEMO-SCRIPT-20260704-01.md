# PD-P1-LIFECYCLE-DEMO-SCRIPT-20260704-01 — 第一阶段全流程演示详细脚本

## Story Shape Classification

| Dimension | Classification |
| --- | --- |
| shared_file_density | Low. One new demo script document plus this task file and evidence. |
| prereq_dependency_density | Medium. Script depends on the approved lifecycle design, P1 FS, current routes, and demo seed evidence. |
| be_fe_coupling | None for this task. Documentation-only output, but the script references current frontend routes and visible fields. |
| evidence_cost | Low. Content and structure checks plus task gate. |

## chosen_runbook

`P0-single-lane-story`

## Closure

Generate a complete Chinese lifecycle demo script strictly based on the approved design, including mock data, pre-demo preparation, detailed page-by-page steps, demo field inputs, why each input is used, expected results, legal-status changes, work-package status changes, and field changes.

## Non-Closure

Do not modify backend, frontend, database, E2E tests, demo seed scripts, browser companion HTML, CPC/OA direct submission, RPA, signature automation, automatic payment, or email sending behavior.

## Allowlist

- `tasks/postdemo/PD-P1-LIFECYCLE-DEMO-SCRIPT-20260704-01.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `artifacts/PD-P1-LIFECYCLE-DEMO-SCRIPT-20260704-01/**`

## Inputs

- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.html`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_p1_e2e_demo_20260612.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- Current frontend routes/pages for cases, official workflows, fees, grant fees, annuity, pay-lists, and documents.

## Verification

- Content check: required sections, Chinese legal statuses, no forbidden English status codes as status wording.
- Structure check: each demo step includes action, input fields, reason, expected result, legal status, package/task status, and field changes.
- `./scripts/task_validate.sh PD-P1-LIFECYCLE-DEMO-SCRIPT-20260704-01`

## Done Definition

- New script document exists under `docs/postdemo`.
- Script is fully Chinese and customer-facing for all status wording.
- Script includes mock data, preparation checklist, seed/reset guidance, detailed demo steps, expected results, status changes, field changes, and boundary wording.
- Evidence artifacts exist and task gate passes.

## Remaining Follow-Up Task IDs

None.
