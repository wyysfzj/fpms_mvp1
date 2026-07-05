# PD-P1-DEMO-V5-DESIGN-SCRIPT-STATUS-20260705-01

## Design References

- `AGENTS.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- `artifacts/PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01/summary.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Update the P1 lifecycle demo design and script with a V5 section that starts from a new demo customer and new demo case, retains one old V4 demo dataset for comparison, and explicitly explains case business status, legal status, work package/file status, and fee node status at each demo stage.

## Explicit Non-Closure

Do not write product code, seed scripts, UI tests, backend tests, database migrations, CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, or Longxia email automation. Do not execute the UI demo in this task.

## Allowed Files

- `tasks/postdemo/PD-P1-DEMO-V5-DESIGN-SCRIPT-STATUS-20260705-01.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `artifacts/PD-P1-DEMO-V5-DESIGN-SCRIPT-STATUS-20260705-01/**`

## Verification Commands

- `rg -n "V5|CLIENT-PD-P1-V5-LIVE|P1E2E-V5-LIVE|案件业务状态|法律状态|工作包/文件状态|费用节点状态|保留一套旧演示数据" docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `git diff --check -- docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md tasks/postdemo/PD-P1-DEMO-V5-DESIGN-SCRIPT-STATUS-20260705-01.md`
- `./scripts/task_validate.sh PD-P1-DEMO-V5-DESIGN-SCRIPT-STATUS-20260705-01`

## Done Definition

- V5 design states that `P1E2E-LIVE` / `CLIENT-PD-P1-LIVE` is retained as the old comparison dataset.
- V5 design states that the new demo starts from `CLIENT-PD-P1-V5-LIVE` and `P1E2E-V5-LIVE`.
- V5 script includes a status-change table covering case business status, legal status, work package/file status, and fee node status.
- V5 script includes cleanup/seed command and no-wildcard deletion rule.
- Required evidence exists under `artifacts/PD-P1-DEMO-V5-DESIGN-SCRIPT-STATUS-20260705-01/**`.

## Remaining Follow-Up Task IDs

- `PD-P1-DEMO-V5-SEED-CLEANUP-NEW-CASE-20260705-01`
- `PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01`
