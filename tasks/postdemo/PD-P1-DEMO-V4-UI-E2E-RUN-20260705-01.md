# PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01

## Design References

- `AGENTS.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.html`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- Current implementation for cases, documents, official workflows, tasks, fees, grant fees, annuity, templates, frontend, and E2E fixtures.

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-frontend-heavy-story`

## Exact Closure Slice

Execute the latest V4 FPMS demo script once through real UI pages with live backend, announce a Chinese Step Brief before each UI step, record actual UI observations, diagnose and split any blocking P1/P1.5 bug into a separate atomic task, and write the successful step runbook to `docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md`.

## Explicit Non-Closure

Do not implement CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, Longxia email automation, or P2/P3 integration. Do not delete real data. Do not modify product code inside this task; if a product bug blocks the demo, create a separate atomic task for that fix.

## Allowed Files

- `tasks/postdemo/PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01.md`
- `docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md`
- `artifacts/PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01/**`

## Demo Data Boundary

- Allowed seed command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`.
- The seed/cleanup must only target fixed P1 demo fixtures such as `P1E2E-LIVE`, `FILING-PD-P1-LIVE`, `OA-PD-P1-LIVE`, `FD-PD-P1-LIVE`, `DOC-LETTER-PD-P1-LIVE`, and known derived demo fee/pay-list records.
- No wildcard deletion of real or unknown data.

## UI Step Brief Contract

Before each visible UI action, output:

- 要做的内容
- 输入的字段和值
- 点击的按钮
- 期望结果
- 为什么要做
- UI 检查点

After each step, record:

- 实际 UI 结果
- 是否符合预期
- Screenshot or trace path when available
- Issue ID when not conforming

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`
- Browser-observed UI smoke through the V4 demo pages with live backend.
- `rg -n "Step 1|要做的内容|输入的字段和值|点击的按钮|期望结果|为什么要做|UI 检查点|实际 UI 结果|是否符合预期" docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md`
- `git diff --check -- docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md tasks/postdemo/PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01.md`
- `./scripts/task_validate.sh PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01`

## Done Definition

- Demo data is safely rebuilt from fixed demo fixtures.
- Each executed UI step has a Step Brief before action and observed result after action.
- The user can visually observe UI interactions in the in-app browser.
- Blocking P1/P1.5 bugs are recorded and either fixed through separate atomic tasks or the run is marked BLOCKED with evidence.
- Successful steps are written to `docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md`.
- Required evidence exists under `artifacts/PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01/**`.

## Evidence Path

- `artifacts/PD-P1-DEMO-V4-UI-E2E-RUN-20260705-01/**`

## Remaining Follow-Up Task IDs

None unless a blocking bug is discovered.
