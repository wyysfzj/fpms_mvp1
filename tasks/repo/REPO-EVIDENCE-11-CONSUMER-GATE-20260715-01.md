# REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01

Status: PASS / INDEPENDENT REVIEW APPROVED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Risk tier: `HIGH` — authoritative evidence acceptance and atomic ownership gate
Executor role: High repository-governance implementer

## Design References

- `AGENTS.md` section 0.3.6, Approved 2026-07-15 Evidence 1.1 transition
- `REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01`: PASS
- `scripts/task_validate.sh`
- `scripts/atomic_evidence_validate.py`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: none
- `evidence_cost`: high
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Implement one repository-local Evidence 1.1 semantic consumer and make both
`scripts/task_validate.sh` and `scripts/atomic_evidence_validate.py` delegate task-local
evidence acceptance to it. For each required step, the consumer must parse JSONL
structurally, accept only the latest record, require exact integer `rc == 0`, require its
normalized task-local output log to exist, and reject malformed or stale-success evidence.
It must require a non-malformed PASS summary, task metadata and dirty-baseline artifacts
when declared, a scoped diff artifact, and one task-local independent review with explicit
`APPROVED` plus zero unresolved P0/P1/P2 findings. Atomic peer ownership, manifest,
overlap, NUL-safe worktree and isolated-current-task checks remain in the atomic wrapper;
only their final task-local evidence acceptance converges on the same consumer.

## Explicit Non-Closure

Do not change the Evidence 1.1 producer, its tests, installed global evidence helper,
legacy/historical activation policy, AGENTS.md, V8 manifests, product source/tests or
release gate. Do not weaken existing peer ownership, exact allowlist, manifest,
serialization or fail-closed checks. Do not repair historical artifacts or continue
Evidence Bundle V2/R4.

## Dependencies

- `REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01`: PASS

## Remaining Follow-Up Task IDs

- `REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01`

## Allowed Files

- `tasks/repo/REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01.md`
- `scripts/evidence_validate.py`
- `scripts/task_validate.sh`
- `scripts/atomic_evidence_validate.py`
- `scripts/tests/test_task_validate_jsonl.py`
- `scripts/tests/test_atomic_evidence_validate.py`
- `artifacts/REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01/**`

No other path is authorized. Preserve the dirty worktree. The three pre-existing
untracked atomic-validator/test files are captured byte-for-byte in this task's baseline
artifacts and must be subtracted from the scoped diff; they are not re-attributed to this
task.

## Verification Commands

- Atomic task shape:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01.md`
- Shell syntax:
  `bash -n scripts/task_validate.sh`
- Targeted lint:
  `ruff check scripts/evidence_validate.py scripts/atomic_evidence_validate.py scripts/tests/test_task_validate_jsonl.py scripts/tests/test_atomic_evidence_validate.py`
- Targeted tests:
  `python3 -m unittest scripts.tests.test_task_validate_jsonl scripts.tests.test_atomic_evidence_validate -v`
- Scoped diff validation:
  `python3 artifacts/REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01/analysis/validate_scope.py`
- Repository task gate:
  `./scripts/task_validate.sh REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01`
- Atomic evidence validation:
  `python3 scripts/atomic_evidence_validate.py REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01 --required-step lint --required-step test --required-step scope`

Expected HTTP status codes: `None` (repository tooling task).

## Evidence Path

- `artifacts/REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01/**`

## Done Definition

Targeted regressions prove both public gates use the same semantic consumer; earlier
success followed by failure, missing/outside log, malformed JSONL/summary/metadata,
missing dirty-baseline files, missing review, non-approved review and any P0/P1/P2 finding
all fail closed. Existing atomic peer/manifest/ownership tests remain green. The
baseline-subtracted patch contains only this task's actual delta, one independent HIGH
review reports zero unresolved P0/P1/P2 findings, and final repository plus atomic gates
pass. Legacy activation remains the sole follow-up.
