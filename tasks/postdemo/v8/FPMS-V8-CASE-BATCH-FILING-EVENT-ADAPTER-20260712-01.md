# FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `60`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `446`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Batch filing calls external-submission lifecycle event instead of assigning `WAITING_RECEIPT`.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task08:FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts.
- `inherited` — `Task09:FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts.

- Approved source dependency cell (verbatim): external-submission rule; Tasks08–09 regressions

### Shared ownership serialization

- `backend/app/modules/cases/service.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_v8_batch_filing_lifecycle_adapter.py`
- `artifacts/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_batch_filing_lifecycle_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_batch_filing_lifecycle_adapter.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts src/tests/addgap-filing-case-entry.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/service.py tests/test_v8_batch_filing_lifecycle_adapter.py && .venv/bin/ruff format app/modules/cases/service.py tests/test_v8_batch_filing_lifecycle_adapter.py && .venv/bin/ruff check app/modules/cases/service.py tests/test_v8_batch_filing_lifecycle_adapter.py`
- `git diff --check -- backend/app/modules/cases/service.py backend/tests/test_v8_batch_filing_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Authority and latest-wins boundary

- Authoritative Delta-4 contract:
  `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`,
  especially lines 247–290.
- Frozen Delta-4 specification SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`.
- Supplemental batch authority: row `17 / M4-E / H4-2` of
  `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk is `HIGH`; this contract is frozen for High execution, while product implementation
  and task evidence remain `NOT STARTED` in this materialization lane.
- This section is the latest-wins authority only for the Delta-4 batch document/lifecycle
  evidence contract, dependencies, runbook and serialization below. The inherited task body
  and prior blocker status remain immutable history and do not constitute acceptance.
- `chosen_runbook: P0-prereq-heavy-story` governs Delta-4 and High execution. The historical
  `P0-single-lane-story` classification above is preserved only as baseline history.

### Exact atomic batch filing closure

Change only the existing `execute_batch_filing()` adapter in
`backend/app/modules/cases/service.py`. Process selected cases in the request's stable,
de-duplicated order. For every case, resolve the exact `FILING_PREP:<case_id>` package and
call `resolve_filing_final_evidence()`; do not select a latest package/version, infer from a
filename or duplicate the resolver's role, current, review, ownership or hash validation.

For each fresh submission:

1. Require both resolver activity fields to be `None` before finalization.
2. Use the exact naive submission time
   `datetime.combine(submitted_date, time.min)`; do not invent a wall clock or timezone.
3. Require the existing server-owned `user_id` as the nonblank actor. Do not accept a client
   actor, infer one from stored evidence or substitute a fallback/system identity.
4. Call `finalize_external_submission()` exactly once with base idempotency key
   `batch-filing:<case_id>:<submitted_date.isoformat()>`.
5. Re-resolve the same package and require the exact matching persisted finalized activity,
   evidence version, content hash, submission time and actor-bound activity truth.
6. Call `apply_lifecycle_event(FILING_EXTERNAL_SUBMISSION_RECORDED)` exactly once with
   lifecycle idempotency key
   `batch-filing-lifecycle:<case_id>:<submitted_date.isoformat()>`, the same actor and
   submitted time, and the exact evidence pair below.

The document activity idempotency key is exactly
`document-external-submission:batch-filing:<case_id>:<submitted_date.isoformat()>`.
Its accepted immutable four-key payload remains exactly:

```json
{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<submitted_at.isoformat()>"}
```

After re-resolution, construct the canonical activity snapshot with exactly the accepted
keys and values:

```json
{"activity_id":"<activity.id>","activity_type":"DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED","actor_id":"<activity.actor_id>","case_id":"<case_id>","confirmation_status":"CONFIRMED","effective_at":"<submitted_at.isoformat()>","evidence":[{"captured_at":"<submitted_at.isoformat()>","content_hash":"<version.content_hash>","evidence_kind":"DOCUMENT_EVIDENCE_VERSION","object_id":"<version.id>","object_type":"DocumentEvidenceVersion"}],"idempotency_key":"document-external-submission:batch-filing:<case_id>:<submitted_date.isoformat()>","lane":"DOCUMENT","occurred_at":"<submitted_at.isoformat()>","payload":{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<submitted_at.isoformat()>"},"reviewer_id":"<version.reviewer_id>"}
```

Serialize that snapshot as UTF-8 sorted-key compact JSON with no ASCII escaping, NaN or
trailing newline. Its hash is exactly
`"sha256:" + sha256(exact_snapshot_bytes).hexdigest()` and must full-match lowercase
`sha256:[0-9a-f]{64}`. No created/updated timestamp, database order or later mutable field
participates.

The lifecycle evidence tuple contains exactly these two `EvidenceReference` values and no
other member:

