# REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01

Status: REVIEW / V2 CLOSE PENDING
Risk-Tier: HIGH
Closure-Tags: ["activation", "evidence", "governance", "release"]
Task-Path: tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md
Execution class: `CONTRACT FROZEN`
Chosen runbook: `P0-prereq-heavy-story`

## Authority

- Final approved Governance Reset design.
- Independently accepted PASS outputs from GVR-1 and GVR-2.
- Current root AGENTS/Evidence 1.1 remain authoritative until this task's v2 state PASS.

## Exact Closure Slice

Convert the named legacy entry points to taskctl adapters; update the named task, atomic and
release consumers for mutually exclusive legacy-ledger/v2-state acceptance; generate the
complete legacy PASS ledger; execute frozen-v1/v2 shadow fixtures; build and independently
approve one virtual candidate; install root first and manifest second with crash-safe
bootstrap; add one review-bound frozen-v1 acceptance runner; run frozen legacy acceptance
and v2 close; make state PASS the final activation receipt.

## Explicit Non-Closure

- Do not change GVR-1 modules/validator or GVR-2 taskctl/scope implementation.
- Do not edit historical task artifacts, product code/tests, V8 catalog/plan, SQLite cache/
  FIFO, product Goal status or release state.
- Do not run product full tests, Playwright or release gate.

## Dependencies

- `REPO-GOVERNANCE-RESET-MODULES-20260716-01`: independently accepted PASS.
- `REPO-GOVERNANCE-RESET-TASKCTL-20260716-01`: independently accepted PASS.
- No active product owner and no SQLite/migration/shared-file verification.

## Remaining Follow-Up Task IDs

None.

## Allowed Files

- `tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md`
- `AGENTS.md`
- `docs/agents/manifest.json`
- `docs/agents/legacy-pass-ledger.json`
- `scripts/evidence_init.sh`
- `scripts/evidence_run.sh`
- `scripts/evidence_task.py`
- `scripts/evidence_validate.py`
- `scripts/task_validate.sh`
- `scripts/atomic_evidence_validate.py`
- `scripts/release_gate.sh`
- `scripts/frozen_v1_acceptance.py`
- `scripts/tests/test_governance_reset_adapters.py`
- `scripts/tests/test_governance_reset_consumers.py`
- `scripts/tests/test_governance_reset_activation.py`
- `artifacts/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01/**`

## Verification Commands

Every command below runs from the repository root. `RED` alone must return nonzero before
implementation; every other command must return `0`. The two review commands are executed
by their named independent reviewer identities, never by the implementer. No alternative
argv, product/full/release command or direct helper `init` is allowed.

1. Atomic task shape:

   ```bash
   python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md
   ```

2. Initialize Evidence 1.1 exactly once after GVR-1 and GVR-2 are accepted and this
   contract is frozen:

   ```bash
   ./scripts/evidence_init.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 --task-file tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md --allowlist tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md --allowlist AGENTS.md --allowlist docs/agents/manifest.json --allowlist docs/agents/legacy-pass-ledger.json --allowlist scripts/evidence_init.sh --allowlist scripts/evidence_run.sh --allowlist scripts/evidence_task.py --allowlist scripts/evidence_validate.py --allowlist scripts/task_validate.sh --allowlist scripts/atomic_evidence_validate.py --allowlist scripts/release_gate.sh --allowlist scripts/frozen_v1_acceptance.py --allowlist scripts/tests/test_governance_reset_adapters.py --allowlist scripts/tests/test_governance_reset_consumers.py --allowlist scripts/tests/test_governance_reset_activation.py
   ```

3. Before editing any Adapter, consumer, runner or activation source, record the
   contract-complete RED through the still-active Evidence 1.1 entry. It must return
   nonzero and remain byte-for-byte in the adopted legacy prefix:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 red env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_governance_reset_adapters scripts.tests.test_governance_reset_consumers scripts.tests.test_governance_reset_activation
   ```

4. Still before any source edit, bootstrap this exact task from the non-PASS Evidence 1.1
   bundle into v2. Both candidate files must match the accepted GVR-1 hashes; the candidate
   manifest must validate, select the current task metadata deterministically, declare this
   exact task as `activation_task`, and both GVR dependencies must be accepted PASS. This
   call must preserve the v1 task/baseline/RED bytes, must not recapture baseline, must
   create state `IMPLEMENTING`, and must return `0`:

   ```bash
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 start --task-file tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md --bootstrap-kernel artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/AGENTS.md --bootstrap-manifest artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/manifest.json
   ```

5. Implement the closure, including the adapters and review-bound frozen-v1 runner, then
   run the one final v2 GREEN suite. It must cover clean, dirty, SQLite, direct-helper
   rejection, stale/dual review, each triple mismatch, exact/mutated legacy ledger,
   adopted non-PASS, governance adoption, frozen-runner hash/input rejection, every
   root/manifest/PASS crash point, and v2-equal-or-stricter shadow decisions:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_governance_reset_adapters scripts.tests.test_governance_reset_consumers scripts.tests.test_governance_reset_activation
   ```

