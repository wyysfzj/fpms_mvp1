# FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `U3-1 — delta-3 fail-closed and evidence-tool contract freeze`
Executor role: Ultra Architect / designer

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md`
- `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01/review/independent_review.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Freeze one additive delta-3 design that closes the discovered RAW attachment registration
and external-submission authority gaps and defines two repository-owned evidence-tool
contracts without changing product or tool implementation.

## Explicit Non-Closure

No product, test, script, external skill, `AGENTS.md`, parent spec/plan/manifest/overlay,
task materialization, release gate execution, commit or unrelated cleanup. This task only
creates the delta-3 specification and its own evidence.

## Remaining Follow-Up Task IDs

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01/**`

No other file is authorized. Preserve the dirty worktree and subtract the captured
baseline.

## Verification Commands

- Structural spec validation: `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01/analysis/validate_spec.py`
- Scoped diff: `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01.md docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- Task gate: `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (design-only task).

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01/**`

## Done Definition

The spec freezes four separate atomic implementation contracts, preserves the immutable
283/197/86 and accepted delta-1/delta-2 parents, computes the additive 290/204 product
counts, keeps evidence governance outside product counts, records exact dependencies and
serialization, passes two independent read-only reviews, scoped checks, task gate and
atomic evidence validation. Only then may this design task be PASS.
