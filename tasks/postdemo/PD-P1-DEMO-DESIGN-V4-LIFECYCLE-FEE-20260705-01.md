# PD-P1-DEMO-DESIGN-V4-LIFECYCLE-FEE-20260705-01

## Design References

- `AGENTS.md` section `0.3 Source Document Index for Reviews and Audits`
- `docs/FPMS SPEC 2.0.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- `docs/postdemo/相关流程操作-20260526.docx`
- `docs/postdemo/OA答复流程.docx`
- `docs/postdemo/信函生成操作.docx`
- `docs/postdemo/专利收费场景-20260626.docx`
- `/Users/cfcc/Documents/相关问题解答.docx`
- `artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/extracted/tianyueip_product_612.txt`
- `artifacts/FPMS-AUDIT-REMEDIATION-BATCH-20260705-01/summary.md`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: medium
- `be_fe_coupling`: none
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Enhance the V3 lifecycle demo HTML and lifecycle demo design documentation into a V4 demo design that uses one patent case as the main story and covers three visible lines: lifecycle/legal status, file-driven workflow, and official-fee nodes based on the latest customer fee requirements.

## Explicit Non-Closure

Do not write product code, backend code, frontend code, database migrations, UI E2E tests, CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, or Longxia email automation.

## Allowed Files

- `.superpowers/brainstorm/75098-1783163908/demo-lifecycle-spec2-overlay-v3.html`
- `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.html`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `tasks/postdemo/PD-P1-DEMO-DESIGN-V4-LIFECYCLE-FEE-20260705-01.md`
- `artifacts/PD-P1-DEMO-DESIGN-V4-LIFECYCLE-FEE-20260705-01/**`

## Verification Commands

- `rg -n "三条线|案件生命周期主线|文件驱动主线|官费节点主线|发明申请费 900|复审费发明 1000|减缴 85%|PCT / Hague / IC_LAYOUT" .superpowers/brainstorm/75098-1783163908/demo-lifecycle-spec2-overlay-v3.html docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `rg -n "未递交|等待受理|实审中|一通或二通阶段|已授权|维持有效|年费监控" .superpowers/brainstorm/75098-1783163908/demo-lifecycle-spec2-overlay-v3.html docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `python3 - <<'PY' ... PY` HTML structure check for title and required sections
- `git diff --check -- .superpowers/brainstorm/75098-1783163908/demo-lifecycle-spec2-overlay-v3.html docs/postdemo/demo-lifecycle-spec2-overlay-v3.html docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.html docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md tasks/postdemo/PD-P1-DEMO-DESIGN-V4-LIFECYCLE-FEE-20260705-01.md`
- `./scripts/task_validate.sh PD-P1-DEMO-DESIGN-V4-LIFECYCLE-FEE-20260705-01`

## Done Definition

- HTML demo uses Simplified Chinese and has no blank status cells.
- HTML demo shows one-case lifecycle as the primary structure.
- HTML demo and design doc cover lifecycle/legal status, file-driven workflow, and official-fee nodes.
- Latest fee requirements are explicitly represented: official fees only, fee item/category and subtype mapping, fee-rate parameters, `0.85` as 85% reduction and 15% payable, invention application fee 900, invention reexamination fee 1000, application/additional/publication/exam/reexam/grant/annuity/late-fee nodes, Chinese deadline preview wording, annuity tasks/pay-lists, and PCT/Hague/IC_LAYOUT frozen boundary.
- Required evidence files and task gate exist.

## Evidence Path

- `artifacts/PD-P1-DEMO-DESIGN-V4-LIFECYCLE-FEE-20260705-01/**`

## Remaining Follow-Up Task IDs

None
