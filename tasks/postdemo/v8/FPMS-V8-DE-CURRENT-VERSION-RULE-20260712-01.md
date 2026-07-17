# FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `45`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `417`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Switch current working version; final version linked to a receipt cannot be ordinarily replaced.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Implementation Freeze — 2026-07-13

This section is the complete implementation contract for High. It reconciles
the canonical plan's mandatory `DOCUMENT` activity at line 420 with the
already frozen register-version, register-derivation and lifecycle-append
contracts. It adds no receipt workflow, correction override or review policy.

### Exact task-owned public types and callable

`evidence_contracts.py` remains unchanged. `evidence_service.py` defines these
two task-owned public dataclasses exactly; both use
`@dataclass(frozen=True, slots=True, kw_only=True)` and the ordered fields below:

```python
class SwitchCurrentEvidenceVersionCommand:
    case_id: str
    expected_current_evidence_version_id: str
    target_evidence_version_id: str
    actor_id: str
    switched_at: datetime
    idempotency_key: str

class SwitchCurrentEvidenceVersionResult:
    case_id: str
    lineage_key: str
    previous_current_evidence_version_id: str
    current_evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    switched_at: datetime
    idempotency_key: str
    reused: bool
```

Expose exactly this callable; helpers remain private:

```python
def switch_current_evidence_version(
    command: SwitchCurrentEvidenceVersionCommand,
    transaction: Session,
) -> SwitchCurrentEvidenceVersionResult:
    ...
```

The command carries an expected-current identity so the switch is an explicit
compare-and-swap, not a last-writer-wins assignment. The result describes the
historical switch represented by its idempotency key; on a replay it does not
claim that the target is still current after later legitimate switches.

### Validation order and exact errors

Perform these checks in order before a new switch writes anything:

1. Require the exact command type. All four identifiers are non-blank strings;
   `case_id`, both evidence-version IDs and `actor_id` are at most 36
   characters, while `idempotency_key` is at most 100 characters so the
   prefixed activity key remains within the W1-L2 128-character carrier.
   `switched_at` must be a timezone-naive `datetime`. The expected and target
   IDs must differ. Shape failures use existing `BusinessError`, code
   `EVIDENCE_CURRENT_INVALID`, status 400 and `details.field`.
2. Resolve `Case(command.case_id)`, then the expected-current version, then the
   target version. Missing rows use `CASE_NOT_FOUND`,
   `EXPECTED_EVIDENCE_VERSION_NOT_FOUND` and
   `TARGET_EVIDENCE_VERSION_NOT_FOUND`, each with status 404.
3. Both versions must have `case_id == command.case_id`, otherwise
   `EVIDENCE_CURRENT_CASE_MISMATCH`/400. Their non-blank `lineage_key` values
   must be equal, otherwise `EVIDENCE_CURRENT_LINEAGE_MISMATCH`/409.
4. Convert stored case axes and verification status only through the frozen
   lifecycle enums; nullable values remain `None`. An unknown stored code uses
   `LIFECYCLE_PROJECTION_CONFLICT`/409. Preserve `Case.status` exactly.
5. Form the activity idempotency key
   `document-current-version:{command.idempotency_key}`. If that same case/key
   already exists, use the exact replay path below before applying current,
   review-state or receipt-lock guards. This keeps a valid historical replay
   valid after later review, lifecycle or current-version changes.
6. For a new switch, stored `state` and `review_state` on both versions must be
   exact frozen enum values. Unknown values use
   `EVIDENCE_CURRENT_STATE_CONFLICT`/409. A target whose review state is
   `REJECTED` uses `EVIDENCE_CURRENT_REJECTED`/409. `PENDING` and `APPROVED`
   targets are both allowed here; approval readiness belongs to later policy
   tasks.
7. Compute `current_identity_key=f"{case_id}|{lineage_key}"`. Exactly one row
   must hold it and its ID must equal
   `expected_current_evidence_version_id`. If no row holds it, use
   `EVIDENCE_CURRENT_NOT_FOUND`/409; a different holder or a target already
   carrying any current identity uses `EVIDENCE_CURRENT_CONFLICT`/409.
8. If the expected current row is `FINAL` and is the parent of any same-case
   `DocumentEvidenceDerivation` whose exact type is `RECEIPT_LINK`, reject the
   ordinary switch with `EVIDENCE_CURRENT_RECEIPT_LOCKED`/409. The frozen D2
   `RECEIPT_LINK` is the authoritative receipt-link fact for this rule; do not
   infer linkage from attachment flags, manifests or
   `OfficialWorkPackageReceipt`. A final row without that derivation may be
   switched. There is no override flag or privileged bypass in this task.

All validation and conflicts raise the existing `BusinessError`. Do not add a
public exception hierarchy or translate these service errors into HTTP
responses here.

### Current-identity switch and concurrency

For a new switch, clear the expected row's exact current identity first, flush
that change to release the SQLite unique key, then set the target row to the
same identity. Update only `current_identity_key`; every immutable evidence
fact remains unchanged. Use compare-and-swap predicates on the expected row ID
plus exact current key and on the target row ID plus NULL current key. A lost
predicate uses `EVIDENCE_CURRENT_CONCURRENCY_CONFLICT`/409 and appends no
activity. The caller must roll back after any error that follows a write.

The service may flush to release the unique current key and may rely on
`append_case_activity()` for the final flush. It must not call `commit()`,
`rollback()`, close the session, retry a database lock, or use `RETURNING` for
correctness. SQLite-writing verification remains globally serialized; the
expected-current predicate still protects stale commands across serialized
transactions.

