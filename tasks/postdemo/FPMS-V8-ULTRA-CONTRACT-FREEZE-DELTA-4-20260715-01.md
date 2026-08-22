# FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01

Status: PASS / ULTRA CONTRACT FROZEN R3 2026-07-15 / MATERIALIZATION IN PROGRESS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `U4-1 — proven blocker contract freeze and dependency correction`
Executor role: Ultra Architect / designer

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- High blocker and rejected-review evidence for the exact task IDs enumerated by the
  delta-4 specification

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Freeze one additive delta-4 design that resolves only the HIGH contract omissions proven
by the current blocked Foundation tasks, adds only indispensable atomic prerequisites,
classifies the already-frozen obligation-detail task as execution recovery rather than a
new design problem, and defines the exact materialization/review/serialization handoff.

## Explicit Non-Closure

No product, test, migration, script, external skill, `AGENTS.md`, parent
spec/plan/manifest/overlay, existing task-file materialization, customer-source mutation,
release gate execution, commit or unrelated cleanup. This task creates only the delta-4
specification and its own evidence. It must not infer customer approval or activate an
unreviewed official-fee source.

## Remaining Follow-Up Task IDs

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01`

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01.md`
- `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01/**`

No other file is authorized. Preserve the dirty worktree and subtract the captured
baseline.

## Verification Commands

- Structural spec validation:
  `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01/analysis/validate_spec.py`
- Scoped diff:
  `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01.md docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- Task gate:
  `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01`
- Evidence validation:
  `python3 scripts/atomic_evidence_validate.py FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (design-only task).

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01/**`

## Done Definition

The spec freezes every newly proven executable contract or explicit prerequisite without
guessing customer authority; preserves immutable parent history; records exact task IDs,
closure/non-closure/dependencies/allowlists/TDD/error/transaction/serialization contracts;
passes independent domain/fail-closed and dependency/ownership reviews; and passes scoped
checks, task gate and atomic evidence validation. Only then may this design task be PASS.
