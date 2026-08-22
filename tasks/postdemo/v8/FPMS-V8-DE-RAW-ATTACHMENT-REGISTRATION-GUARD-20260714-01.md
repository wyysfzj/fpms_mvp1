# FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01

Status: PASS / POST-ENUM REAL-MEMBER REGRESSION APPROVED 2026-07-14
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Wave: `H3-2 — delta-3 product prerequisites`
Phase: `foundation_external_prerequisite` (delta-3; outside the immutable baseline)
Delta-3 supplemental manifest row: `01`
Executor role: Backend Developer / worker
Risk tier: `HIGH` (document/evidence identity and role authority)

## Ultra Contract Resolution — 2026-07-14

This task freezes the fail-closed registration guard required before the separately owned
`RAW_ATTACHMENT` enum extension can be reconsidered. Product and test implementation is
NOT STARTED. High must execute this task only after its accepted product dependencies,
audit prerequisite and shared-file predecessor are PASS.

The contract is exactly one pre-database role/state rule on the existing public
`register_evidence_version()` service. It neither appends the RAW enum member nor changes
any formal evidence role's existing registration authority.

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
  - `Product prerequisite P1 — RAW registration state guard`
  - `Dependency and serialization overrides`
  - `High execution handoff`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- `tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`
- `tasks/postdemo/v8/FPMS-V8-DE-REGISTER-VERSION-20260712-01.md`
- Expected manifest phase: `foundation_external_prerequisite`
- Immutable baseline membership: `outside`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: through the public service and a test-local forward enum, a denied
  `RAW_ATTACHMENT`/`FINAL` or future-role command reaches the transaction because the
  required pre-database guard is missing.
- GREEN expectation: the exact role/state matrix is enforced before transaction or
  activity access, allowed registrations retain the accepted service behavior, and the
  inherited register-version suite stays green.

## Exact Closure Slice

Add one explicit fail-closed role-value/state matrix guard to
`register_evidence_version(command, transaction)` after its accepted basic command
validation and before its first database read, write, flush or activity append: preserve
the original nine roles' `DRAFT | FINAL` registrations, allow `RAW_ATTACHMENT` only as
`DRAFT`, and reject every future unlisted role value.

## Approved Delta-3 Service Contract

### Existing public boundary remains exact

Keep the accepted public callable and frozen command/result types unchanged:

```python
def register_evidence_version(
    command: RegisterEvidenceVersionCommand,
    transaction: Session,
) -> EvidenceVersionResult:
    ...
```

Any task-owned helper remains private. Do not change `RegisterEvidenceVersionCommand`,
`EvidenceVersionResult`, `EvidenceRole`, `EvidenceVersionState` or any other contract
type in this task.

The accepted basic validation order remains intact: exact command type; text-field
shapes; exact current `EvidenceRole` member; exact `EvidenceVersionState` member; and
lowercase SHA-256 content-hash shape. Run the new matrix guard only after those checks
and before the first use of `transaction`. The guard must inspect the role's explicit
machine value so the forward-enum RED/GREEN can freeze `RAW_ATTACHMENT` before the real
enum member exists.

### Exact role-value/state matrix

Each of the original nine role values retains both existing states:

| explicit role value | `DRAFT` | `FINAL` |
| --- | --- | --- |
| `FILING_FULL_WORD` | allow | allow |
| `TRACKED_REVISED_WORD` | allow | allow |
| `FILING_COMPONENT` | allow | allow |
| `EXTERNAL_XML_PACKAGE` | allow | allow |
| `OFFICIAL_SUBMISSION_LIST` | allow | allow |
| `OFFICIAL_FINAL_PDF` | allow | allow |
| `SUBMITTED_XML` | allow | allow |
| `OFFICIAL_RECEIPT` | allow | allow |
| `CLIENT_LETTER_WORD` | allow | allow |

The new and future boundaries are exact:

| role value | `DRAFT` | `FINAL` | exact denied outcome |
| --- | --- | --- | --- |
| `RAW_ATTACHMENT` | allow | deny | `BusinessError`, status 400, code `EVIDENCE_VERSION_INVALID`, `details={"field":"state"}` |
| any future enum value not explicitly listed above | deny | deny | `BusinessError`, status 400, code `EVIDENCE_VERSION_INVALID`, `details={"field":"role"}` |

For an unlisted role, the role failure takes precedence for either otherwise valid state.
No enum iteration, fallback, `else: allow`, or rule that admits every `EvidenceRole`
member is authorized. The allowlist is the ten literal role values above and no others.

### Pre-database and preserved-behavior boundary

For `RAW_ATTACHMENT`/`FINAL` and every future unlisted role, rejection occurs before any
transaction lookup, scalar query, add, execute, flush, refresh or other database access
and before `append_case_activity()`. These failures produce zero version, activity,
evidence-link or case-revision mutation.

