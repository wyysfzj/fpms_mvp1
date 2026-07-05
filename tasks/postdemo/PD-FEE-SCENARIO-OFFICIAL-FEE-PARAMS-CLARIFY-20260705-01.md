# PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-CLARIFY-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice
- Surgical update the post-demo fee scenario design and implementation plan to clarify that this scope has only official fees, and that customer DOCX / Tianyue URL fee entries should be loaded into an official-fee parameter table as auditable master data, while executable trigger coverage can be phased.

## Explicit Non-Closure
- No backend, frontend, database migration, fee calculation implementation, seed data changes, official payment implementation, or UI changes.
- No claim that Tianyue URL is the authoritative legal source; it is a customer-provided source clue until confirmed against official policy.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01`
- Existing implementation tasks listed in `docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-CLARIFY-20260705-01.md
- docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md
- docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md
- artifacts/PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-CLARIFY-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-CLARIFY-20260705-01.md`
- `rg -n "只有官费|参数目录全量承载|自动触发分期启用|FeeRate.*official-fee parameter table|Generated fee items.*GOV|RATE-CATALOG-SEED" docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-CLARIFY-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-OFFICIAL-FEE-PARAMS-CLARIFY-20260705-01/**

## Done Definition
- The design and plan explicitly answer the customer question: all listed official-fee entries belong in the official-fee parameter table for traceability; P1.5 implementation may activate a smaller domestic-mainline trigger subset first.
