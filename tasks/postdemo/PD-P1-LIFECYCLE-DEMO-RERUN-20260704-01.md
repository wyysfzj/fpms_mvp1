# PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

`P0-frontend-heavy-story`

## Closure Slice

Run the full P1 lifecycle demo visibly in the in-app browser after fixes, announcing each step and expected result before UI input, then record screenshots, observations, and PASS/BLOCKED status.

## Non-Closure

No product code fixes in this task. If a new bug appears, file a new atomic implementation task and stop the rerun task as BLOCKED.

## Allowlist

- `artifacts/PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01/**`
- `tasks/postdemo/PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01.md`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`
- Start backend and frontend locally.
- Visible browser walkthrough for `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`.
- `./scripts/task_validate.sh PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01`

## Done Definition

- The user can visibly observe UI interactions.
- Each step records planned action, expected result, and observed result.
- Legal status, workflow status, fee status, and file-driven status changes are explained in Chinese.
- No user-visible English/internal code remains in the demo path.

## Remaining Follow-Up Task IDs

None.