For an allowed role/state pair, control proceeds into the already accepted registration
service unchanged. In particular, `RAW_ATTACHMENT`/`DRAFT` creates one immutable version
with stored role `RAW_ATTACHMENT`, state `DRAFT` and review state `PENDING`, while retaining
the accepted caller-owned transaction, activity, identity, version-allocation and error
semantics. This task does not duplicate or rewrite that accepted implementation.

## Exact TDD Contract

High must use the public `register_evidence_version()` interface and this sequence:

1. In `test_v8_raw_attachment_registration_guard.py`, define one test-local forward
   `str, Enum` with the original nine ordered role values, `RAW_ATTACHMENT`, and one
   clearly unlisted future value. Monkeypatch only `evidence_service.EvidenceRole` for
   each test; do not edit `evidence_contracts.py` or the inherited register test.
2. RED first: call the public service with valid command shapes for
   `RAW_ATTACHMENT`/`FINAL` and the future value under both `DRAFT` and `FINAL`. Use a
   transaction sentinel and forbidden activity append so the current missing guard
   fails by attempting database access. Preserve that exact failure as RED evidence.
3. GREEN the denied cases: assert the exact 400/code/details surface above and assert
   zero transaction calls, zero activity append and zero pending ORM writes.
4. Parameterize the original nine values across both `DRAFT` and `FINAL` through the
   public service and prove all eighteen combinations still reach successful accepted
   registration behavior.
5. Through a real serialized SQLite session, prove `RAW_ATTACHMENT`/`DRAFT` returns and
   persists exactly one version whose role is `RAW_ATTACHMENT`, state is `DRAFT` and
   review state is `PENDING`; preserve the accepted registration activity behavior.
6. Run the complete inherited
   `backend/tests/test_v8_document_evidence_register_version.py` suite together with the
   new task test. No inherited test file is allowlisted for edits.

The forward enum must be used before the separately owned real RAW enum extension. RED
must result from the missing guard, not from a changed command shape, invalid hash, missing
fixture, edited production enum or manufactured unrelated failure.

## Explicit Non-Closure

No `EvidenceRole` enum extension; no command/result contract change; no API, upload,
attachment adapter, derivation, current-version, review, promotion, finalization,
external-submission or readiness-gate behavior; no schema, migration, seed, endpoint or
UI; no rewrite of accepted registration semantics for the original nine roles; no second
service rule, task, source file or unrelated cleanup. The H3-2 peer external-submission
role allowlist remains independently owned and must not be implemented here.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-CONTRACTS-20260712-01` — accepted `PASS`.
- `FPMS-V8-DE-REGISTER-VERSION-20260712-01` — accepted `PASS`.

### Audit prerequisite

- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` — must be `PASS` before
  task initialization, product/test edits, acceptance or any PASS claim. It is an audit
  gate and is not a product-graph node.

G1 precedes G2 in the audit lane. This task may receive read-only inspection before G2,
but High implementation begins only in H3-2 after G2 PASS.

### Execution overlay parser prerequisite

- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` (`G1`) — accepted `PASS`.
  It uniquely owns `scripts/tests/test_task_validate_jsonl.py` while the final H3-2
  peer-mode wrapper audits the dirty worktree.
- `REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01` — accepted `PASS`.
- Its accepted ownership of `scripts/atomic_evidence_validate.py` and
  `scripts/tests/test_atomic_evidence_validate.py` remains active while the final H3-2
  peer-mode wrapper validates this task. The wrapper/test dirty paths therefore belong to
  that exact concurrent parser task, not to either product lane.
- The task-local active-ownership manifest is
  `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01/h3_2_active_ownership_manifest.md`.
  It declares exactly this task, the H3-2 product peer, the parser compatibility task,
  and G1 as explicit task-ID/task-file pairs.

### Shared ownership serialization

The frozen `backend/app/modules/documents/evidence_service.py` owner order is:

```text
REGISTER_VERSION
-> REGISTER_DERIVATION
-> CURRENT_VERSION_RULE
-> REVIEW_SERVICE
-> RAW_ATTACHMENT_REGISTRATION_GUARD
-> COMPENSATION_PERIOD_ANNUITY
-> OPEN_LICENSE_ANNUITY
```

This task owns only the `RAW_ATTACHMENT_REGISTRATION_GUARD` position and starts after
`FPMS-V8-DE-REVIEW-SERVICE-20260712-01` is PASS. It must not run concurrently with any
other `evidence_service.py` owner or shared-file verification. H3-2 peer
`FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` edits a different service and
may execute concurrently, but both tasks' SQLite-writing RED/GREEN commands enter
`GLOBAL_SQLITE_SERIAL_QUEUE` with maximum writers `1`.

## Post-enum real-member regression overlay — 2026-07-14

The independent H3-3 review recorded a P1 finding that this task's guard suite still used
a test-local forward enum for `RAW_ATTACHMENT` after the production member existed. This
successor test-only overlay preserves the accepted service implementation, source hash,
closure, non-closure, runbook and allowlist.

- All original nine accepted roles and `RAW_ATTACHMENT` must exercise the production
  `evidence_contracts.EvidenceRole` directly, without monkeypatching the service module's
  enum.
- Only `FUTURE_UNLISTED_ROLE` cases may use a test-local forward enum with a case-scoped
  monkeypatch.
- Preserve the public service path, real SQLite execution, denied-case ordering, all 18
  original positive combinations, and persisted `RAW_ATTACHMENT` / `DRAFT` = `PENDING`
  behavior.
- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01` has an implemented enum and GREEN
  contract test, but its independent review remains pending; do not treat it as PASS.
