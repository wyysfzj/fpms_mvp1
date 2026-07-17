# FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-16 / ULTRA CONTRACT FROZEN 2026-07-15
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `H4-0 / D4-03`
Risk tier: `HIGH`
Scope: `Foundation`
Contract state: `CONTRACT FROZEN`
Executor role: High implementation agent

## Authoritative Contract

- Delta-4 specification:
  `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- Frozen specification SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`
- Supplemental batch manifest row: `03 / D4-03`
- Accepted predecessor:
  `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01` (catalog Task 19)

The frozen Delta-4 specification controls if this task text is read ambiguously. A hash
mismatch or non-Status drift fails closed and returns this task to Ultra contract review.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: none for this pure lifecycle rule
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Close exactly one pure lifecycle service rule: `FILING_PREPARATION_STARTED` accepts an
evidence tuple only when it contains exactly one value whose exact type is
`EvidenceReference` and whose fields are exactly valid as follows:

- `evidence_kind == "FILING_WORK_PACKAGE"`;
- `object_type == "OfficialWorkPackage"`;
- `case_id == command.case_id`;
- `object_id` is a nonblank evidence identity;
- `content_hash` full-matches lowercase `sha256:[0-9a-f]{64}`; and
- `captured_at` is a naive `datetime`.

The accepted Task19 projection decision remains unchanged: the rule accepts only the exact
CASE_OPENED projection, changes only `business_stage` from `NEW_CASE` to
`FILING_PREPARATION`, preserves `NOT_SUBMITTED`, `NOT_ESTABLISHED` and `CONFIRMED`, and
returns `oa_sequence=None`. Exact registry lookup, event type, actor, lane, confirmation,
idempotency, event-time, payload and all other accepted command semantics remain unchanged.

## Fail-Closed Contract

The rule returns no decision (`None`) through the accepted public lifecycle-rule surface
for any of the following and must never guess or select a fallback:

- missing evidence, an empty tuple, or a non-tuple evidence carrier;
- zero or multiple work-package evidence values, any extra or unknown item, or a duplicate
  object identity;
- a tuple member whose exact type is not `EvidenceReference`;
- wrong evidence kind, object type or case; blank object identity;
- malformed, shortened, uppercase or otherwise non-exact content hash; or
- missing, non-datetime or timezone-aware capture time.

Tuple order is never authority: reordering cannot turn an invalid set into an accepted
one. The rule does not query whether the referenced object exists. Package existence,
same-transaction source truth and canonical snapshot/hash linkage belong to the later
filing-preparation adapter before it calls `apply_lifecycle_event()`.

## Transaction and Replay Contract

- The rule remains pure and read-only and must not access the caller-owned transaction:
  no SELECT, add, delete, write, flush, refresh, commit, rollback or nested transaction.
- It creates no package, activity, evidence link, projection row or replay record and does
  not mutate the command, projection or transaction identity map.
- Repeated invocation with the same exact immutable command and prior projection returns
  the same decision (or the same no-decision result). This guard does not reconstruct
  evidence from a later mutable package or perform durable replay lookup.
- Existing lifecycle-service idempotency and adapter replay behavior remain unchanged and
  outside this closure.

## Explicit Non-Closure

- No D4-01 `CASE_OPENED`, D4-04 external-submission, receipt, OA, document, fee, deadline
  or any other lifecycle evidence matrix.
- No filing-preparation adapter, package lookup, source snapshot/hash construction,
  activity persistence or actor propagation; existing Task 59 owns those behaviors.
- No direct case projection/status write and no change to the accepted Task19 legal
  transition, registry order or persistence seam.
- No API, router, schema, model, migration, seed, permission, response-envelope, status-code
  or frontend change.
- No unrelated refactor, cleanup, broad test rewrite, repo-wide verification, release gate,
  commit, push, reset, clean, stash or discard.

## Dependencies and Ownership

- `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01` (D4-01) must be PASS and
  independently accepted before this task edits or verifies the shared lifecycle source.
- Accepted PASS `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01` (catalog Task 19)
  supplies the immutable legal transition, registry seam and inherited regression test;
  this task does not reopen its PASS history.
- Shared-source order is strictly D4-01 → D4-03 → D4-04 → catalog Task 21.
  No other task may edit or verify `lifecycle_rules.py` concurrently with this task.
- No migration is owned. The target tests activate the repository autouse Alembic/SQLite
  setup even though their rule bodies are database-free; every pytest run must therefore
  report `READY_FOR_SERIAL_TEST`, wait for controller `GRANT`, and hold
  `GLOBAL_SQLITE_SERIAL_QUEUE` with maximum writer one.

## Inherited Test Migration

`backend/tests/test_v8_lifecycle_filing_preparation_started.py` is allowlisted only for the
minimum fixture migration required by Delta-4: after the task-owned RED is recorded, its
valid `_command()` baseline must carry the exact one-element `FILING_WORK_PACKAGE` /
`OfficialWorkPackage` evidence tuple. Preserve its accepted registry, projection,
malformed-command, prior-projection and transaction-interaction assertions. The new
evidence-matrix cases belong in
`backend/tests/test_v8_lc_filing_preparation_evidence_guard.py`.