| Cardinality | `evidence_kind` | `object_type` | Object/hash/time authority |
| --- | --- | --- | --- |
| exactly 1 | `FINAL_SUBMISSION_VERSION` | `DocumentEvidenceVersion` | resolver version ID / persisted version content hash / resolver `reviewed_at` |
| exactly 1 | `MANUAL_EXTERNAL_SUBMISSION_RECORD` | `CaseActivityEvent` | finalized activity ID / canonical snapshot hash / exact submitted time |

Both references use the exact transitioning `case_id`, nonblank distinct identities,
lowercase full hashes and naive capture times. Tuple order is not authority; a missing,
extra, duplicate, malformed, cross-case or unknown reference fails closed. Never assign
`Case.status` or a lifecycle projection directly, and never retain the historical direct
`WAITING_RECEIPT` write.

### Replay, conflict and whole-batch transaction rules

- Exact replay at the document and lifecycle seams must compare the persisted immutable
  activity payload, evidence links, canonical snapshot/hash, actor, event time and exact
  idempotency keys. It reuses the same durable activities and projection and creates no
  duplicate evidence, event, document, list or task side effect.
- A mixed/null finalized-activity tuple, changed actor/time/key/version/hash/payload,
  mismatched re-resolution, stale/mutable reconstruction, ambiguous candidate or any
  resolver/finalizer/lifecycle contradiction fails closed through the accepted
  `BusinessError` status/code. Do not choose a row, return partial evidence or remap a
  conflict to success.
- Validate and execute every selected case inside the one caller-owned transaction. One
  invalid case or one document/lifecycle conflict aborts and rolls back the whole batch,
  including case fields, generated document/list effects, apply-fee tasks, document
  activities and all lifecycle transitions. No partial commit, partial success count or
  per-case durable remainder is permitted.
- Commit exactly once, only after document finalization and lifecycle application succeed
  for every case. The adapter and delegated seams perform no internal commit/rollback.
- Preserve the existing meanings of `apply_exam_now` and `generate_list`; this task changes
  only the document-backed lifecycle authority and transaction boundary required above.

### Dependencies and High serialization

- Accepted catalog Task 55
  `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01` remains the first accepted owner of
  `backend/app/modules/cases/service.py`.
- D4-02 / supplemental row 02
  `FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01` must then reach independently
  accepted PASS before this row 17 task starts. Exact case-service order is therefore
  `accepted Task 55 → D4-02 / row 02 → Task 60 / row 17`.
- D4-05 `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` must independently PASS
  before this adapter consumes it. The accepted finalization seam, Delta-3 positive role
  allowlist, Task 20 lifecycle event and D4-04 exact external-submission evidence guard
  remain required immutable prerequisites.
- No other agent may edit or verify `backend/app/modules/cases/service.py` concurrently.
  Row 17 acquires that shared source only after row 02 releases it and releases it only
  after independent acceptance.
- Any pytest or shared-file verification that activates SQLite reports
  `READY_FOR_SERIAL_TEST`, waits for the controller's explicit `GRANT`, and runs under
  `GLOBAL_SQLITE_SERIAL_QUEUE` with maximum writer one.

### Explicit Delta-4 non-closure

- No second case entrypoint, filing-preparation/external-operation/receipt adapter, resolver,
  finalization seam, lifecycle rule or evidence-role change; no duplication of their
  validation inside case service.
- No API/router/schema/model/migration/seed/frontend, permission, response-envelope,
  status-code, fee, deadline, customer-decision, source-activation or release-gate change.
- No new source/test/task/artifact path, allowlist addition/removal, adjacent refactor,
  cleanup, broad test/lint run or rewrite of inherited task/evidence history.

### Unchanged implementation, TDD, evidence and gates

- The exact existing Allowed Files list remains the complete allowlist. The task-owned test
  remains `backend/tests/test_v8_batch_filing_lifecycle_adapter.py`.
- Under the latest-wins `P0-prereq-heavy-story` runbook, preserve task-scoped TDD: record a
  behavioral RED for the direct status/missing-evidence or partial-commit behavior, then make
  the smallest adapter/test change proving stable de-duplicated order, exact identities,
  snapshot/hash and evidence pair, actor/time/idempotency, exact replay, fail-closed conflict,
  whole-batch rollback and unchanged `apply_exam_now`/`generate_list` behavior.
- The existing targeted RED/GREEN and inherited regressions, scoped Ruff/format/diff
  commands, evidence path, dirty-baseline and baseline-subtracted diff requirements,
  independent zero-finding approval, repository task gate, atomic evidence validation and
  Done Definition remain binding. Evidence 1.1 is the final High acceptance authority for
  this not-yet-PASS task.
- This Ultra materialization performs no product/test edit, evidence initialization or
  rewrite, task gate, atomic evidence validation, broad verification or release execution;
  only the repository atomic task check is run.
