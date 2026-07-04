# PD-P1-DEMO-LEARNINGS-RUNBOOK-20260704-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: none
- evidence_cost: low

## chosen_runbook

`P0-single-lane-story`

## Closure Slice

Capture reusable lessons from the P1 demo fix/rerun/fix loop as two focused documents: a host-facing demo execution runbook and an engineering-facing demo verification checklist.

## Non-Closure

No product code changes, no E2E implementation changes, no seed script changes, no new demo scope, and no rewrite of existing P1 FS or lifecycle demo script.

## Allowlist

- `docs/postdemo/p1_demo_execution_runbook.md`
- `docs/postdemo/p1_demo_engineering_checklist.md`
- `tasks/postdemo/PD-P1-DEMO-LEARNINGS-RUNBOOK-20260704-01.md`
- `artifacts/PD-P1-DEMO-LEARNINGS-RUNBOOK-20260704-01/**`

## Verification

- `test -s docs/postdemo/p1_demo_execution_runbook.md`
- `test -s docs/postdemo/p1_demo_engineering_checklist.md`
- `rg -n "法律状态|工作包状态|费用状态|文件驱动|demo:p1:seed|Task Gate" docs/postdemo/p1_demo_execution_runbook.md docs/postdemo/p1_demo_engineering_checklist.md`
- `./scripts/task_validate.sh PD-P1-DEMO-LEARNINGS-RUNBOOK-20260704-01`

## Done Definition

- The host runbook explains how to demo one patent case as a status/file/fee story in customer-facing Chinese.
- The engineering checklist captures seed/cleanup, UI wording, visible E2E, atomic bugfix, and evidence gate lessons from the rerun.
- Both documents reference the existing lifecycle demo script and relevant evidence paths without duplicating the whole script.

## Remaining Follow-Up Task IDs

None.
