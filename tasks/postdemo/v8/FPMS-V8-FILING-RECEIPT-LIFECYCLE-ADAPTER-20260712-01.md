# FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `66`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `452`
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

Valid filing receipt links to final submission and records receipt lifecycle event in the same transaction.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task14:FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_receipt_same_case_gate.py.
- `inherited` — `Task15:FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_receipt_source_gate.py.
- `inherited` — `Task16:FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/summary.md, artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_receipt_history_scan.py.

- Approved source dependency cell (verbatim): filing receipt rule; Tasks14–16 ownership tests

### Shared ownership serialization

- `backend/app/modules/official_workflows/service.py` order key `5`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_filing_receipt_lifecycle_adapter.py`
- `artifacts/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_filing_receipt_lifecycle_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_filing_receipt_lifecycle_adapter.py tests/test_addgap_receipt_same_case_gate.py tests/test_addgap_oa_receipt_source_gate.py tests/test_addgap_receipt_history_scan.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_filing_receipt_lifecycle_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_filing_receipt_lifecycle_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_filing_receipt_lifecycle_adapter.py`
- `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_receipt_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, Task 66 lines 291–307 and lifecycle evidence matrix lines 102–126.
- Supplemental authority: row `19 / M4-E / H4-2` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work and evidence remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact closure, dependencies, serialization and fail-closed behavior below; every other inherited byte and the exact Allowed Files list remain binding.

### Exact archived-receipt acceptance, evidence and activity

- Close only the existing filing-receipt adapter for one exact `FILING_PREP` package and its persisted receipt; do not create a second entrypoint.
- A fresh lifecycle advance requires `archive_status=ARCHIVED`, a non-null persisted receipt attachment owned by the same case, and a non-null naive `received_at`. A `PENDING` receipt alone never advances lifecycle.
- Revalidate the package, receipt and attachment linkage in the caller transaction. The attachment bytes must exist and their canonical persisted content hash must match; never select a cross-case, historical, missing or ambiguous row.
- Resolve the package through D4-05 `resolve_filing_final_evidence()` and require the exact current reviewed final version plus its exact persisted finalized external-submission activity; missing, multiple, mutable or mismatched evidence fails closed.
- Call `apply_lifecycle_event(FILING_RECEIPT_ARCHIVED)` with exactly two same-case `EvidenceReference` values and no extra value:
  1. `FINAL_SUBMISSION_VERSION / DocumentEvidenceVersion / evidence_version_id / content_hash / reviewed_at`;
  2. `VALID_FILING_RECEIPT / OfficialWorkPackageReceipt / receipt.id / receipt_attachment_content_hash / received_at`.
- The receipt evidence object identity is exact `receipt.id`, not the attachment ID; its hash is the validated attachment-content hash, while the final-version reference uses the resolver's exact version identity and hash.
- The required finalized activity is the D4-05-validated `DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED` activity and evidence link; do not reconstruct it from mutable version/package state or accept a nullable/mismatched activity identity/hash.
- Lifecycle idempotency is exact `filing-receipt-archived:<receipt.id>`. `effective_at`, `occurred_at` and receipt evidence `captured_at` are exact `received_at`; actor is the server-owned current user.

### Replay, failure and transaction

- Exact replay must match the same package, receipt identity, attachment linkage/hash, final-version identity/hash, finalized activity/link, actor, `received_at`, evidence tuple and idempotency key; it reuses the durable lifecycle event/projection and creates no duplicate activity or evidence.
- Any changed identity, hash, link, actor, time, evidence, archive state or mixed replay state fails closed through the accepted resolver/adapter/lifecycle error surface; never choose a fallback or remap conflict to success.
- Receipt creation, attachment evidence flags, lifecycle event/evidence and projection share one caller-owned transaction. Remove internal commit/refresh from this path; commit once only after the whole operation succeeds.
- Any validation or lifecycle failure rolls back the whole operation and leaves no partial receipt, attachment-flag, activity, evidence or direct status/projection write.

### Dependencies, serialization and non-closure

- D4-05 `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` and the inherited `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01` rule must each have independently accepted PASS evidence before this row starts.
- Official-workflow shared ownership is strict row 16 → row 18 → row 19. Each predecessor must be independently accepted and release ownership before this task edits or verifies the shared service.
- Keep the existing Allowed Files list unchanged. Row 19 adds no API path; only rows 16 and 18 own the existing `backend/app/modules/official_workflows/api.py` addition.
- OA receipt behavior remains explicit non-closure. Keep inherited Tasks 14–16 regressions green; add no OA behavior, router, schema, model, migration, seed, endpoint, UI or adjacent refactor.
- Existing RED/GREEN, targeted regression, Ruff/format/diff, SQLite serialization, Evidence 1.1 initialization/finalization, independent review, repository task gate, atomic evidence validation and Done Definition remain unchanged for later High execution.
- This Ultra materialization performs no product/test edit or evidence initialization and runs only the atomic task-file check.
