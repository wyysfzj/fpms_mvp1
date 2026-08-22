# FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Main-thread Governance Maintainer

## Design References

- `AGENTS.md`
- `tasks/postdemo/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01.md`
- Local Codex/Clash diagnostics performed on 2026-07-14; diagnostic logs remain external
  read-only inputs and are not copied into repository evidence.

## Story Shape Classification

- `shared_file_density`: low — exactly one authoritative governance file changes.
- `prereq_dependency_density`: low — the existing vNext governance task is already PASS.
- `be_fe_coupling`: none — no product behavior changes.
- `evidence_cost`: medium — deterministic prose checks plus independent review are required.
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

## Exact Closure Slice

Add one transport-resilient orchestration rule set to `AGENTS.md` that requires minimal-
context subagent spawning, bounded tool output and execution intervals, state reconciliation
before retry after a reconnect, and timely interruption of objectively zero-progress agents.

## Explicit Non-Closure

No product source, test, schema, migration, task contract other than this task, approved
spec/plan/manifest, proxy or network configuration, Codex application configuration,
model setting, existing evidence family, release gate, commit or push is changed. The task
does not claim to eliminate external network failures or alter the existing two-observation
stall threshold.

## Dependencies

- `FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01` — PASS.

## Remaining Follow-Up Task IDs

None.

## Allowed Files

- `tasks/postdemo/FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01.md`
- `AGENTS.md`
- `artifacts/FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01/**`

The pre-existing dirty worktree and the captured `AGENTS.md` baseline must be preserved
and subtracted from the task-scoped diff.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01.md`
- deterministic rule-presence and no-duplicate-heading validation for `AGENTS.md`
- `git diff --check -- AGENTS.md tasks/postdemo/FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01.md artifacts/FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01`
- independent review of the exact baseline-subtracted governance delta
- `./scripts/task_validate.sh FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Product tests, Ruff, migrations, frontend checks, Playwright, full-repo checks and the
release gate are prohibited for this documentation-only governance task.

## Evidence Path

- `artifacts/FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01/**`

## Done Definition

The four required resilience rules are explicit and non-duplicative; existing atomicity,
fail-closed, evidence, independent review, serialization, stall classification and release-
gate rules are unchanged; dirty-baseline and scoped-diff evidence exist; independent review,
repository task gate and atomic evidence validation pass; no non-allowlisted file changes
are attributed to this task.
