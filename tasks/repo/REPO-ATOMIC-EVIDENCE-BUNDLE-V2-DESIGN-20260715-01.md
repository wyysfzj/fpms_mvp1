# REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01

Status: READY FOR ULTRA SPEC REREVIEW / R4 MINIMAL CORRECTION AUTHORIZED 2026-07-15
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Risk tier: `HIGH` — authoritative evidence production and acceptance governance
Executor role: Ultra repository-governance architect

## Design References

- `AGENTS.md`
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/references/evidence-gates.md`
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py`
- `scripts/evidence_run.sh`
- `scripts/evidence_finalize.sh`
- `scripts/task_validate.sh`
- `scripts/atomic_evidence_validate.py`
- `scripts/tests/test_atomic_evidence_validate.py`
- `tasks/repo/REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01.md`
- `tasks/repo/REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01.md`
- `docs/superpowers/specs/2026-07-15-fpms-atomic-evidence-reconciliation-checkpoint-design.md`
- `artifacts/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01/git/diff.patch`
- `artifacts/REPO-ATOMIC-EVIDENCE-RECONCILIATION-DESIGN-20260715-01/analysis/reviewer_dispatch_log.md`
- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/analysis/bootstrap_reconciliation.json`
- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/analysis/r1_findings_and_closure.md`
- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/review/round3_adversarial_checkpoint.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: none
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## R4 Exception Authorization

After R3 returned two approvals and one adversarial `P1`, the user explicitly authorized
one narrowly scoped R4 correction on 2026-07-15. R4 may only remove the self-anchored
external patch-renderer trust root, bind the replacement to the independently accepted V2
toolchain chain, refresh this task's scoped evidence, and repeat the same three review axes.
It does not authorize product implementation, a broader redesign, or an automatic R5.

## Exact Closure Slice

Freeze one superseding Ultra design for a repository-local Evidence Bundle V2 contract.
The design must define exact evidence production, canonical bundle sealing, semantic
scope validation, shared task-gate/atomic-validator consumption, legacy bootstrap rules,
orthogonal independent review and the amended dependency boundary for the previously
approved G3/G4 reconciliation checkpoint design.

## Explicit Non-Closure

No implementation of the V2 producer, verifier, task-gate integration, atomic-validator
integration, checkpoint or reconciliation authority. No edit to the installed global
skill/helper, existing G1/G2/Delta-3 code or history, `AGENTS.md`, an existing task,
baseline, evidence bundle, manifest, product source/test, release gate or Git state. Do
not retroactively invalidate historical PASS tasks from a heuristic scan.

## Remaining Follow-Up Task IDs

- `REPO-ATOMIC-EVIDENCE-BUNDLE-V2-CORE-20260715-01`
- `REPO-EVIDENCE-BUNDLE-V2-LEGACY-PASS-REGISTER-20260715-01`
- `REPO-TASK-GATE-EVIDENCE-BUNDLE-V2-INTEGRATION-20260715-01`
- `REPO-ATOMIC-VALIDATOR-EVIDENCE-BUNDLE-V2-INTEGRATION-20260715-01`
- `REPO-ATOMIC-EVIDENCE-RECONCILIATION-CHECKPOINT-V2-20260715-01`
- `REPO-AGENTS-EVIDENCE-BUNDLE-V2-ACTIVATION-20260715-01`
- `REPO-V8-FOUR-TASK-WORKTREE-RECONCILIATION-AUTHORITY-20260715-01`
- implementation-plan/materialization task to be named after written-spec approval

## Allowed Files

- `tasks/repo/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01.md`
- `docs/superpowers/specs/2026-07-15-fpms-atomic-evidence-bundle-v2-design.md`
- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/**`

No other path is authorized. Preserve the dirty worktree and subtract the captured
baseline. Bootstrap evidence for this task must independently prove that its scoped patch
contains exactly the task and new spec paths, and must expand each collapsed legacy
baseline directory into provenance-backed concrete descendants. The bootstrap is valid
only for this design task, grants no directory-prefix authority and does not grant V2,
legacy, product or release acceptance. Stock `finalize` output is not acceptance.

## Verification Commands

- Atomic task shape:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01.md`
- Structural design validation:
  `python3 artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/analysis/validate_design.py`
- Bootstrap semantic scope validation:
  `python3 artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/analysis/validate_bootstrap_scope.py`
- Canonical scoped patch check:
  `git apply --check --reverse -- artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/git/diff.patch`
- Repository task gate:
  `./scripts/task_validate.sh REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01`
- Atomic evidence validation:
  `python3 scripts/atomic_evidence_validate.py REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (design-only task).

## Evidence Path

- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/**`

## Done Definition

The written spec freezes one end-to-end Evidence Bundle V2 trust model, exact schemas,
producer/consumer behavior, legacy boundary, fail-closed adversarial regressions, atomic
follow-up ownership, one-time serialized core-bootstrap root and G3/G4 supersession.
Structural and semantic bootstrap checks pass; independent Ultra producer, consumer/gate
and adversarial/checkpoint review axes each bind the same spec, bootstrap ledger and scoped
patch hashes and issue an evidence-backed `APPROVED` verdict; the compatibility task gate
and atomic evidence validation pass without being treated as semantic acceptance.
