# FPMS-V8-DE-REVIEW-SERVICE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `46`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `418`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Record one irreversible approve/reject decision for one pending evidence version,
require reviewer != creator, preserve that decision as one immutable `DOCUMENT`
activity, and leave current/final promotion outside the review mutation.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Implementation Freeze — 2026-07-13

This section is the complete implementation contract for High. It reconciles the
canonical plan's mandatory `DOCUMENT` activity at line 420 with the frozen D1
single-row carrier, `append_case_activity()`, and the re-frozen register/current
service tasks. It does not invent a second review-history table or widen this task
into current-version, finalization, submission, endpoint or UI behavior.

### Carrier capacity and fail-closed review-history boundary

The accepted D1 carrier stores only the current `review_state`, one `reviewer_id`
and one `reviewed_at`; it cannot preserve two successive decisions. Therefore this
task supports exactly one terminal transition per evidence version:

```text
PENDING -> APPROVED
PENDING -> REJECTED
```

`APPROVED` and `REJECTED` are terminal and immutable in this service. The one
terminal decision is preserved both in the D1 row and in exactly one append-only
`DOCUMENT_EVIDENCE_REVIEW_DECIDED` activity. An exact retry may reuse that activity;
it never creates a second history entry. A new key after a terminal decision, a
second reviewer, or a decision reversal fails closed. Supporting re-review,
withdrawal, supersession or multiple decision history requires a separately
approved carrier/task and is prohibited here.

### Exact task-owned public types and callable

`evidence_contracts.py` remains unchanged. `evidence_service.py` defines the
following task-owned public enum and dataclasses. `EvidenceReviewDecision` inherits
from `str, Enum`; member names and values are identical. Both dataclasses use
`@dataclass(frozen=True, slots=True, kw_only=True)`, and field order is exact.

```python
class EvidenceReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class ReviewEvidenceVersionCommand:
    case_id: str
    evidence_version_id: str
    reviewer_id: str
    decision: EvidenceReviewDecision
    reviewed_at: datetime
    idempotency_key: str


class ReviewEvidenceVersionResult:
    case_id: str
    evidence_version_id: str
    creator_id: str
    reviewer_id: str
    decision: EvidenceReviewDecision
    review_state: EvidenceReviewState
    reviewed_at: datetime
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    idempotency_key: str
    reused: bool
```

Expose exactly this callable; helpers remain private:

```python
def review_evidence_version(
    command: ReviewEvidenceVersionCommand,
    transaction: Session,
) -> ReviewEvidenceVersionResult:
    ...
```

`APPROVE` maps only to `EvidenceReviewState.APPROVED`; `REJECT` maps only to
`EvidenceReviewState.REJECTED`. The result intentionally omits `is_current` and
`is_final`: currentness may change after the historical decision and the review
activity carrier cannot preserve an at-review snapshot of those flags. The later
read projection owns current display state.

### Validation order and exact errors

Perform the following checks in order. Every failure raises the existing
`BusinessError`, performs no new write, and does not mutate case axes/status.

1. Require the exact command type. `case_id`, `evidence_version_id` and
   `reviewer_id` are non-blank strings of at most 36 characters;
   `idempotency_key` is non-blank and at most 103 characters so the 25-character
   activity prefix remains within the W1-L2 128-character carrier; `decision` is
   a real `EvidenceReviewDecision`; and `reviewed_at` is a timezone-naive
   `datetime`. Shape failures use `EVIDENCE_REVIEW_INVALID`, status 400 and
   `details.field`.
2. Resolve `Case(command.case_id)`, then
   `DocumentEvidenceVersion(command.evidence_version_id)`. Missing rows use
   `CASE_NOT_FOUND` and `EVIDENCE_VERSION_NOT_FOUND`, respectively, each with
   status 404.
3. Require `version.case_id == command.case_id`; otherwise use
   `EVIDENCE_REVIEW_CASE_MISMATCH`/400. Require the persisted `creator_id` and
   `content_hash` to satisfy the frozen D1/register-version shapes and persisted
   `state` to be an exact `EvidenceVersionState`; malformed carrier data uses
   `EVIDENCE_REVIEW_STATE_CONFLICT`/409.
4. Require `command.reviewer_id != version.creator_id`; self-review uses
   `EVIDENCE_REVIEW_SELF_REVIEW`/409. This guard also applies to a replay, so an
   invalid maker/reviewer history is never reported successful.
