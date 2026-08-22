# REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01

Status: PASS / INDEPENDENT GOVERNANCE REVIEW APPROVED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Risk tier: `HIGH` — authoritative evidence activation and dirty-worktree compatibility
Executor role: High repository-governance implementer

## Design References

- `AGENTS.md` section 0.3.6, Approved 2026-07-15 Evidence 1.1 transition
- `REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01`: PASS
- `REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01`: PASS
- `scripts/evidence_scope.py`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: none
- `evidence_cost`: high
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Activate Evidence 1.1 for subsequent repository work with one repository-local init entry
point. The entry point must preserve the existing `task.json`,
`baseline_allowlist.diff`, `baseline_external_files.txt`, results, summary and git artifact
names while replacing the legacy initializer's incomplete baseline projection with one
coherent binary-capable HEAD-to-pre-task allowlisted patch. It must include pre-existing
tracked and untracked allowlisted files, exclude the task's own artifact subtree, and
record every outside dirty path as an exact concrete NUL-safe path rather than a collapsed
directory. Update AGENTS.md to require this entry point for newly initialized tasks,
activate the strict shared Evidence 1.1 consumer, preserve pre-activation PASS tasks as
historical acceptance without rerunning or rewriting them, and forbid grandfathering a
pre-activation non-PASS task as PASS. After this task passes, the accepted V8 Foundation
catalog resumes directly in High.

## Explicit Non-Closure

Do not change the Evidence 1.1 finalizer or shared consumer semantics, atomic peer
ownership, product source/tests, V8 task catalog/manifest, historical task/evidence bytes,
historical PASS status, customer decisions, Foundation business work or release gate. Do
not create a fourth evidence prerequisite, a legacy PASS hash registry, a new artifact
schema or continue Evidence Bundle V2/R4.

## Dependencies

- `REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01`: PASS
- `REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01`: PASS

## Remaining Follow-Up Task IDs

- `None` — resume dependency-ready V8 Foundation tasks from the existing manifest.

## Allowed Files

- `tasks/repo/REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01.md`
- `AGENTS.md`
- `scripts/evidence_init.sh`
- `scripts/evidence_scope.py`
- `scripts/tests/test_evidence_finalize.py`
- `artifacts/REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01/**`

No other path is authorized. Preserve the dirty worktree. Capture and subtract the
pre-existing untracked producer/test bytes and the tracked AGENTS.md baseline; do not
re-attribute the two prior Evidence 1.1 tasks to this activation task.

## Verification Commands

- Atomic task shape:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01.md`
- Shell syntax:
  `bash -n scripts/evidence_init.sh scripts/evidence_finalize.sh`
- Targeted lint:
  `ruff check scripts/evidence_scope.py scripts/tests/test_evidence_finalize.py`
- Targeted tests:
  `python3 -m unittest scripts.tests.test_evidence_finalize -v`
- Activation policy validation:
  `python3 artifacts/REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01/analysis/validate_activation.py`
- Scoped diff validation:
  `python3 artifacts/REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01/analysis/validate_scope.py`
- Repository task gate:
  `./scripts/task_validate.sh REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01`
- Atomic evidence validation:
  `python3 scripts/atomic_evidence_validate.py REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01 --required-step lint --required-step test --required-step scope`

Expected HTTP status codes: `None` (repository governance/tooling task).

## Evidence Path

- `artifacts/REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01/**`

## Done Definition

Targeted tests prove the repository init captures a coherent pre-task tracked/untracked
baseline, expands outside untracked directories into exact paths, and lets the existing
finalizer emit only the later task delta. AGENTS.md activates the entry point and strict
consumer without weakening historical PASS or fail-closed new work. The five-path
baseline-subtracted patch, task-local checks, one independent governance review,
repository task gate and atomic evidence validation all pass. No fourth evidence task is
created, and Foundation execution is unblocked.
