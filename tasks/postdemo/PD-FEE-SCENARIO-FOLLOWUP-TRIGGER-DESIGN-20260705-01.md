# PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-DESIGN-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice
- Analyze and design the follow-up official-fee trigger scope after the completed fee scenario enhancement:
  - reexamination trigger preview
  - grant/annuity deadline preview
  - PCT/Hague/IC layout trigger rules
- Produce a source-aware design document that defines recommended scope, trigger events, required fields, output behavior, implementation wave order, and customer clarification questions.

## Explicit Non-Closure
- No backend, frontend, database, migration, seed, or test implementation.
- No automatic PCT/Hague/IC fee generation.
- No CPC/OA integration, RPA, automatic signing, or automatic payment.
- No rewrite of the existing fee scenario integration design.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-PCT-HAGUE-TRIGGER-RULES-20260705-01`
- `PD-FEE-SCENARIO-IC-LAYOUT-TRIGGER-RULES-20260705-01`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-DESIGN-20260705-01.md
- docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md
- artifacts/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-DESIGN-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-DESIGN-20260705-01.md`
- `test -f docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- `rg -n "复审触发|授权/年费|PCT|海牙|IC_LAYOUT|待确认|推荐实施顺序" docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-DESIGN-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-DESIGN-20260705-01/**

## Done Definition
- Design document exists and covers all three follow-up scopes.
- Design distinguishes P1.5-ready domestic follow-ups from P2/P3 policy-sensitive triggers.
- Design lists required data fields, idempotency rules, output objects, and customer clarification questions.
- Task gate and required evidence artifacts pass.
