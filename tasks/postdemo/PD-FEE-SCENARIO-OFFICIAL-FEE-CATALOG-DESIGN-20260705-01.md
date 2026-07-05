# PD-FEE-SCENARIO-OFFICIAL-FEE-CATALOG-DESIGN-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice
- Surgical update the post-demo fee scenario integration design to state that customer DOCX and Tianyue URL fee entries are official-fee catalog inputs, should be loaded into an auditable official-fee parameter table, and must not be split into management fee or service fee concepts.

## Explicit Non-Closure
- No backend, frontend, database migration, fee calculation implementation, seed data implementation, official payment implementation, or UI changes.
- No claim that Tianyue URL is the final legal authority; official or customer-confirmed versions remain required before enabling executable rates.

## Remaining Follow-Up Task IDs
- Existing implementation tasks listed in `docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-CATALOG-DESIGN-20260705-01.md
- docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md
- artifacts/PD-FEE-SCENARIO-OFFICIAL-FEE-CATALOG-DESIGN-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-CATALOG-DESIGN-20260705-01.md`
- `rg -n "官费参数表|参数表装载|不进入草单候选|不拆分管费|FeeRate|待确认/未启用" docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-OFFICIAL-FEE-CATALOG-DESIGN-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-OFFICIAL-FEE-CATALOG-DESIGN-20260705-01/**

## Done Definition
- The design explicitly answers that all customer-listed official-fee entries should be cataloged in `FeeRate` as official-fee parameters, while only confirmed and field-computable entries become enabled trigger candidates.