- No service, closure, non-closure, runbook, dependency ownership or allowlist expansion
  is authorized. Independent contract rereview is required before editing the test.

## Remaining Follow-Up Task IDs

- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`

The follow-up remains blocked until this task and the H3-2 external-submission role guard
both independently PASS. Do not absorb its enum closure here.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01.md`
- `backend/app/modules/documents/evidence_service.py`
- `backend/tests/test_v8_raw_attachment_registration_guard.py`
- `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01/**`

No other source, test, task, manifest, accepted dependency or shared ownership file is
authorized. Inherited regression inputs are read-only. Capture and preserve the dirty
baseline before High edits.

## Runtime Contracts

- Preserve the accepted caller-owned transaction: no service-level commit, rollback,
  close, lock retry or `RETURNING` reliance.
- Preserve all accepted registration validation, lookup, allocation, current-identity,
  immutable version and mandatory `DOCUMENT` activity behavior after an allowed pair.
- Denied matrix cases are pure pre-database failures and append no activity.
- All SQLite-writing tests and all shared-file verification are globally serialized.
- This task adds no endpoint. The exact observable service error status for both denied
  classes is 400; no other HTTP/status-code behavior is changed.

## Verification Commands

- Dependency gates:
  `./scripts/task_validate.sh FPMS-V8-DE-CONTRACTS-20260712-01` and
  `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-VERSION-20260712-01`.
- Audit-prerequisite gate:
  `./scripts/task_validate.sh REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`.
- RED, serialized in `GLOBAL_SQLITE_SERIAL_QUEUE`:
  `cd backend && .venv/bin/pytest -q tests/test_v8_raw_attachment_registration_guard.py`.
  Expected pre-implementation result: nonzero because a denied forward-enum command
  reaches the transaction instead of returning the frozen 400 error.
- GREEN, serialized in `GLOBAL_SQLITE_SERIAL_QUEUE`:
  `cd backend && .venv/bin/pytest -q tests/test_v8_raw_attachment_registration_guard.py`.
- Inherited registration regression, serialized in `GLOBAL_SQLITE_SERIAL_QUEUE`:
  `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_register_version.py tests/test_v8_raw_attachment_registration_guard.py`.
- Scoped Ruff:
  `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_raw_attachment_registration_guard.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_raw_attachment_registration_guard.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_raw_attachment_registration_guard.py`.
- Scoped diff:
  `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_raw_attachment_registration_guard.py tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01.md`.
- Task gate:
  `./scripts/task_validate.sh FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`.
- Active-ownership manifest structure check: use the current
  `scripts.atomic_evidence_validate.parse_manifest()` and require exactly the four
  explicit ID/path pairs declared in
  `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01/h3_2_active_ownership_manifest.md`.
- Atomic evidence validation with the task-local H3-2 execution overlay and all three
  exact active peers:
  `python3 scripts/atomic_evidence_validate.py FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope --manifest artifacts/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01/h3_2_active_ownership_manifest.md --concurrent-task FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01 --concurrent-task REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01 --concurrent-task REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`.

Expected service status codes: 400 for `RAW_ATTACHMENT`/`FINAL` and every future unlisted
role. No endpoint is in scope.

## Evidence Path

- `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, scoped `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when High starts from a
  dirty worktree.
- Required named successful steps: `lint`, `test`, `independent_review`, `scope`.
- RED evidence must record the expected nonzero targeted command separately from the
  later successful `test` step.

## Done Definition

The two accepted product dependencies, G2 audit prerequisite and `REVIEW_SERVICE`
shared-file predecessor remain PASS; the exact public-service RED is preserved; the
minimum allowlisted implementation makes the full matrix GREEN with denied cases proving
zero database/activity access, `RAW_ATTACHMENT`/`DRAFT` proving persisted `PENDING`, and
all original nine `DRAFT | FINAL` combinations preserved; the complete inherited register
suite passes; scoped Ruff/diff/scope checks pass; SQLite and shared-file execution were
serialized; dirty-baseline and baseline-subtracted diff evidence exist when applicable;
an independent reviewer approves this exact closure and non-closure; the task gate and
the common-manifest/peer atomic evidence command both pass. Only then may a lead report
this product task PASS and release the remaining RAW enum task.