5. Convert the case's nullable central axes and verification status only through
   the frozen lifecycle enums. Unknown stored codes use
   `LIFECYCLE_PROJECTION_CONFLICT`/409. Preserve `Case.status` exactly.
6. Form
   `activity_idempotency_key=f"document-evidence-review:{command.idempotency_key}"`.
   If that same case/key already exists, execute the exact replay path below
   before applying the pending/terminal guard.
7. For a new decision, `review_state` must be an exact frozen enum. A pending row
   must have both `reviewer_id is None` and `reviewed_at is None`; a terminal row
   must have both populated. Any inconsistent tuple or unknown value uses
   `EVIDENCE_REVIEW_STATE_CONFLICT`/409. A consistent terminal row under a new key
   uses `EVIDENCE_REVIEW_ALREADY_DECIDED`/409.
8. Apply the compare-and-swap update and append the mandatory activity exactly as
   frozen below.

No public exception hierarchy, implicit string-to-enum coercion, creator fallback,
reviewer default or wall-clock timestamp generation is authorized.

### Compare-and-swap decision write

For a new decision, update exactly the target D1 row using a predicate on its ID,
case ID, `review_state=PENDING`, `reviewer_id IS NULL` and `reviewed_at IS NULL`.
Set only `review_state` to the mapped terminal value, `reviewer_id` to the command
reviewer, `reviewed_at` to the command timestamp and `updated_at` to the same
timestamp. A zero-row predicate uses
`EVIDENCE_REVIEW_CONCURRENCY_CONFLICT`/409 and appends no activity.

The service may flush the compare-and-swap update and must rely on
`append_case_activity()` for the final flush. It must not call `commit()`,
`rollback()`, close the session, retry a database lock or rely on `RETURNING` for
correctness. If the later append fails, propagate the error; the caller must roll
back the review update. SQLite-writing verification is globally serialized, while
the predicate still protects stale competing reviewers.

### Mandatory DOCUMENT activity

After the successful compare-and-swap, call frozen `append_case_activity()` in the
same `Session`. Pass the captured current case projection as both
`previous_projection` and `current_projection`, unchanged captured `Case.status`
as `legacy_case_status`, and `conflict_codes=()`. Construct its command exactly:

- `event_type="DOCUMENT_EVIDENCE_REVIEW_DECIDED"`,
  `lane=ActivityLane.DOCUMENT`, `effective_at=reviewed_at`,
  `occurred_at=reviewed_at`, `actor_id=reviewer_id`,
  `reviewer_id=reviewer_id`, `source_activity_id=None`,
  `supersedes_event_id=None` and
  `confirmation_status=ConfirmationStatus.CONFIRMED`;
- `idempotency_key=f"document-evidence-review:{idempotency_key}"`;
- payload with exactly `creator_id`, `decision`, `evidence_version_id`,
  `previous_review_state`, `review_state` and `reviewer_id`; values are the stored
  creator ID, decision machine value, version ID, `PENDING`, mapped terminal state
  and command reviewer ID;
- exactly one `EvidenceReference` with the command case,
  `evidence_kind="DOCUMENT_EVIDENCE_VERSION"`,
  `object_type="DocumentEvidenceVersion"`, the reviewed version ID, its immutable
  stored content hash and `captured_at=reviewed_at`.

The append seam owns canonical JSON and deterministic evidence ordering. Empty
central changes are represented only by identical old/new projections and
unchanged legacy status; do not add `center_changes` to payload or call the legacy
projection adapter. Review row, activity, evidence link and case revision increment
commit or roll back together in the caller transaction.

Return the exact task-owned result with the activity result's ID, sequence,
revision and `reused=False`; for a new decision
`activity_sequence == lifecycle_revision`.

### Exact idempotent replay and history consistency

For an existing prefixed case/activity key, build the command-derived event,
payload and evidence reference exactly as above. Reconstruct the activity's old/new
three axes into frozen projections, using the case's current valid verification
value for both. The stored old/new three axes must be identical; otherwise use
`EVIDENCE_REVIEW_HISTORY_CONFLICT`/409. Call `append_case_activity()` before
returning so its frozen comparison rejects any changed decision, reviewer,
timestamp, version, payload or evidence fact with
`LIFECYCLE_IDEMPOTENCY_CONFLICT`/409.

