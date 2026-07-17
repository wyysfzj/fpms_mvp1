# FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `65`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- Source catalog line: `451`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Existing filing entrypoint calls `finalize_external_submission()` and records the filing submission lifecycle event in the same transaction; it does not duplicate evidence validation.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
- `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` — direct prerequisite;
  the adapter must call `finalize_external_submission()` and must not duplicate or bypass
  the seam's role-allowlist logic.
- `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`
- `FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): filing policy, finalize-external-submission seam, external-submission rule

### Shared ownership serialization

- `backend/app/modules/official_workflows/service.py` order key `4`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md`
- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/official_workflows/api.py`
- `backend/tests/test_v8_filing_external_submission_adapter.py`
- `artifacts/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- The filing adapter must delegate external-submission validation to
  `finalize_external_submission()`; it must not reproduce the role allowlist locally.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_filing_external_submission_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_filing_external_submission_adapter.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_filing_external_submission_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_filing_external_submission_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_filing_external_submission_adapter.py`
- `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_external_submission_adapter.py tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
- Evidence validation (single lane): `python3 scripts/atomic_evidence_validate.py FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- Any declared-peer run must append exactly one
  `--manifest <COMMON-EXECUTION-BATCH-MANIFEST>` and one
  `--concurrent-task <PEER-TASK-ID>` for every declared peer; that common manifest must
  list this task and every peer per the delta-3 G2 mandatory execution rule.

## Evidence Path

- `artifacts/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 247–290, with Task 65 behavior at lines 263–273.
- Supplemental authority: row `18 / M4-E / H4-2` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work and evidence remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact closure, dependencies, allowlist and serialization below; every other inherited byte remains history.

### Exact Task 65 external-submission closure

- Only normalized operation code `EXTERNAL_SUBMISSION_RECORDED` enters this path; every other existing checklist operation keeps its current semantics.
- Resolve the package by exact identity through D4-05 `resolve_filing_final_evidence()`; before fresh finalization require both nullable resolver activity fields to be `None`.
- The existing API propagates the server-owned current user as the nonblank actor. Never accept or infer a client, stored-evidence, fallback or system actor.
- Call `finalize_external_submission()` exactly once with `occurred_at` as the submission time and adapter base key exact `filing-external:<package_id>:<occurred_at.isoformat()>`.
- The document event key is exact `document-external-submission:filing-external:<package_id>:<occurred_at.isoformat()>`; the lifecycle event key is exact `filing-external-lifecycle:<package_id>:<occurred_at.isoformat()>`.
- Re-resolve the same package and require the exact persisted finalized activity, then call `apply_lifecycle_event(FILING_EXTERNAL_SUBMISSION_RECORDED)` once with the same actor/time and the exact two evidence refs below.
- Never duplicate resolver role/review/current/hash validation and never assign `Case.status` or a lifecycle projection directly.

### Canonical evidence snapshot and hash

- The finalized activity payload remains exactly `{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<occurred_at.isoformat()>"}`.
- Its canonical activity snapshot has exactly the accepted keys and values:

```json
{"activity_id":"<activity.id>","activity_type":"DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED","actor_id":"<activity.actor_id>","case_id":"<case_id>","confirmation_status":"CONFIRMED","effective_at":"<occurred_at.isoformat()>","evidence":[{"captured_at":"<occurred_at.isoformat()>","content_hash":"<version.content_hash>","evidence_kind":"DOCUMENT_EVIDENCE_VERSION","object_id":"<version.id>","object_type":"DocumentEvidenceVersion"}],"idempotency_key":"document-external-submission:filing-external:<package_id>:<occurred_at.isoformat()>","lane":"DOCUMENT","occurred_at":"<occurred_at.isoformat()>","payload":{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<occurred_at.isoformat()>"},"reviewer_id":"<version.reviewer_id>"}
```

- Serialize as UTF-8 sorted-key compact JSON with no ASCII escaping; `submission_activity_hash` is exact `sha256:<64-lower-hex>` over those bytes. No mutable version field, database order or created/updated timestamp participates.
- Lifecycle evidence is exactly one `FINAL_SUBMISSION_VERSION / DocumentEvidenceVersion / version.id / version.content_hash / reviewed_at` plus one `MANUAL_EXTERNAL_SUBMISSION_RECORD / CaseActivityEvent / activity.id / submission_activity_hash / occurred_at`, both for the transitioning case.

### Durable replay, conflict and transaction

- Exact replay compares persisted immutable payload, evidence link, canonical snapshot/hash, actor, submission time and all exact idempotency keys; it reuses durable activities/projection and creates no duplicate event or evidence.
- Mixed/null activity state, changed actor/time/key/version/hash/payload, mismatched re-resolution, ambiguous evidence or mutable reconstruction fails closed through the accepted resolver/finalizer/lifecycle `BusinessError`; never choose a row or remap conflict to success.
- All writes remain in the caller-owned transaction. Commit exactly once only after document finalization and lifecycle application both succeed; delegated services perform no internal commit or rollback, and failure leaves no partial document or lifecycle state.

### Dependencies, serialization and non-closure

- D4-05 `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` must have independently accepted PASS evidence before this row starts.
- Official-workflow shared service/API ownership is strict row 16 → row 18 → row 19; each predecessor releases ownership only after independent acceptance, and no shared edit or verification runs concurrently.
- The sole allowlist addition is `backend/app/modules/official_workflows/api.py` for server-owned actor propagation. Add no router, schema, model, migration, seed, endpoint-shape, UI or other source path.
- Do not implement D4-05, alter another checklist operation, lifecycle rule, role allowlist, receipt/batch adapter or adjacent official-workflow behavior.
- This Ultra materialization performs no product/test edit or evidence initialization and runs only the repository atomic task check.