### Mandatory DOCUMENT activity

After assigning the target current identity, call frozen
`append_case_activity()` in the same `Session`. For a new switch, pass the
captured current case projection as both `previous_projection` and
`current_projection`, the unchanged captured `Case.status` as
`legacy_case_status`, and `conflict_codes=()`. Construct the command exactly:

- `event_type="DOCUMENT_EVIDENCE_CURRENT_VERSION_SWITCHED"`,
  `lane=ActivityLane.DOCUMENT`, `effective_at=switched_at`,
  `occurred_at=switched_at`, `actor_id=actor_id`, `reviewer_id=None`,
  `source_activity_id=None`, `supersedes_event_id=None` and
  `confirmation_status=ConfirmationStatus.CONFIRMED`;
- `idempotency_key=f"document-current-version:{idempotency_key}"`;
- payload with exactly `current_evidence_version_id`, `lineage_key` and
  `previous_current_evidence_version_id`, using the target ID, shared lineage
  and expected-current ID respectively; the append seam owns canonical JSON;
- exactly two evidence references, expected-current then target before the
  append seam's deterministic sorting. Each uses the command case,
  `evidence_kind="DOCUMENT_EVIDENCE_VERSION"`,
  `object_type="DocumentEvidenceVersion"`, the corresponding version ID and
  stored content hash, and `captured_at=switched_at`.

The switch, activity, two evidence links and case revision increment succeed
or roll back together in the caller transaction. The activity must have empty
central changes: old/new axes are identical and neither the projection nor
`Case.status` changes. Do not invent a `center_changes` payload member, call
the legacy projection adapter, or return a second version row.

Return the exact task-owned result using the activity result's ID, sequence,
revision and `reused` flag. For a new switch `reused=False` and
`activity_sequence == lifecycle_revision`.

### Exact idempotent replay

The prefixed case/activity key is the switch idempotency identity. On an
existing key, reconstruct the append decision from the stored activity's
old/new central axes (and the current valid verification value), then call
`append_case_activity()` with the same command-derived payload, timestamps,
actor and evidence references. This delegates exact event/payload/evidence
comparison to the frozen append seam.

- An exact replay returns the original activity ID/sequence/revision with
  `reused=True` and performs no evidence-version, case, activity or evidence
  mutation, even if a later activity or later current-version switch exists.
- Reusing the key with a changed expected/target ID, actor, timestamp, payload
  fact or evidence identity/hash delegates to
  `LIFECYCLE_IDEMPOTENCY_CONFLICT`/409 after the referenced versions pass the
  earlier existence checks; a non-existent changed ID retains the frozen 404
  lookup priority.
- An already-current target without a matching historical activity is not a
  successful no-op; it uses `EVIDENCE_CURRENT_CONFLICT`/409. Each real switch
  therefore has exactly one auditable activity.

### Exact RED/GREEN dataset

The task test must prove through the public callable and real
foreign-key-enabled SQLite sessions:

1. the two task-owned dataclasses have the exact frozen/slots/keyword-only
   shapes and the callable has the exact signature;
2. a normal same-case/same-lineage switch moves only the unique current key,
   returns the exact result, appends one `DOCUMENT` activity and two evidence
   links with exact payload/timestamps/hashes, leaves all case axes/status
   unchanged and increments revision once;
3. missing case/version, wrong case, different lineage, same IDs, malformed
   command/timestamp, unknown persisted enum/projection code and rejected
   target each produce the exact status/code with no committed change;
4. a current `FINAL` parent with a same-case `RECEIPT_LINK` derivation is
   locked, while a final current version without that derivation is switchable;
5. missing/different current identity and a stale expected-current command
   after another serialized transaction fail with the exact 409 code and do
   not append an activity;
6. exact replay, including replay after a later activity/switch, returns the
   original result with `reused=True`; changed facts under the same key fail
   with `LIFECYCLE_IDEMPOTENCY_CONFLICT` and do not mutate current identity;
7. caller rollback removes the current-key move, activity/evidence rows and
   revision increment; an append error propagated by the service likewise
   leaves no committed task change after caller rollback; and
8. the service never commits/rolls back and never calls the legacy projection
   adapter.

High must first write the exact test and preserve a RED proving the callable is
missing, then implement only this frozen slice. The inherited serialized GREEN
includes the register-version, register-derivation and lifecycle-append tests.

### Reaffirmed non-closure

Do not implement evidence review decisions, final-submission timestamps,
receipt creation/archive, receipt role-pair validation, derivation cycle
policy, correction/override replacement, endpoint/UI/schema changes, legacy
status calculation, case lifecycle transitions or generic evidence policy. A
future controlled correction of a receipt-locked final version requires its
own explicitly approved task; this ordinary switch has no bypass.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): register version; the frozen
  final-receipt guard requires the D2 derivation fact and the canonical plan's
  mandatory `DOCUMENT` activity requires the lifecycle append seam.

### Shared ownership serialization

- `backend/app/modules/documents/evidence_service.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01.md`
- `backend/app/modules/documents/evidence_service.py`
- `backend/tests/test_v8_document_evidence_current_version.py`
- `artifacts/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_current_version.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_current_version.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_activity_append.py tests/test_v8_document_evidence_register_version.py tests/test_v8_document_evidence_derivation.py tests/test_v8_document_evidence_current_version.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_current_version.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_current_version.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_current_version.py`
- `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_current_version.py tasks/postdemo/v8/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01` pass. Only then may this task be reported PASS.
