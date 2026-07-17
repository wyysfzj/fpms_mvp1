# FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01

Status: PASS / POST-ENUM REAL-MEMBER REGRESSION APPROVED 2026-07-14
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Materialization batch: `FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01`
Materialization row: `02`
High execution wave: `H3-2`
Risk tier: `HIGH`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- `tasks/postdemo/v8/FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01.md`
- Expected manifest phase: `foundation_external_prerequisite`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: A test-local forward enum makes `RAW_ATTACHMENT` and one future
  unlisted value valid to the existing stored-identity check; calls through the public
  `finalize_external_submission()` service then prove the accepted seam currently reaches
  projection, replay or update behavior instead of returning the frozen evidence conflict.
- GREEN expectation: The public service accepts every original positive role, rejects
  both forward values before projection/replay/write behavior, binds the validated exact
  role into the compare-and-swap predicate, and keeps the accepted seam regressions green.

## Exact Closure Slice

Implement only the external-submission positive-role eligibility rule inside
`finalize_external_submission(command, transaction)`: immediately after the stored
evidence identity is validated and before lifecycle projection capture, replay lookup,
state/review/current checks, carrier mutation, compare-and-swap update or activity append,
require the stored evidence role to be one of the exact original nine accepted role
values; add the validated exact role to the existing compare-and-swap predicate.

## Ultra Contract Freeze — 2026-07-14

This is one fail-closed service rule on the accepted external-submission seam. It does not
reopen the seam's public command/result contract or authorize the deferred RAW enum task.

### Exact placement and positive set

Keep `_validate_stored_identity(version)` as the first stored-role validator. Immediately
after it returns, apply one explicit positive-set membership check to `version.role`.
The positive set contains exactly these nine values and no others:

```text
FILING_FULL_WORD
TRACKED_REVISED_WORD
FILING_COMPONENT
EXTERNAL_XML_PACKAGE
OFFICIAL_SUBMISSION_LIST
OFFICIAL_FINAL_PDF
SUBMITTED_XML
OFFICIAL_RECEIPT
CLIENT_LETTER_WORD
```

Represent eligibility as an explicit immutable positive set of those exact value strings.
Do not derive eligibility from iteration over `EvidenceRole`, from enum validity alone,
from a negative denylist, from role aliases, or from a fallback/default branch. Adding a
future enum member therefore grants no external-submission authority until a later
approved contract explicitly adds its value to this positive set.

### Exact failure and no-write behavior

- `RAW_ATTACHMENT` and every future enum value absent from the positive set fail with
  status 409 and code `EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT`.
- Do not add a new public error code, response shape or status. A malformed stored role
  continues to fail through the accepted stored-identity validation with the same 409
  `EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT` semantics.
- The positive-set rejection occurs before `_capture_lifecycle_projection()`, replay
  activity lookup, `_activity_command()`, replay-carrier validation, state/review/current
  eligibility checks, SQL update, ORM expiration or `append_case_activity()`.
- Fresh and replay calls with a rejected role perform zero business writes. They do not
  change case projection/revision/status fields, the evidence carrier, submission time,
  activity rows or activity-evidence links, and they do not commit or roll back the
  caller-owned transaction.

### Exact compare-and-swap hardening

Add this exact role equality to the existing `DocumentEvidenceVersion` update predicate:

```python
DocumentEvidenceVersion.role == version.role
```

The predicate locks the same exact role value that passed the positive-set check. Do not
rewrite the stored role or replace any existing state, review, reviewer, current-identity
or `final_submitted_at` predicate. Any zero-row update, including a role change after
validation, continues to return the existing status 409
`EXTERNAL_SUBMISSION_CONCURRENCY_CONFLICT`; do not introduce a role-specific concurrency
code.

### Exact task-owned TDD matrix

All new cases live only in
`backend/tests/test_v8_external_submission_role_allowlist.py` and call the public
`finalize_external_submission()` service. Do not test a new private helper directly.

1. Define a test-local forward `EvidenceRole` containing the original nine values plus
   `RAW_ATTACHMENT` and one clearly future unlisted value. Monkeypatch only the workflow
   module's enum binding so both forward values pass the existing stored-identity enum
   validation. Do not edit the accepted enum contract to manufacture RED.
2. RED first: for valid fresh and replay fixtures, require each forward value to return
   409 `EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT`; prove the pre-change public service instead
   reaches a forbidden projection/replay/update sentinel or otherwise misses that exact
   error.
3. Parameterize all nine original values and prove each remains compatible through a
   successful fresh public-service finalization. Preserve the accepted seam's replay and
   caller-owned transaction behavior through its inherited regression suite.
