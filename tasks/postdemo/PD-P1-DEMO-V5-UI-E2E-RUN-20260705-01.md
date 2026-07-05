# PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01

## Design References

- `AGENTS.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- Current Vue pages and live backend for cases, clients, documents, official workflows, fees, grant fees, annuity, templates, and E2E fixtures.

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-frontend-heavy-story`

## Exact Closure Slice

Run the V5 demo script through real UI pages with live backend, announce a Chinese Step Brief before each UI step, visibly execute the UI interactions, record actual observations and status changes, split any blocking P1/P1.5 bug into a separate atomic task, and write the successful V5 demo runbook.

## Explicit Non-Closure

Do not implement CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, Longxia email automation, or P2/P3 integration. Do not delete real data. Do not modify product code inside this task; if a product bug blocks the demo, create a separate atomic task.

## Allowed Files

- `tasks/postdemo/PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01.md`
- `docs/postdemo/postdemo_p1_v5_ui_e2e_success_runbook_20260705.md`
- `artifacts/PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01/**`

## Required Step Brief

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
- Status changes observed
- Screenshot or trace path when available
- Issue ID when not conforming

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:v5:seed`
- Browser-observed UI smoke through the V5 demo pages with live backend.
- `rg -n "Step 0|要做的内容|输入的字段和值|点击的按钮|期望结果|为什么要做|UI 检查点|实际 UI 结果|案件业务状态|法律状态|工作包/文件状态|费用节点状态" docs/postdemo/postdemo_p1_v5_ui_e2e_success_runbook_20260705.md`
- `git diff --check -- docs/postdemo/postdemo_p1_v5_ui_e2e_success_runbook_20260705.md tasks/postdemo/PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01.md`
- `./scripts/task_validate.sh PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01`

## Done Definition

- Old V4 demo data retained is recorded in the runbook.
- V5 new customer and new case are recorded in the runbook.
- Each visible UI step has a Step Brief and actual observation.
- Status changes are explicitly called out in Chinese for case business status, legal status, work package/file status, and fee node status.
- Blocking issues are either fixed through separate atomic tasks or this task is marked BLOCKED with evidence.
- Required evidence exists under `artifacts/PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01/**`.

## Remaining Follow-Up Task IDs

None unless a blocking P1/P1.5 bug is discovered.
