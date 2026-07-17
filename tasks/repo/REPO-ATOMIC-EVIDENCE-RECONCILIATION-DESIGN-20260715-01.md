# REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01

Status: IN PROGRESS / USER APPROVED — INDEPENDENT REVIEW TOOLING STALLED 2026-07-15
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Risk tier: `HIGH` — authoritative atomic-evidence acceptance governance
Executor role: Ultra repository-governance architect

## Design References

- `AGENTS.md`
- `tasks/repo/REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01.md`
- `tasks/repo/REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01.md`
- `artifacts/REPO-COLLAPSED-DIRTY-BASELINE-PREFIX-COMPATIBILITY-20260714-01/rejected_contract.md`
- `artifacts/REPO-COLLAPSED-DIRTY-BASELINE-PREFIX-COMPATIBILITY-20260714-01/review/contract_review.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: none
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Freeze one additive Ultra design for an opt-in, exact-state reconciliation checkpoint
mode and one independently reviewed current-worktree reconciliation authority. The design
must allow the four named, already independently reviewed V8 product tasks to complete
atomic evidence validation without rewriting their original baselines, trusting directory
prefixes, omitting dirty paths, fabricating owners, or weakening existing no-peer/peer
validation.

## Explicit Non-Closure

No wrapper or test implementation; no product source/test change; no edit to `AGENTS.md`,
the external evidence helper, G1/G2/history, an existing baseline, manifest, task evidence,
release gate or Git state. No implementation plan or task materialization beyond this
design task. No commit, push, reset, clean, stash or discard.

## Remaining Follow-Up Task IDs

- `REPO-ATOMIC-EVIDENCE-RECONCILIATION-CHECKPOINT-MODE-20260715-01`
- `REPO-V8-FOUR-TASK-WORKTREE-RECONCILIATION-AUTHORITY-20260715-01`
- implementation-plan/materialization task to be named after written-spec approval

## Allowed Files

- `tasks/repo/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01.md`
- `docs/superpowers/specs/2026-07-15-fpms-atomic-evidence-reconciliation-checkpoint-design.md`
- `artifacts/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01/**`

No other path is authorized. Preserve the dirty worktree and subtract the captured
baseline.

## Verification Commands

- Atomic task shape:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01.md`
- Structural design validation:
  `python3 artifacts/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01/analysis/validate_design.py`
- Scoped diff:
  `git diff --check -- tasks/repo/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01.md docs/superpowers/specs/2026-07-15-fpms-atomic-evidence-reconciliation-checkpoint-design.md`
- Repository task gate:
  `./scripts/task_validate.sh REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01`
- Atomic evidence validation:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (design-only task).

## Evidence Path

- `artifacts/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01/**`

## Done Definition

The written design freezes G3/G4 as separate atomic closures, exact checkpoint schema and
trust boundaries, legacy-mode compatibility, fail-closed drift/provenance behavior,
quiescent four-task rollout, independent review and follow-up boundaries. Structural and
scope checks, repository task gate, independent Ultra spec review and atomic evidence
validation must pass before this design task may be reported PASS.
