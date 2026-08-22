# REPO-GOVERNANCE-RESET-TASKCTL-20260716-01

Status: PASS / IMPLEMENTATION COMPLETE / PENDING EVIDENCE 1.1 CLOSE
Risk-Tier: HIGH
Closure-Tags: ["evidence", "governance", "tooling"]
Task-Path: tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md
Execution class: `CONTRACT FROZEN`
Chosen runbook: `P0-prereq-heavy-story`

## Authority

- Final approved Governance Reset design and GVR-1 accepted candidate artifacts.
- Current `AGENTS.md` and Evidence 1.1 remain active during this task.

## Exact Closure Slice

Implement the single `taskctl` interface, including the exact GVR-3 bootstrap start/adopt,
and internal state/event/lease/review/adopt/doctor behavior defined by the approved design.
Replace only the temporary-index implementation
inside evidence scope. Provide focused contract, fault-injection, concurrency, idempotence,
legacy-prefix and crash-recovery tests.

## Explicit Non-Closure

- Do not edit root AGENTS, active manifest, existing evidence adapters, task/atomic/release
  consumers, release gate, product files, historical task artifacts or Goal state.
- Do not activate v2 or implement SQLite database-template cache/FIFO scheduling.
- Do not change legal, fee, lineage, permission, migration or release semantics.

## Dependencies

- `REPO-GOVERNANCE-RESET-MODULES-20260716-01`: independently accepted PASS.
- Its kernel/manifest/digest artifacts are read-only immutable inputs.

## Remaining Follow-Up Task IDs

- `REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01`

## Allowed Files

- `tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md`
- `scripts/taskctl`
- `scripts/evidence_scope.py`
- `scripts/tests/test_taskctl.py`
- `scripts/tests/test_evidence_scope_v2.py`
- `artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/**`

## Verification Commands

Every command below runs from the repository root. `RED` alone must return nonzero before
implementation; every other command and every child command of canonical close must return
`0`. No alternative argv, product/full/release command or direct helper `init` is allowed.

1. Atomic task shape:

   ```bash
   python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md
   ```

2. Initialize Evidence 1.1 exactly once after GVR-1 is accepted and this contract is frozen:

   ```bash
   ./scripts/evidence_init.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 --task-file tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md --allowlist tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md --allowlist scripts/taskctl --allowlist scripts/evidence_scope.py --allowlist scripts/tests/test_taskctl.py --allowlist scripts/tests/test_evidence_scope_v2.py
   ```

3. Contract-complete RED for the full public CLI/CAS contract, GVR-3-only
   bootstrap-kernel/manifest validation and non-PASS adopt, virtual activation staging,
   candidate/receipt split, strict review lease, atomic events, JSONL view, FD lock,
   governance adopt, legacy prefix, canonical scope/frozen-v1 classification, and recovery
   semantics:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 red env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_taskctl scripts.tests.test_evidence_scope_v2
   ```

4. Final GREEN. The two named test modules must contain the full fault matrix: short write,
   EINTR, ENOSPC, file/dir fsync, rename, SIGKILL, ordinal reservation crash, two writers,
   opaque post-effect/pre-result `OUTCOME_UNKNOWN`, both replay-safe effect-verifier
   branches, GVR-3 bootstrap missing/mismatched/dependency-failed/idempotent cases,
   FD-lock process death, sidecar failure, and every activation crash point.

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_taskctl scripts.tests.test_evidence_scope_v2
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 format_check ruff format --check scripts/taskctl scripts/evidence_scope.py scripts/tests/test_taskctl.py scripts/tests/test_evidence_scope_v2.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 lint ruff check scripts/taskctl scripts/evidence_scope.py scripts/tests/test_taskctl.py scripts/tests/test_evidence_scope_v2.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 compile env PYTHONPYCACHEPREFIX=/tmp/fpms-gvr2-pycache python3 -m py_compile scripts/taskctl scripts/evidence_scope.py scripts/tests/test_taskctl.py scripts/tests/test_evidence_scope_v2.py
   ```

5. After every final test/lint/compile command is green, and before independent review,
   change only this task's first Status line to:

   ```text
   Status: PASS / IMPLEMENTATION COMPLETE / PENDING EVIDENCE 1.1 CLOSE
   ```

   Then replace this task's `summary.md` with exactly this content. This legacy PASS marker
   is only the current Evidence 1.1 content precondition; taskctl remains inactive and it
   does not authorize GVR-3 or product work.

   ```text
   # Summary
   Status: PASS / IMPLEMENTATION COMPLETE / PENDING EVIDENCE 1.1 CLOSE
   Task-ID: REPO-GOVERNANCE-RESET-TASKCTL-20260716-01

   ## Commands
   - Canonical results and logs are recorded in results.jsonl and outputs/.

   ## Results
   - Final targeted test, format check, lint and compile returned 0; scope and close results are recorded separately in results.jsonl.

   ## Notes
   - Active governance and legacy adapters remain unchanged; final Evidence 1.1 close is pending.
   ```

6. Generate the final baseline-subtracted patch only after step 5, then record the exact
   task/summary/patch hashes that the reviewer must inspect:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 diff_check git diff --check -- tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md scripts/taskctl scripts/evidence_scope.py scripts/tests/test_taskctl.py scripts/tests/test_evidence_scope_v2.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 scope_contract python3 artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/analysis/validate_scope.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 scope ./scripts/evidence_finalize.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 candidate_hashes shasum -a 256 tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/summary.md artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/git/diff.patch
   ```

7. A reviewer other than the implementer reviews the final bytes from step 6 and writes
   their observed 64-lowercase-hex values as `Reviewed-Task-SHA256`,
   `Reviewed-Summary-SHA256`, and `Reviewed-Patch-SHA256` in exactly
   `artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/review/independent_review.md`
   together with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, and `P2: 0`. The implementer does
   not edit that file or change the reviewed task/summary/patch. The reviewer also writes
   the three standard `shasum -a 256` output lines, in task/summary/patch order, to
   `artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/review/candidate.sha256`.
   Verify those reviewer-owned hashes, then execute the current Evidence 1.1 canonical
   close entry, not the not-yet-activated taskctl:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 review_binding shasum -a 256 -c artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/review/candidate.sha256
   python3 scripts/evidence_task.py close REPO-GOVERNANCE-RESET-TASKCTL-20260716-01
   ```

   Canonical close must execute these exact final child argv, in this order, and each must
   return `0`:

   ```bash
   ./scripts/evidence_finalize.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01
   python3 scripts/evidence_validate.py REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 --required-step lint --required-step test --required-step scope
   ./scripts/task_validate.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01
   python3 scripts/atomic_evidence_validate.py REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 --required-step lint --required-step test --required-step scope --required-step independent_review --required-step task_gate
   ```

   After canonical close returns `0`, require the reviewer-hash binding in the final
   bootstrap acceptance as well:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 review_binding shasum -a 256 -c artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/review/candidate.sha256
   python3 scripts/atomic_evidence_validate.py REPO-GOVERNANCE-RESET-TASKCTL-20260716-01 --required-step lint --required-step test --required-step scope --required-step review_binding --required-step independent_review --required-step task_gate
   ```

Expected HTTP status codes: `None` (repository evidence/tooling task).

## Evidence Path

- `artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/**`

## Done Definition

The frozen interface is fully testable through public commands; all failure matrices pass;
GVR-1 inputs remain unchanged; legacy adapters and active governance remain untouched.
