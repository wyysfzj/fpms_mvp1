# PD-FEE-SCENARIO-DESIGN-20260704-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

Closure
- 分析 docs/postdemo/专利收费场景-20260626.docx 与 http://www.tianyueip.com/product/612，并结合现有 FPMS 案件/文书/任务/费用实现，产出收费场景有机结合设计。

Non-closure
- 不写后端、前端、数据库 migration、自动缴费、第三方接口或收费计算实现。

Allowlist
- tasks/postdemo/PD-FEE-SCENARIO-DESIGN-20260704-01.md
- docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md
- artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/**

Verification
- DOCX text extraction succeeds
- Website fetch attempted and source saved or marked blocked
- Existing fee/case/document implementation reviewed
- ./scripts/task_validate.sh PD-FEE-SCENARIO-DESIGN-20260704-01

Done Definition
- Design document records source evidence, current-system fit, proposed domain model/flow, P1/P2 split, risks, and clarification questions.
