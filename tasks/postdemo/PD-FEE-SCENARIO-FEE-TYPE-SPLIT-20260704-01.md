# PD-FEE-SCENARIO-FEE-TYPE-SPLIT-20260704-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

Closure
- Surgical update post-demo fee scenario integration design to clarify that new fee-trigger scenarios are not a new fee type; each generated item must be classified as GOV / SERVICE / MISC, with only GOV entering official pay-list / GovPayment.

Non-closure
- No backend, frontend, database migration, fee calculation implementation, official payment implementation, or seed data changes.

Allowlist
- tasks/postdemo/PD-FEE-SCENARIO-FEE-TYPE-SPLIT-20260704-01.md
- docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md
- artifacts/PD-FEE-SCENARIO-FEE-TYPE-SPLIT-20260704-01/**

Verification
- Content check for GOV / SERVICE / MISC boundary
- Content check for only GOV entering PayList / GovPayment
- ./scripts/task_validate.sh PD-FEE-SCENARIO-FEE-TYPE-SPLIT-20260704-01

Done Definition
- Design explicitly separates fee-trigger scenarios from fee item accounting types and records the official-pay-list boundary.