After an exact append replay, require the D1 row to equal the historical decision:
mapped terminal `review_state`, command `reviewer_id` and command `reviewed_at`.
Any mismatch uses `EVIDENCE_REVIEW_HISTORY_CONFLICT`/409. An exact match returns
the original activity ID/sequence/revision with `reused=True` and performs no row,
case, activity or evidence mutation, including after a later activity or
current-version switch. A same decision under a different new key is not a replay
and fails with `EVIDENCE_REVIEW_ALREADY_DECIDED`/409.

### Rejected/current/final promotion boundary

Review records a decision only. It never changes `state`, `current_identity_key`,
`final_submitted_at`, content, role, lineage, version number or attachment/document
identity. A rejection is valid even when the pending version was already current or
`FINAL`; silently hiding that adverse decision by demoting or replacing the row is
not authorized. Such a row remains visibly `REJECTED` and is unusable by downstream
independent-review/readiness gates.

No rejected version may be newly made current: the frozen
`switch_current_evidence_version()` contract already rejects a `REJECTED` target
with `EVIDENCE_CURRENT_REJECTED`/409. There is no task-owned final-promotion input
or mutation here; `DRAFT` stays `DRAFT`, `FINAL` stays `FINAL`, and every later
final/submission readiness seam must require `APPROVED`. This task must not invent a
demotion, replacement selection, final promotion, submission or correction bypass.

### Exact RED/GREEN dataset

The task test must prove through the public callable and real
foreign-key-enabled SQLite sessions:

1. the enum/dataclasses and callable have the exact frozen values, ordered fields,
   frozen/slots/keyword-only shapes and signature;
2. approve and reject each perform only `PENDING ->` the mapped terminal state,
   preserve maker/reviewer separation, return the exact result, append one exact
   `DOCUMENT` activity/evidence link, leave case axes/status unchanged and increment
   revision once;
3. self-review, missing case/version, wrong case, malformed command/timestamp,
   malformed persisted carrier values and inconsistent review tuples produce the
   exact status/code with no committed change;
4. a second decision, decision reversal or different-key repeat fails with
   `EVIDENCE_REVIEW_ALREADY_DECIDED`; a lost compare-and-swap fails with
   `EVIDENCE_REVIEW_CONCURRENCY_CONFLICT`; neither appends activity;
5. exact replay, including after a later activity/current switch, returns the
   original result with `reused=True`; changed facts under the same key use
   `LIFECYCLE_IDEMPOTENCY_CONFLICT`, and carrier/activity disagreement uses
   `EVIDENCE_REVIEW_HISTORY_CONFLICT`;
6. both decisions leave `state`, `current_identity_key`, `final_submitted_at` and
   all immutable evidence facts unchanged; inherited current-version coverage proves
   a rejected target cannot become current;
7. caller rollback removes the review update, activity/evidence row and revision
   increment; an append error likewise leaves no committed task change after caller
   rollback; and
8. the service never commits/rolls back, never calls the legacy projection adapter
   and creates no second review-history carrier.

High must first write the exact test and preserve a RED proving the callable is
missing, then implement only this frozen slice. The inherited serialized GREEN
includes lifecycle append plus register-version, derivation and current-version
tests.

### Reaffirmed non-closure

Do not implement re-review, decision withdrawal/reversal/supersession, a review
history table, evidence state/current/final promotion, receipt/submission workflow,
derivation policy, endpoint/UI/schema changes, legacy status calculation, lifecycle
transition or generic evidence policy. Any future multi-decision history requires a
new explicitly approved schema and task.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): current-version rule; serialized.
  The explicit lifecycle-append prerequisite is required by the canonical plan's
  mandatory `DOCUMENT` activity rule.

### Shared ownership serialization

- `backend/app/modules/documents/evidence_service.py` order key `4`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-SERVICE-20260712-01.md`
- `backend/app/modules/documents/evidence_service.py`
- `backend/tests/test_v8_document_evidence_review_service.py`
- `artifacts/FPMS-V8-DE-REVIEW-SERVICE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_review_service.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_review_service.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_activity_append.py tests/test_v8_document_evidence_register_version.py tests/test_v8_document_evidence_derivation.py tests/test_v8_document_evidence_current_version.py tests/test_v8_document_evidence_review_service.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_review_service.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_review_service.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_review_service.py`
- `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_review_service.py tasks/postdemo/v8/FPMS-V8-DE-REVIEW-SERVICE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-REVIEW-SERVICE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-REVIEW-SERVICE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-SERVICE-20260712-01` pass. Only then may this task be reported PASS.
