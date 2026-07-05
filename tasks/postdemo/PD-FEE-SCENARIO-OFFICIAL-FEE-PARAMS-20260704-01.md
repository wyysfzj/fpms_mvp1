# PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-20260704-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

Closure
- Surgical update post-demo fee scenario integration design to reflect customer clarification: the scope contains only official fees. Customer DOCX and Tianyue URL fees should be modeled through an official-fee rate parameter table plus official-fee trigger rules; generated fee items are GOV only.

Non-closure
- No backend, frontend, database migration, fee calculation implementation, official payment implementation, or seed data changes.

Allowlist
- tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-20260704-01.md
- docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md
- artifacts/PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-20260704-01/**

Verification
- Content check for only-official-fee scope
- Content check for official fee parameter table and trigger rule table
- Content check that generated items are GOV only
- ./scripts/task_validate.sh PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-20260704-01

Done Definition
- Design removes non-official fee split and defines parameterized official-fee rates plus official-fee trigger rules.
