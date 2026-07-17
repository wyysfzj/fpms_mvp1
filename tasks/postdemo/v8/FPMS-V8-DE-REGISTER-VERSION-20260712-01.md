# FPMS-V8-DE-REGISTER-VERSION-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `43`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `415`
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

Register one immutable version, reject wrong-case attachment/document relations,
and append its mandatory `DOCUMENT` activity with `center_changes={}` in the
same caller-owned transaction.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Re-freeze — 2026-07-13

Independent review found that the first High implementation proved only the
immutable version row. It did not satisfy the canonical plan requirement at
line 420 that all four serialized `evidence_service.py` service tasks append a
`DOCUMENT` activity with empty central changes. The prior PASS is invalid. This
section freezes the missing orchestration contract and adopts the already
implemented validation/version-allocation behavior; it does not add another
business slice.

### Exact public and validation contract

- Keep exactly
  `register_evidence_version(command: RegisterEvidenceVersionCommand,
  transaction: Session) -> EvidenceVersionResult`; helpers remain private.
- Use the frozen dataclasses and enums from `evidence_contracts.py`. Do not add
  another command/result type or change their fields.
- Validate before looking up rows: `command` is the exact frozen command type;
  `case_id`, `document_id`, `attachment_id` and `creator_id` are non-blank
  strings of at most 36 characters; `lineage_key` is non-blank and at most 128
  characters; `role` and `state` are exact enum members; and `content_hash`
  matches lowercase `sha256:` plus 64 hexadecimal characters. Shape failures
  use the existing `BusinessError`, code `EVIDENCE_VERSION_INVALID`, status 400
  and `details.field`.
- Resolve the case, document and attachment in that order. Missing rows use
  `CASE_NOT_FOUND`, `DOCUMENT_NOT_FOUND` and `ATTACHMENT_NOT_FOUND`, each with
  status 404. A document outside the command case uses
  `DOCUMENT_CASE_MISMATCH`/400. An attachment outside the command document uses
  `ATTACHMENT_DOCUMENT_MISMATCH`/400. No evidence version or activity is added
  on these failures.
- Allocate `version_number = max(existing version_number for the same
  case_id + lineage_key, default 0) + 1`. The first version in a lineage stores
  `current_identity_key=f"{case_id}|{lineage_key}"`; a later version never
  steals that key and stores NULL. Initialize review state as `PENDING`, with
  nullable review/final-submission fields unset. Generate the version UUID in
  application code, never update an existing version and return the unchanged
  frozen `EvidenceVersionResult` projection.
- Version-number concurrency policy beyond the accepted carrier constraints,
  current-version switching, review/promotion policy and content immutability
  enforcement outside this creation seam remain outside this task.

### Mandatory DOCUMENT activity

Before inserting the version, read the current case projection into the exact
frozen `LifecycleProjection` enum values. Nullable axes remain `None`. An
unknown stored axis code fails closed with
`LIFECYCLE_PROJECTION_CONFLICT`/409 before the version is added. Preserve the
loaded `Case.status` exactly.

After adding the new version, flush it without committing and use its
SQLite-safe server-populated `created_at` as the single activity timestamp;
refresh that attribute after the flush if the ORM did not populate it. Then
call the frozen `append_case_activity()` in the same `Session`. Construct its
command exactly:

- `event_type="DOCUMENT_EVIDENCE_VERSION_REGISTERED"`,
  `lane=ActivityLane.DOCUMENT`, `effective_at=version.created_at`,
  `occurred_at=version.created_at`, `actor_id=creator_id`, `reviewer_id=None`,
  `source_activity_id=None`, `supersedes_event_id=None`, and
  `confirmation_status=ConfirmationStatus.CONFIRMED`;
- `idempotency_key=f"document-evidence-version:{evidence_version_id}"`;
- payload with exactly the keys `evidence_version_id`, `document_id`,
  `attachment_id`, `lineage_key`, `role`, `version_number`, `state` and
  `review_state`, using stored string/number values; the append seam owns exact
  canonical JSON serialization;
- exactly one `EvidenceReference` using the command case,
  `evidence_kind="DOCUMENT_EVIDENCE_VERSION"`,
  `object_type="DocumentEvidenceVersion"`, the new version ID and stored
  content hash, and `captured_at=version.created_at`.

Pass the same captured projection as both `previous_projection` and
`current_projection`, pass the unchanged captured `Case.status` as
`legacy_case_status`, and pass `conflict_codes=()`. Empty center changes are
represented only by the identical old/new projections and unchanged legacy
status; do not invent a `center_changes` payload field and do not call the
legacy projection adapter.

The version, activity, evidence link and revision increment must commit or roll
back together in the caller transaction. This service may use the initial
version flush and must rely on `append_case_activity()` for its own flush. It
must not commit, roll back, close the session, swallow an append error or return
the activity result. If append fails, propagate the error; the caller rolls the
whole transaction back. The public return remains only
`EvidenceVersionResult`.

The activity idempotency key is scoped to the newly generated immutable
version ID. It prevents a duplicate activity for that version; it does not make
two separate version-registration calls equivalent or reuse a prior version.

### Exact resumed RED/GREEN dataset

The task test must retain its existing immutable-result, wrong-case,
same-lineage allocation, current-identity preservation and caller-rollback
coverage and additionally prove:

1. one successful call persists exactly one version, one `DOCUMENT` event and
   one same-case evidence link with the exact event type, canonical payload,
   evidence identity/hash and equal version/activity timestamps;
2. the event old/new axes are identical, `Case.status` is unchanged, and the
   single activity increments the case revision exactly once;
3. caller rollback removes version/activity/evidence and revision changes;
4. an append conflict/error produces no committed version/activity/evidence or
   case mutation after caller rollback;
5. unknown persisted projection codes fail with
   `LIFECYCLE_PROJECTION_CONFLICT`/409 before version insertion; and
6. the service never commits and never calls the legacy projection adapter.

The prior isolated `4 passed` run is retained as historical partial GREEN, not
task completion. High must first extend the test so it REDs on the missing
activity, then implement only this re-frozen delta and rerun the full task test.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-CONTRACTS-20260712-01`
- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): contracts; the canonical plan's
  mandatory DOCUMENT-activity rule adds the append prerequisite exposed by
  independent review.

### Shared ownership serialization

- `backend/app/modules/documents/evidence_service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-REGISTER-VERSION-20260712-01.md`
- `backend/app/modules/documents/evidence_service.py`
- `backend/tests/test_v8_document_evidence_register_version.py`
- `artifacts/FPMS-V8-DE-REGISTER-VERSION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_register_version.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_register_version.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_activity_append.py tests/test_v8_document_evidence_register_version.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_register_version.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_register_version.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_register_version.py`
- `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_register_version.py tasks/postdemo/v8/FPMS-V8-DE-REGISTER-VERSION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-REGISTER-VERSION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-REGISTER-VERSION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-VERSION-20260712-01` pass. Only then may this task be reported PASS.
