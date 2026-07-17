# REPO-GOVERNANCE-RESET-MODULES-20260716-01

Status: PASS / IMPLEMENTATION COMPLETE / PENDING EVIDENCE 1.1 CLOSE
Risk-Tier: HIGH
Closure-Tags: ["governance", "source-authority"]
Task-Path: tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md
Execution class: `CONTRACT FROZEN`
Chosen runbook: `P0-prereq-heavy-story`

## Authority

- `docs/superpowers/specs/2026-07-16-fpms-governance-reset-design.md`, only after its
  immutable final hash and two-axis approval are recorded.
- Current `AGENTS.md` remains authoritative until GVR-3 terminal PASS.

## Exact Closure Slice

Create the six routed governance modules, canonical Rule/Rule-Ref and selector schema,
the governance structure validator and its focused tests. Produce only inside this task's
artifact tree the proposed thin root kernel, proposed manifest, full current-rule
disposition/preservation ledger and candidate governance digest.

## Explicit Non-Closure

- Do not edit root `AGENTS.md` or create active `docs/agents/manifest.json`.
- Do not edit evidence/task/release consumers, adapters, taskctl, product source/tests,
  V8 catalog/plan, historical artifacts or Goal state.
- Do not activate, adopt or release any task under v2.

## Dependencies

- Governance Reset design: final user approval plus independent governance and tooling
  axes `APPROVED`, zero P0/P1/P2.
- No concurrent owner of any Allowed File.

## Remaining Follow-Up Task IDs

- `REPO-GOVERNANCE-RESET-TASKCTL-20260716-01`
- `REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01`

## Allowed Files

- `tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md`
- `docs/agents/README.md`
- `docs/agents/domain-safety.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/source-authority.md`
- `docs/agents/legacy-mvp1.md`
- `scripts/governance_validate.py`
- `scripts/tests/test_governance_validate.py`
- `artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/**`

## Verification Commands

Every command below runs from the repository root. `RED` alone must return nonzero before
implementation; every other command and every child command of canonical close must return
`0`. No alternative argv, product/full/release command or direct helper `init` is allowed.

1. Atomic task shape:

   ```bash
   python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md
   ```

2. Initialize Evidence 1.1 exactly once after this contract is frozen:

   ```bash
   ./scripts/evidence_init.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 --task-file tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md --allowlist tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md --allowlist docs/agents/README.md --allowlist docs/agents/domain-safety.md --allowlist docs/agents/execution.md --allowlist docs/agents/evidence.md --allowlist docs/agents/source-authority.md --allowlist docs/agents/legacy-mvp1.md --allowlist scripts/governance_validate.py --allowlist scripts/tests/test_governance_validate.py
   ```

3. Contract-complete RED, covering every invalid rule/selector/owner/link/fence and every
   omitted preservation family:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 red env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_governance_validate
   ```

4. Final GREEN, format check, lint and compile:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_governance_validate
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 format_check ruff format --check scripts/governance_validate.py scripts/tests/test_governance_validate.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 lint ruff check scripts/governance_validate.py scripts/tests/test_governance_validate.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 compile env PYTHONPYCACHEPREFIX=/tmp/fpms-gvr1-pycache python3 -m py_compile scripts/governance_validate.py scripts/tests/test_governance_validate.py
   ```

5. Validate the exact candidate outputs. These paths are frozen outputs of this task:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 governance_contract python3 scripts/governance_validate.py --root-candidate artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/AGENTS.md --manifest-candidate artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate/manifest.json --disposition-ledger artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/analysis/current_rule_disposition.json
   ```

6. After every final test/lint/contract command is green, and before independent review,
   change only this task's first Status line to:

   ```text
   Status: PASS / IMPLEMENTATION COMPLETE / PENDING EVIDENCE 1.1 CLOSE
   ```

   Then replace this task's `summary.md` with exactly this content. This legacy PASS marker
   is only the current Evidence 1.1 content precondition; it is not final acceptance and
   does not authorize GVR-2, activation or product work.

   ```text
   # Summary
   Status: PASS / IMPLEMENTATION COMPLETE / PENDING EVIDENCE 1.1 CLOSE
   Task-ID: REPO-GOVERNANCE-RESET-MODULES-20260716-01

   ## Commands
   - Canonical results and logs are recorded in results.jsonl and outputs/.

   ## Results
   - Final governance contract, targeted test, format check, lint and compile returned 0; scope and close results are recorded separately in results.jsonl.

   ## Notes
   - Root AGENTS.md and the active manifest remain unchanged; final Evidence 1.1 close is pending.
   ```

7. Generate the final baseline-subtracted patch only after step 6, then record the exact
   task/summary/patch hashes that the reviewer must inspect:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 diff_check git diff --check -- tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md docs/agents/README.md docs/agents/domain-safety.md docs/agents/execution.md docs/agents/evidence.md docs/agents/source-authority.md docs/agents/legacy-mvp1.md scripts/governance_validate.py scripts/tests/test_governance_validate.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 scope_contract python3 artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/analysis/validate_scope.py
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 scope ./scripts/evidence_finalize.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 candidate_hashes shasum -a 256 tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/summary.md artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/git/diff.patch
   ```

8. A reviewer other than the implementer reviews the final bytes from step 7 and writes
   their observed 64-lowercase-hex values as `Reviewed-Task-SHA256`,
   `Reviewed-Summary-SHA256`, and `Reviewed-Patch-SHA256` in exactly
   `artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/review/independent_review.md`
   together with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, and `P2: 0`. The implementer does
   not edit that file or change the reviewed task/summary/patch. The reviewer also writes
   the three standard `shasum -a 256` output lines, in task/summary/patch order, to
   `artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/review/candidate.sha256`.
   Verify those reviewer-owned hashes, then execute the one canonical close entry:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 review_binding shasum -a 256 -c artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/review/candidate.sha256
   python3 scripts/evidence_task.py close REPO-GOVERNANCE-RESET-MODULES-20260716-01
   ```

   Canonical close must execute these exact final child argv, in this order, and each must
   return `0`:

   ```bash
   ./scripts/evidence_finalize.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01
   python3 scripts/evidence_validate.py REPO-GOVERNANCE-RESET-MODULES-20260716-01 --required-step lint --required-step test --required-step scope
   ./scripts/task_validate.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01
   python3 scripts/atomic_evidence_validate.py REPO-GOVERNANCE-RESET-MODULES-20260716-01 --required-step lint --required-step test --required-step scope --required-step independent_review --required-step task_gate
   ```

   After canonical close returns `0`, require the reviewer-hash binding in the final
   bootstrap acceptance as well:

   ```bash
   ./scripts/evidence_run.sh REPO-GOVERNANCE-RESET-MODULES-20260716-01 review_binding shasum -a 256 -c artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/review/candidate.sha256
   python3 scripts/atomic_evidence_validate.py REPO-GOVERNANCE-RESET-MODULES-20260716-01 --required-step lint --required-step test --required-step scope --required-step review_binding --required-step independent_review --required-step task_gate
   ```

Expected HTTP status codes: `None` (repository governance task).

## Evidence Path

- `artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/**`

## Done Definition

All exact files and candidate artifacts exist, every current authoritative rule has a
reviewable disposition and unique owner, focused verification and independent review pass,
and root governance remains unchanged/inactive.
