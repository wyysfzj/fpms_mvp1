# PD-FEE-SCENARIO-STRUCTURED-APPENDIX-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice
- Surgical update the post-demo fee scenario integration design with the user-confirmed structured understanding of patent official fee categories, subtypes, trigger rules, deadline rules, reduction rules, PCT/Hague fee coverage, and IC layout separation.

## Explicit Non-Closure
- No backend, frontend, database migration, seed data, test, demo script, official payment, CPC/OA integration, or fee calculation implementation changes.
- Do not rewrite the full design document; append the confirmed structured catalog as an appendix and adjust only directly related wording if needed.

## Remaining Follow-Up Task IDs
- Existing implementation follow-ups remain in `docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md`.

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-STRUCTURED-APPENDIX-20260705-01.md
- docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md
- artifacts/PD-FEE-SCENARIO-STRUCTURED-APPENDIX-20260705-01/**

## Verification Commands
- `test -s docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `rg -n "附录 A|fee_category|fee_subtype|申请日/受理通知起 2 个月|第三期.*否|IC_LAYOUT" docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-STRUCTURED-APPENDIX-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-STRUCTURED-APPENDIX-20260705-01/**

## Done Definition
- The design document includes the confirmed structured appendix.
- The appendix records `收费项目 = fee_category` and `细分类型 = fee_subtype`.
- The appendix records the confirmed application fee deadline, fee reduction semantics, and Hague third-installment non-reduction rule.
- Evidence artifacts and task gate pass.