## Remaining Follow-Up Task IDs

Follow-up marker: not `None`; the exact remaining follow-up task IDs are:

- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01`
- `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01.md`
- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/tests/test_v8_lifecycle_filing_preparation_started.py`
- `backend/tests/test_v8_lc_filing_preparation_evidence_guard.py`
- `artifacts/FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01/**`

No other path is authorized. Preserve the dirty worktree and subtract the coherent
Evidence 1.1 captured allowlist baseline from this task's scoped diff.

## Verification Commands

### RED

After Evidence 1.1 initialization and serialized-test `GRANT`, add one behavior at a time
to the new guard test. Begin by proving the accepted predecessor incorrectly permits a
tuple that is not the exact single work-package evidence reference. Record the expected
nonzero RED before editing product code or the inherited Task19 fixture:

```bash
cd backend && .venv/bin/pytest -q tests/test_v8_lc_filing_preparation_evidence_guard.py
```

### GREEN

Implement the smallest pure-rule correction and the narrow inherited-fixture migration,
then run under the same serialized-test grant:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_lc_filing_preparation_evidence_guard.py \
  tests/test_v8_lifecycle_filing_preparation_started.py
```

Coverage must prove the exact positive tuple, deterministic repeated invocation, every
fail-closed class named above, no transaction interaction and the unchanged accepted
Task19 projection. Do not broaden into another lifecycle event.

### Scoped lint, format and scope

```bash
cd backend && .venv/bin/ruff check --fix \
  app/modules/cases/lifecycle_rules.py \
  tests/test_v8_lifecycle_filing_preparation_started.py \
  tests/test_v8_lc_filing_preparation_evidence_guard.py
cd backend && .venv/bin/ruff format \
  app/modules/cases/lifecycle_rules.py \
  tests/test_v8_lifecycle_filing_preparation_started.py \
  tests/test_v8_lc_filing_preparation_evidence_guard.py
cd backend && .venv/bin/ruff check \
  app/modules/cases/lifecycle_rules.py \
  tests/test_v8_lifecycle_filing_preparation_started.py \
  tests/test_v8_lc_filing_preparation_evidence_guard.py
git diff --check -- \
  backend/app/modules/cases/lifecycle_rules.py \
  backend/tests/test_v8_lifecycle_filing_preparation_started.py \
  backend/tests/test_v8_lc_filing_preparation_evidence_guard.py \
  tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01.md
```

Do not run repo-wide Ruff, pytest, frontend build, Playwright or release gate.

### Final task-local gates

```bash
./scripts/task_validate.sh FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01
python3 scripts/atomic_evidence_validate.py \
  FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01 \
  --required-step lint \
  --required-step test \
  --required-step independent_review \
  --required-step scope
```

## Evidence Path

- `artifacts/FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01/**`

### Evidence and independent acceptance

- Initialize only through Evidence 1.1 after both direct dependencies are accepted:

  ```bash
  ./scripts/evidence_init.sh FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01 \
    --task-file tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01.md \
    --allowlist backend/app/modules/cases/lifecycle_rules.py \
    --allowlist backend/tests/test_v8_lifecycle_filing_preparation_started.py \
    --allowlist backend/tests/test_v8_lc_filing_preparation_evidence_guard.py
  ```

- Record the latest expected nonzero RED and zero GREEN/lint/scope results with their logs
  under the task-local evidence path; do not hand-author `results.jsonl`.
- Produce dirty-baseline artifacts when applicable and a baseline-subtracted scoped
  `git/diff.patch` containing every tracked/untracked task change and no outside path.
- One independent domain reviewer must issue an evidence-backed APPROVED zero-finding
  verdict; the implementer cannot approve this task.
- PASS requires task-local `results.jsonl`, `summary.md`, scoped `git/diff.patch`, applicable
  dirty-baseline artifacts, scope validation, the repository task gate and atomic evidence
  validation.

## Done Definition

- The exact one-reference `FILING_PREPARATION_STARTED` evidence matrix is enforced fail
  closed through the accepted public lifecycle-rule seam.
- The accepted Task19 legal projection, registry and command behavior remains unchanged;
  the inherited test changes only its now-required valid evidence fixture.
- The rule remains pure, transaction-free and deterministic on exact repeated input, with
  all package persistence, source resolution, hash creation and durable replay outside the
  closure.
- Required RED and GREEN, inherited regression, scoped Ruff/format/scope, serialized SQLite
  verification and Evidence 1.1 artifacts are present and latest.
- Independent review is APPROVED with zero findings; repository task gate and atomic
  evidence validation PASS.
- The exact closure is complete, all non-closure boundaries and shared-source serialization
  are respected, and no follow-up closure was absorbed.
