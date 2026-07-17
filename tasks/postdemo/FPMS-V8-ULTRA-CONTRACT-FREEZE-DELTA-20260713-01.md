# FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Ultra Architect / Designer

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: medium
- `be_fe_coupling`: medium
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Record the user-approved prerequisite-first Ultra contract delta for the nine currently
identified High blockers, including the three newly required atomic prerequisite/test
migration tasks and the fail-closed defaults that govern later task materialization.

## Explicit Non-Closure

No product code, schema, migration, API, UI, test implementation, customer-decision
activation, task-contract materialization, manifest rewrite, commit, push, or High
development execution.

## Dependencies

- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- User approval of prerequisite-first approach A on 2026-07-13.

## Remaining Follow-Up Task IDs

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01.md`
- `rg -n "^## (Purpose|Approved approach|Frozen contracts|New atomic prerequisites|Dependency and runbook corrections|Non-closure|Acceptance)" docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `rg -n "CASE_STATUS_MANAGED_BY_LIFECYCLE|FEE_CLIENT_INSTRUCTION_RECORDED|CNIPA_RATE_SOURCE_V1|case > GLOBAL|form-NNN > ALL-22|rate_effective_on|GRANT-NOTICE-FEE-LINE|OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER|LEGACY-TEST-MIGRATION" docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01.md docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01`

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01/**`

## Done Definition

The delta design captures all nine blockers, the three required new atomic tasks, exact
recommended defaults, dependency/runbook corrections, alternatives and non-closure; an
independent reviewer approves it; scoped checks, evidence validation and the task gate
pass. The document is then presented to the user for the required written-spec review.
