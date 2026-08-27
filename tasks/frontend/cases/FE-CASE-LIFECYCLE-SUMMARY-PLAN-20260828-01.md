# FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "lifecycle", "lineage", "ui"]
Task-Path: tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01.md

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Approved Input

- `docs/superpowers/specs/2026-08-28-case-lifecycle-three-track-summary-design.md`
- User approval in the current Codex task dated 2026-08-28.

## Exact Closure Slice

Produce one implementation-ready, test-first plan for the approved案件详情 three-track
current-first summary design. The plan must identify exact frontend and Playwright files,
freeze minimal component responsibilities, provide executable RED/GREEN commands and
expected outcomes, preserve the existing pagination and fact boundaries, and hand off one
atomic product implementation task.

## Explicit Non-Closure

This task does not change product code, tests, APIs, schemas, lifecycle facts, fees,
permissions, evidence lineage, V6 demo content, runbooks, seed data, or deployment state.

## Remaining Follow-Up Task IDs

- FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01

## Allowed Files

- `tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01.md`
- `docs/superpowers/plans/2026-08-28-case-lifecycle-three-track-summary.md`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01 lint git diff --check -- tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01.md docs/superpowers/plans/2026-08-28-case-lifecycle-three-track-summary.md
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01 test shasum -a 256 tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01.md docs/superpowers/plans/2026-08-28-case-lifecycle-three-track-summary.md
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01 scope python3 scripts/evidence_scope.py finalize FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01
```

## Evidence Path

- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01/task.json`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01/results.jsonl`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01/summary.md`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-PLAN-20260828-01/git/diff.patch`
