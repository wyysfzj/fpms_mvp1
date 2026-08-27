# FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "lifecycle", "lineage", "ui"]
Task-Path: tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01.md

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Design References

- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
- `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
- User-approved detailed design in the current Codex task dated 2026-08-28.

## Exact Closure Slice

Freeze one implementation-ready UI design for the案件详情 three-track lifecycle area. The
design must keep document evidence, lifecycle state, and fee obligations visible together;
make the initial view answer only current state, latest change, and explicit next task; keep
customer-visible warnings outside the collapsed history; and disclose the existing complete
history on demand without changing its authoritative facts or pagination.

## Explicit Non-Closure

This task does not change product code, backend APIs, API types, database schema, lifecycle
transitions, evidence lineage, fee calculations, permissions, balance data sources, the
existing detailed history internals, V6 frozen worktree content, runbooks, or demo data.

## Remaining Follow-Up Task IDs

- FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01

## Allowed Files

- `tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01.md`
- `docs/superpowers/specs/2026-08-28-case-lifecycle-three-track-summary-design.md`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01 lint git diff --check -- tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01.md docs/superpowers/specs/2026-08-28-case-lifecycle-three-track-summary-design.md
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01 test shasum -a 256 tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01.md docs/superpowers/specs/2026-08-28-case-lifecycle-three-track-summary-design.md
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01 scope python3 scripts/evidence_scope.py finalize FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01
```

## Evidence Path

- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01/task.json`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01/results.jsonl`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01/summary.md`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-DESIGN-20260828-01/git/diff.patch`