6. Exact shell and Python format/lint/compile checks:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 shell_check bash -n scripts/evidence_init.sh scripts/evidence_run.sh scripts/task_validate.sh scripts/release_gate.sh
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 format_check ruff format --check scripts/evidence_task.py scripts/evidence_validate.py scripts/atomic_evidence_validate.py scripts/frozen_v1_acceptance.py scripts/tests/test_governance_reset_adapters.py scripts/tests/test_governance_reset_consumers.py scripts/tests/test_governance_reset_activation.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 lint ruff check scripts/evidence_task.py scripts/evidence_validate.py scripts/atomic_evidence_validate.py scripts/frozen_v1_acceptance.py scripts/tests/test_governance_reset_adapters.py scripts/tests/test_governance_reset_consumers.py scripts/tests/test_governance_reset_activation.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 compile env PYTHONPYCACHEPREFIX=/tmp/fpms-gvr3-pycache python3 -m py_compile scripts/evidence_task.py scripts/evidence_validate.py scripts/atomic_evidence_validate.py scripts/frozen_v1_acceptance.py scripts/tests/test_governance_reset_adapters.py scripts/tests/test_governance_reset_consumers.py scripts/tests/test_governance_reset_activation.py
   ```

7. Run the frozen pre-change Evidence 1.1 consumer against the isolated candidate fixture.
   The frozen consumer bytes remain under this task's artifact tree, but the executable
   runner is the allowlisted, linted, tested and scoped source file
   `scripts/frozen_v1_acceptance.py`. It must prove every captured input hash before
   execution and must not mutate the real task, summary, review, root, manifest or
   repository consumers. The successful `frozen_v1` result/log becomes a mandatory
   pre-review candidate input:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 frozen_v1 python3 scripts/frozen_v1_acceptance.py --task-id REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 --frozen-root artifacts/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01/bootstrap/frozen-v1 --candidate-root artifacts/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01/candidate
   ```

8. Before freezing, change only this task's first Status line to
   `Status: REVIEW / V2 CLOSE PENDING` and complete `summary.md` with that same Status,
   this exact task ID, the observed zero results for test/lint/frozen_v1, a statement that
   canonical scope is recorded separately in v2 events, the explicit non-closure, and
   `Final-Acceptance: PENDING GVR-3 DUAL REVIEW AND V2 CLOSE`. Then freeze
   the virtual candidate. Both candidate inputs are immutable accepted outputs of GVR-1;
   taskctl must virtualize them as the future root paths and bind them, the final summary,
   and all mandatory result/log hashes to the current baseline-subtracted patch. After the
   Status/summary edit, rerun the exact diff and canonical scope before prepare-review:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 diff_check git diff --check -- tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md AGENTS.md docs/agents/manifest.json docs/agents/legacy-pass-ledger.json scripts/evidence_init.sh scripts/evidence_run.sh scripts/evidence_task.py scripts/evidence_validate.py scripts/task_validate.sh scripts/atomic_evidence_validate.py scripts/release_gate.sh scripts/frozen_v1_acceptance.py scripts/tests/test_governance_reset_adapters.py scripts/tests/test_governance_reset_consumers.py scripts/tests/test_governance_reset_activation.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 scope python3 scripts/evidence_scope.py finalize REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 prepare-review --kernel artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/AGENTS.md --manifest artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/manifest.json
   ```

9. The controller grants two distinct leases. The governance reviewer and tooling reviewer
   then write and submit their exact files; each report must contain one `APPROVED` verdict,
   zero P0/P1/P2, and the identical candidate fingerprint/patch/governance triple:

   ```bash
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 review lease governance --reviewer gvr3-governance-reviewer
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 review submit governance --report artifacts/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01/review/governance_axis.md
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 review lease tooling --reviewer gvr3-tooling-reviewer
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 review submit tooling --report artifacts/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01/review/tooling_axis.md
   ```

10. Install exactly the reviewed bytes root-first/manifest-second. `activate` must return
   `0` only after revalidating the actual triple and must leave the repository in
   `GOVERNANCE_STAGED`, never PASS:

   ```bash
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 activate --kernel artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/AGENTS.md --manifest artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/manifest.json
   ```

11. Execute the only v2 close entry. It must validate both submitted axes, then execute the
   exact task-gate and atomic-consumer child argv below, in order, before writing state PASS
   as the final receipt:

   ```bash
   ./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 close
   ```

   ```bash
   ./scripts/task_validate.sh REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01
   python3 scripts/atomic_evidence_validate.py REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 --required-step lint --required-step test --required-step scope --required-step independent_review --required-step task_gate
   ```

Expected HTTP status codes: `None` (repository governance/evidence activation task).

## Evidence Path

- `artifacts/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01/**`

## Done Definition

The actual installed bytes equal the dual-reviewed candidate; frozen legacy and v2 gates
pass; state PASS is written last; active manifest/root validate; legacy/v2 release branches
are mutually exclusive; only then may the product Goal be resumed.
