# PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01 — 第一阶段全流程演示脚本 UI 走查

## Story Shape Classification

| Dimension | Classification |
| --- | --- |
| shared_file_density | Low. Verification task file plus evidence only. |
| prereq_dependency_density | Medium. Requires local backend, frontend, P1 demo seed, and current browser page. |
| be_fe_coupling | Frontend-heavy verification. The task drives visible Vue pages against live backend state. |
| evidence_cost | Medium. Step-by-step UI observations, screenshots where useful, and task gate. |

## chosen_runbook

`P0-frontend-heavy-story`

## Closure

Strictly follow `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md` in the in-app browser, announcing each step and expected result before UI input, then executing the visible UI interaction and recording observed results.

## Exact Closure Slice

Execute the P1 lifecycle demo script through visible in-app browser UI steps against the local live backend, with step-by-step planned action, expected result, observed result, and evidence.

## Non-Closure

Do not modify backend, frontend, database schema, E2E tests, demo seed scripts, CPC/OA direct submission, RPA, signature automation, automatic payment, or email-sending behavior. If a product bug is found, record it as a finding instead of fixing it inside this task.

## Explicit Non-Closure

No product code, schema, automated official submission, RPA, signature automation, payment automation, email sending, or bug fix implementation.

## Allowlist

- `tasks/postdemo/PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01.md`
- `artifacts/PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01/**`

## Allowed Files

- `tasks/postdemo/PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01.md`
- `artifacts/PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01/**`

## Inputs

- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- Current backend and frontend implementation.

## Verification

- Start or confirm local backend and frontend services.
- Run the documented demo seed command before UI steps.
- Use the in-app browser for visible UI navigation and inputs.
- Record observed result for each completed script step.
- Run `./scripts/task_validate.sh PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01`.

## Verification Commands

- `curl -sS http://127.0.0.1:8000/healthz`
- `curl -sS http://127.0.0.1:5173`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`
- `./scripts/task_validate.sh PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01`

## Evidence Path

- `artifacts/PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01/**`

## Done Definition

- UI walkthrough has executed as far as live product state allows.
- Each executed step has a stated planned action, expected result, and observed result.
- Any gap or bug is recorded with page, expected behavior, and actual behavior.
- Evidence artifacts exist and task gate passes.

## Remaining Follow-Up Task IDs

None unless the walkthrough exposes a product bug or missing demo fixture.
