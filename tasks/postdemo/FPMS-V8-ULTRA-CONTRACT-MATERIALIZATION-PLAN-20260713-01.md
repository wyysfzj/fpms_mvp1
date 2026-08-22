# FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Ultra Architect / Planner

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Create one reviewed implementation plan and explicit 16-task-file materialization batch
for the approved Ultra contract delta, using an additive delta overlay that preserves the
immutable 283/197/86 baseline catalog and still makes the three new external prerequisites
mandatory before Foundation close.

## Explicit Non-Closure

No task-contract edits beyond this planning task, no product code/test/schema/migration/UI
implementation, no baseline catalog or historical materializer rewrite, no High execution,
no repo-wide gate, commit, or push.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-20260713-01` — PASS and user approved.

## Remaining Follow-Up Task IDs

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01.md`
- `docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01.md`
- `rg -n "^# .*Implementation Plan|^> \*\*For agentic workers|^## Story Shape Classification|^## Explicit batch manifest|^## Wave order|^## Shared ownership and verification|^## Done definition" docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01/analysis/validate_plan.py`
- `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01.md docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01`

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-20260713-01/**`

## Done Definition

The plan names exactly 16 task files, assigns one file per agent, records closure,
allowlist, dependency/runbook, verification and wave order, preserves immutable baseline
materialization, defines the mandatory delta overlay and close linkage, passes independent
plan review and all scoped evidence/task gates.
