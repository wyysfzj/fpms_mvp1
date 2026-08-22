# FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-16 / ULTRA CONTRACT FROZEN 2026-07-15

## Risk and ownership

- Risk: HIGH — guards the exact evidence-reference shape for a lifecycle transition.
- Atomic owner: exactly one implementing agent owns this task-file path while work is active.
- Closure slice: only the evidence guard for `FILING_EXTERNAL_SUBMISSION_RECORDED` frozen by D4-04.
- Runbook: `P0-prereq-heavy-story`.
- Authority: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 102–138, D4-04 catalog entry.
- Contract state: frozen; non-matching input returns no lifecycle-rule decision.

## Dependencies

- `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01` must have an independently accepted PASS.
- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01` is the accepted projection-behavior dependency and must remain accepted.
- Do not begin implementation or initialize evidence until both prerequisite verdicts are present and valid.

## Remaining Follow-Up Task IDs

- None within this atomic task. Any newly discovered prerequisite or closure slice requires a separately frozen task ID.

## Exact Closure Slice

Implement and verify only the evidence guard for event `FILING_EXTERNAL_SUBMISSION_RECORDED` at the `apply_lifecycle_event` rule boundary.

The guard accepts an unordered evidence tuple only when all of these conditions hold:

- The tuple contains exactly two entries and both are exact `EvidenceReference` values.
- Exactly one entry is `FINAL_SUBMISSION_VERSION` / `DocumentEvidenceVersion`.
- Exactly one entry is `MANUAL_EXTERNAL_SUBMISSION_RECORD` / `CaseActivityEvent`.
- Both references carry exactly the command `case_id`.
- The two referenced object identities are distinct.
- Each reference carries a full lowercase hash matching `sha256:[0-9a-f]{64}`.
- Each reference carries a naive `datetime` value.

Missing, extra, duplicate, unknown, wrong-reference-type, wrong-object-type, wrong-case, invalid-hash, or non-naive/wrong-time input returns no decision. When the exact tuple is accepted, preserve and return the original projection decision unchanged; otherwise return `None`. The rule contract remains `LifecycleRuleDecision | None`.

The guard remains pure, read-only, and transaction-free. It never validates source existence, currentness, review state, lifecycle status, hash linkage, or provenance. Adapters/resolvers complete those validations before calling `apply_lifecycle_event`.

Add focused tests for the exact positive tuple and every listed deny dimension.

## Explicit Non-Closure

- No UI, API route, schema, migration, seed, fixture, workflow, document-generation, upload, fee, permission, notification, or release-gate changes.
- No changes to filing status vocabulary, lifecycle deadlines, customer-decision gates, either named dependency, or event semantics outside the exact D4-04 guard.
- No source lookup, persistence read/write, transaction, currentness/review/status check, hash-linkage check, or provenance validation in the rule.
- No refactor, rename, formatting cleanup, generalized evidence framework, speculative compatibility path, or adjacent lifecycle behavior.
- No production-data mutation and no broad repository test or lint run.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01.md`
- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/tests/test_v8_lifecycle_filing_external_submission.py`
- `backend/tests/test_v8_lc_filing_external_submission_evidence_guard.py`
- `artifacts/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01/**`

Every tracked or untracked path outside this allowlist is out of scope. Stop and split/replan if another path becomes necessary.

## Required gates

### Gate 0 — prerequisite and contract preflight

- Confirm `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01` has independently accepted PASS evidence and `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01` remains accepted.
- Confirm this task passes the repository atomic task check.
- Confirm the frozen authority hash/input has not changed.
- Capture the exact allowlist baseline with the repository Evidence 1.1 entry point.

### Gate 1 — RED

- Add one focused `apply_lifecycle_event` test at a time for the exact tuple or one deny dimension.
- Run the targeted test and record the expected failure before production edits.
- The RED failure must demonstrate missing D4-04 behavior, not test setup or import failure.

### Gate 2 — GREEN

- Make the smallest surgical change in `lifecycle_rules.py` that satisfies the exact tuple guard.
- Run the focused test after each behavior increment.
- Keep every non-closure behavior unchanged.

### Gate 3 — targeted regression

- Run both allowlisted test modules together.
- Run targeted lint/static checks only for allowlisted Python files when the repository task contract requires them.
- Serialize any SQLite-writing verification and obtain the controller grant before acquiring the repository lock.

### Gate 4 — evidence and independent acceptance

- Produce task-local Evidence 1.1 artifacts through repository-owned commands.
- Obtain one independent reviewer verdict for this HIGH, contract-frozen task.
- Reviewer must compare the frozen exact-tuple guard, baseline-subtracted diff, targeted results, and non-closure boundary.
- Final verdict must be approved with zero findings; the implementer cannot approve its own work.

### Gate 5 — repository acceptance

- Validate scope against the exact allowlist.
- Run the repository task gate.
- Run atomic evidence validation using the shared Evidence 1.1 consumer.
- Any missing or non-latest required result, log, summary, scoped diff, dirty baseline, or review verdict fails closed.

## Verification Commands

Run from the repository root after prerequisites and Evidence 1.1 initialization:

```bash
pytest -q backend/tests/test_v8_lc_filing_external_submission_evidence_guard.py
pytest -q backend/tests/test_v8_lifecycle_filing_external_submission.py backend/tests/test_v8_lc_filing_external_submission_evidence_guard.py
```

If repository configuration requires a wrapper or environment prefix, use the existing repository form without broadening test scope, and record the exact command and exit code.

## Evidence Path

Evidence root:

`artifacts/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01/`

Required evidence includes:

- `results.jsonl` with latest required commands, timestamps, and exit codes.
- `summary.md` stating PASS/FAIL/BLOCKED, closure completed, non-closure respected, modified files, and observed results.
- `git/diff.patch` containing the baseline-subtracted scoped tracked and untracked allowlist diff.
- Dirty-baseline artifacts when any allowlisted or outside-allowlist dirt existed at initialization.
- Targeted RED and GREEN logs, combined regression log, scope validation, repository task-gate output, and atomic evidence validation output.
- Independent review record with reviewer identity, frozen-authority comparison, separate verdict, and zero findings for approval.

Initialize only with:

```bash
./scripts/evidence_init.sh FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01 \
  --task-file tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01.md \
  --allowlist tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01.md \
  --allowlist backend/app/modules/cases/lifecycle_rules.py \
  --allowlist backend/tests/test_v8_lifecycle_filing_external_submission.py \
  --allowlist backend/tests/test_v8_lc_filing_external_submission_evidence_guard.py \
  --allowlist artifacts/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01
```

Do not call the installed evidence helper `init` entry point directly.

## Done Definition

This task is DONE only when all of the following are true:

- `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01` remains independently accepted PASS and `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01` remains accepted.
- The exact positive tuple and every missing/extra/duplicate/unknown/type/case/hash/time deny dimension are covered through `apply_lifecycle_event`.
- Accepted input preserves the original projection decision; all rejected input returns `None` under the `LifecycleRuleDecision | None` contract.
- The rule is proven pure, read-only, and transaction-free, with source validation left to adapters/resolvers.
- Both targeted test modules pass together with recorded latest results.
- The baseline-subtracted diff contains only exact allowlist paths and no non-closure behavior changed.
- Required Evidence 1.1 artifacts are complete and internally consistent.
- One independent reviewer issues an approved, zero-finding verdict.
- Repository task gate and atomic evidence validation both pass.

Until then, status remains NOT STARTED, IN PROGRESS, FAIL, or BLOCKED as evidenced; never report PASS by inference.