4. Parameterize `RAW_ATTACHMENT` and the future value across fresh and replay calls.
   Prove the exact error and ordering, zero calls to projection/replay/update/activity
   collaborators, and zero database side effects on the case, carrier and activity rows.
5. Prove an actually malformed stored role still returns the accepted 409 evidence
   conflict from stored-identity validation and gains no new error surface.
6. Capture the update issued by an allowed public-service call and prove its where-clause
   contains equality to the loaded exact role. A simulated zero-row compare-and-swap keeps
   the accepted 409 `EXTERNAL_SUBMISSION_CONCURRENCY_CONFLICT` and leaves the transaction
   usable.
7. Run `test_v8_finalize_external_submission_seam.py` unchanged as the inherited
   regression for command/result shape, fresh/replay behavior, review/current/final
   eligibility, projection neutrality, activity linkage, rollback and existing
   concurrency semantics.

The forward enum is test instrumentation only. It grants no production enum member,
stored-role migration, adapter authority or accepted public behavior.

## Post-enum real-member regression overlay — 2026-07-14

This successor test overlay responds to the independent H3-3 review finding recorded at
`artifacts/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01/review/independent_review.md`:
the pre-enum forward-compatibility suite passed, but its RAW cases did not prove runtime
behavior with the real production `EvidenceRole.RAW_ATTACHMENT` member.

- Execution prerequisite state: the H3-3 enum contract is GREEN and production
  `app.modules.documents.evidence_contracts.EvidenceRole.RAW_ATTACHMENT` exists. The H3-3
  task remains `IMPLEMENTED / INDEPENDENT REVIEW PENDING`; this lane therefore freezes the
  successor test contract only and does not claim successor regression acceptance yet.
- Parameterize the original nine role members and `RAW_ATTACHMENT` across fresh and replay
  public `finalize_external_submission()` calls using the production
  `evidence_contracts.EvidenceRole` class directly. These cases MUST NOT monkeypatch the
  workflow module's `EvidenceRole` binding or substitute a test-local enum, mock, string
  stand-in or alias for the production member.
- Only `FUTURE_UNLISTED` remains a forward-compatibility case. That case MAY define a
  test-local forward enum and monkeypatch the workflow module's enum binding, but the
  monkeypatch scope must be limited to the FUTURE_UNLISTED case and must not execute for
  any original-role or RAW_ATTACHMENT case.
- Preserve the already accepted malformed stored-role, exact-role SQL predicate,
  post-validation zero-row CAS, caller-owned transaction usability, collaborator-ordering
  and zero-business-write assertions. Do not weaken or delete the existing matrix while
  converting RAW to the real member.
- The accepted service closure and production implementation remain unchanged. The
  preserved service SHA-256 is
  `d8477e24ccfb65fc7100002c69bc4a33a0c931b23355061c55fce417bac9c66f`.

This overlay adds no production behavior, role authority, endpoint, adapter or migration;
it only freezes the successor post-enum task-owned regression contract for independent
contract rereview.

## Explicit Non-Closure

No `RAW_ATTACHMENT` enum addition; no evidence-contract, schema, migration, seed, HTTP,
endpoint or UI change; no change to stored-identity, review, current-version, final-state,
replay or activity semantics; no role rewrite, alias inference or formal-role promotion;
no filing adapter, OA adapter or prepare-OA implementation; no new error/status surface;
no unrelated cleanup and no second service rule. Do not edit the accepted finalize seam,
its historical evidence, another task, a manifest or any file outside this task's exact
allowlist.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01` — accepted `PASS` before
  this additive guard.

### External, gate and inherited prerequisites

- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` — audit-gate
  prerequisite; it is not a product-graph node. Before this prerequisite is `PASS`, this
  task permits read-only inspection only and MUST NOT initialize evidence, edit product or
  tests, run acceptance, or claim `PASS`.
- `REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01` — accepted `PASS` as
  the hidden active-ownership prerequisite. It is the only active peer that owns the dirty
  validator wrapper `scripts/atomic_evidence_validate.py` and its regression test
  `scripts/tests/test_atomic_evidence_validate.py`; this task owns neither path.
- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` — accepted `PASS` as governance
  prerequisite G1. It is the only active peer that owns the dirty structural-gate test
  `scripts/tests/test_task_validate_jsonl.py`; this task does not own that path.
- `inherited` — `backend/tests/test_v8_finalize_external_submission_seam.py` is a required
  read-only regression input.

### Shared ownership serialization

- `backend/app/modules/documents/evidence_workflow_service.py` order key `2`:
  `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01` → this task →
  `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` → the remaining accepted owners in their
  original relative order.
- No other owner may edit or verify this shared source file concurrently with this task.
- This task and `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` are the only
  H3-2 implementation peers and use the delta-3 batch as their one common authoritative
  execution manifest.
- Both peers may implement concurrently because their source/test allowlists do not
  overlap, but every SQLite-writing RED/GREEN command and shared-file verification enters
  `GLOBAL_SQLITE_SERIAL_QUEUE` with maximum writers `1`.
- Validator execution uses the active path-only ownership manifest at
  `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01/h3_2_active_ownership_manifest.md`.
  Its four exact parser rows are the two H3-2 implementation tasks, the compatibility
  prerequisite and G1; directory-prefix ownership is not an accepted substitute for any
  exact task-ID/task-file pair.

## Remaining Follow-Up Task IDs

- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
- `FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01`

`FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` is also the next serialized owner of the
shared workflow-service file; its separate delta-3 dependency-overlay task owns that
existing task-file update.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01.md`
- `backend/app/modules/documents/evidence_workflow_service.py`
- `backend/tests/test_v8_external_submission_role_allowlist.py`
- `artifacts/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01/**`

No other source, test, task, manifest, script, evidence family or shared ownership file is
authorized. The inherited seam test and both dependency task/evidence families are
read-only. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve the accepted public dataclasses, function signature, `__all__`, caller-owned
  transaction boundary, projection neutrality and activity/result envelope.
- Preserve AGENTS.md SQLite, response/status and permission rules applicable to this
  service-only closure. This task adds no endpoint and has no HTTP response model.
- `RAW_ATTACHMENT` remains unable to satisfy external-submission finalization even after
  the deferred enum extension executes. Content hash, aliases and enum validity carry no
  role authority.
- All SQLite-writing tests and all shared-file verification are globally serialized.

## Verification Commands

- Dependency gates:
- `./scripts/task_validate.sh FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
- `./scripts/task_validate.sh REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`
- `./scripts/task_validate.sh REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01` — `PASS`
- `./scripts/task_validate.sh REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` — `PASS`
- RED, serialized: `cd backend && .venv/bin/pytest -q tests/test_v8_external_submission_role_allowlist.py`; run before product implementation and preserve the expected failure proving the missing positive-role guard.
- GREEN and inherited regression, serialized:
- `cd backend && .venv/bin/pytest -q tests/test_v8_external_submission_role_allowlist.py tests/test_v8_finalize_external_submission_seam.py`
- Post-enum real-member successor regression, SQLite-serialized only after the H3-3
  prerequisite and this overlay contract are independently accepted:
- `cd backend && .venv/bin/pytest -q tests/test_v8_external_submission_role_allowlist.py`
  with production `EvidenceRole` identity for the original nine plus RAW_ATTACHMENT
  fresh/replay cases; only FUTURE_UNLISTED may use the case-local forward-enum monkeypatch.
- Scoped Ruff and format, serialized with this shared-file owner:
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py tests/test_v8_external_submission_role_allowlist.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py tests/test_v8_external_submission_role_allowlist.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py tests/test_v8_external_submission_role_allowlist.py`
- Scoped diff:
- `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/tests/test_v8_external_submission_role_allowlist.py tasks/postdemo/v8/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01.md`
- Task gate:
- `./scripts/task_validate.sh FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`
- Concurrent-wave atomic evidence validation:
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope --manifest artifacts/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01/h3_2_active_ownership_manifest.md --concurrent-task FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01 --concurrent-task REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01 --concurrent-task REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`

Expected HTTP status codes: `None` (public service only; no endpoint). Expected rejected
service status is 409 with `EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT`; a lost exact-role
compare-and-swap remains 409 with `EXTERNAL_SUBMISSION_CONCURRENCY_CONFLICT`.

## Evidence Path

- `artifacts/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when execution starts from a
  dirty worktree.
- Required recorded steps: `lint`, `test`, `independent_review`, and `scope`.

## Done Definition

The accepted finalize seam and G2 audit prerequisite are `PASS`; the exact forward-enum
RED is preserved; the minimum allowlisted service/test change accepts all and only the
original nine roles, rejects RAW and future unlisted roles before projection/replay/write
behavior in fresh and replay paths, and binds the validated exact role into the existing
compare-and-swap; the inherited seam suite, task-scoped Ruff/format/diff, task gate and
common-manifest concurrent-wave atomic validator all pass under serialized SQLite/shared-
file ownership; dirty-baseline and baseline-subtracted evidence exist when required; and
an independent reviewer approves the exact closure, failure ordering, error semantics and
non-closure. Only then may this implementation task be reported `PASS`. Materialization
alone leaves it `NOT STARTED`.
