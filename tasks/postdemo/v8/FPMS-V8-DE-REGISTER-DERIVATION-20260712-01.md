# FPMS-V8-DE-REGISTER-DERIVATION-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `44`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `416`
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

Register one same-case parent-child derivation and append its mandatory
`DOCUMENT` activity with `center_changes={}` in the same caller-owned
transaction.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Re-freeze — 2026-07-13

Independent review found that the first High implementation proved only the
derivation row. It did not satisfy the canonical plan requirement that all four
serialized `evidence_service.py` tasks append a `DOCUMENT` activity with empty
central changes. This section resolves that hidden prerequisite and adopts the
already-written fail-closed validation behavior; it does not add a new business
slice.

### Exact public and validation contract

- Keep exactly
  `register_evidence_derivation(command: RegisterEvidenceDerivationCommand,
  transaction: Session) -> EvidenceDerivationResult`; helpers remain private.
- Use the frozen dataclasses and enums from `evidence_contracts.py`. Do not add
  another command/result type or change their fields.
- Validate before looking up rows: all four identifiers are non-blank strings
  of at most 36 characters; `derivation_type` is an exact
  `EvidenceDerivationType`; `derived_at` is timezone-naive; and
  `source_snapshot` is canonical JSON object text produced with
  `ensure_ascii=False`, sorted keys, compact separators and `allow_nan=False`.
  Shape failures use existing `BusinessError`, code
  `EVIDENCE_DERIVATION_INVALID`, status 400 and `details.field`.
- Reject a self-link with `EVIDENCE_DERIVATION_SELF_REFERENCE`/400. Resolve
  parent before child. Missing rows use
  `PARENT_EVIDENCE_VERSION_NOT_FOUND`/404 and
  `CHILD_EVIDENCE_VERSION_NOT_FOUND`/404. Both versions and the command must
  share one case or fail with `EVIDENCE_DERIVATION_CASE_MISMATCH`/400.
- Cycle traversal, role-pair policy, current/review/readiness decisions and a
  uniqueness/idempotency policy for derivation rows remain outside this task.
  Each successful invocation creates one new derivation UUID.

### Mandatory DOCUMENT activity

After validation and row lookup, generate the derivation UUID in application
code, add the derivation without committing, then call the frozen
`append_case_activity()` in the same `Session`. Construct its command exactly:

- `event_type="DOCUMENT_EVIDENCE_DERIVATION_REGISTERED"`,
  `lane=ActivityLane.DOCUMENT`, `effective_at=derived_at`,
  `occurred_at=derived_at`, `actor_id=actor_id`, `reviewer_id=None`,
  `source_activity_id=None`, `supersedes_event_id=None`, and
  `confirmation_status=ConfirmationStatus.CONFIRMED`;
- `idempotency_key=f"document-derivation:{evidence_derivation_id}"`;
- canonical payload object with keys
  `evidence_derivation_id`, `parent_evidence_version_id`,
  `child_evidence_version_id`, `derivation_type`, and `source_snapshot`; the
  last value remains the canonical JSON **text** supplied by the command;
- two evidence references, parent then child before the append seam's own
  deterministic sorting. Each uses the command case,
  `evidence_kind="DOCUMENT_EVIDENCE_VERSION"`,
  `object_type="DocumentEvidenceVersion"`, the corresponding version ID and
  stored content hash, and `captured_at=derived_at`.

Read the current `Case` projection/status and pass identical
`previous_projection` and `current_projection`, the unchanged `Case.status`,
and `conflict_codes=()`. Missing case is `CASE_NOT_FOUND`/404. Unknown stored
projection codes fail closed through the append seam. Do not calculate a
legacy projection and do not change any case axis or status.

The derivation and activity/evidence rows must succeed or roll back together in
the caller transaction. The service may rely on `append_case_activity()` to
flush; it must not commit, roll back, close the session or swallow an append
error. The returned value remains only `EvidenceDerivationResult`; the activity
result is not added to the public result.

### Exact resumed RED/GREEN dataset

The task test must retain the existing shape/same-case/self/missing/rollback
coverage and additionally prove:

1. one successful call persists exactly one derivation, one `DOCUMENT` event
   and two same-case evidence links; event payload, timestamps and identity are
   exact, while all case axes/status remain unchanged;
2. caller rollback removes all three kinds of rows and the revision increment;
3. an append failure leaves no committed derivation/activity/evidence or case
   mutation after caller rollback;
4. the service never commits and never calls the legacy projection adapter.

The prior isolated `16 passed` run is retained as historical partial GREEN, not
task completion. High must first extend the test so it REDs on the missing
activity, then implement only this re-frozen delta and rerun the full task test.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): register version; the canonical
  plan's mandatory DOCUMENT-activity rule adds the append prerequisite exposed
  by independent review.

### Shared ownership serialization

- `backend/app/modules/documents/evidence_service.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01.md`
- `backend/app/modules/documents/evidence_service.py`
- `backend/tests/test_v8_document_evidence_derivation.py`
- `artifacts/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_derivation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_derivation.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_activity_append.py tests/test_v8_document_evidence_derivation.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_derivation.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_derivation.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_derivation.py`
- `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_derivation.py tasks/postdemo/v8/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-REGISTER-DERIVATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-DERIVATION-20260712-01` pass. Only then may this task be reported PASS.
