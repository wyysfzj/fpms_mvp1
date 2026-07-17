# REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01

Status: PASS / INDEPENDENT REVIEW APPROVED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Risk tier: `HIGH` — authoritative repository evidence production
Executor role: High repository-governance implementer

## Design References

- `AGENTS.md` section 0.3.6, Approved 2026-07-15 Evidence 1.1 transition
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/references/evidence-gates.md`
- `scripts/evidence_finalize.sh`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: medium
- `be_fe_coupling`: none
- `evidence_cost`: high
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Implement one repository-local Evidence 1.1 producer behind
`scripts/evidence_finalize.sh`. The producer must read the exact task id, repository root,
allowlist and dirty-baseline metadata from `artifacts/<TASK-ID>/task.json`; reconstruct the
captured tracked baseline from `baseline_allowlist.diff`; compare that baseline with the
current exact allowlisted source/task state; and write a binary-capable, baseline-subtracted
`git/diff.patch` containing tracked modifications, additions, deletions, mode changes and
untracked additions. It must exclude the task's own artifact subtree from the semantic
patch, exclude outside-allowlist changes, preserve `status.txt`, `rev.txt` and summary
compatibility, and fail closed on missing/malformed metadata, repository mismatch,
unusable dirty-baseline evidence or unsafe allowlist paths.

## Explicit Non-Closure

Do not change the repository task gate, atomic ownership validator, installed global
evidence skill/helper, required-result or log semantics, independent-review validation,
legacy PASS activation policy, AGENTS.md, product source/tests, V8 manifests or release
gate. Do not repair historical artifacts or continue Evidence Bundle V2/R4.

## Dependencies

- `REPO-AGENTS-TRUSTED-WORKSPACE-VNEXT-20260715-01`: PASS

## Remaining Follow-Up Task IDs

- `REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01`
- `REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01`

## Allowed Files

- `tasks/repo/REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01.md`
- `scripts/evidence_finalize.sh`
- `scripts/evidence_scope.py`
- `scripts/tests/test_evidence_finalize.py`
- `artifacts/REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01/**`

No other path is authorized. Preserve the dirty worktree and subtract the captured
baseline.

## Verification Commands

- Atomic task shape:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01.md`
- Shell syntax:
  `bash -n scripts/evidence_finalize.sh`
- Targeted lint:
  `ruff check scripts/evidence_scope.py scripts/tests/test_evidence_finalize.py`
- Targeted tests:
  `python3 -m unittest scripts.tests.test_evidence_finalize -v`
- Scoped diff validation:
  `python3 artifacts/REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01/analysis/validate_scope.py`
- Repository task gate:
  `./scripts/task_validate.sh REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01`
- Atomic evidence validation:
  `python3 scripts/atomic_evidence_validate.py REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01 --required-step lint --required-step test --required-step scope`

Expected HTTP status codes: `None` (repository tooling task).

## Evidence Path

- `artifacts/REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01/**`

## Done Definition

The producer's targeted tests prove exact allowlist projection, tracked dirty-baseline
subtraction, tracked/untracked inclusion, deletion and mode/binary handling, outside-scope
exclusion and fail-closed malformed inputs. Task-local lint/tests/scope pass, one
independent HIGH reviewer reports zero unresolved P0/P1/P2 findings, and both repository
task gate and atomic evidence validation pass. The consumer and activation follow-ups
remain untouched.
