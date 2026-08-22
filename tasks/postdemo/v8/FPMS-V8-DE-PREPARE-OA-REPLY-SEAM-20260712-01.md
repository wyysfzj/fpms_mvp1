# FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `48`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- Source catalog line: `429`
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

Implement only `prepare_oa_reply(command, transaction)`: validate the same-case source OA notice/evidence and selected copyable/noncopyable attachment policy, then atomically create/reuse exactly one DRAFT OA_OUT evidence version and its unique OA reply package/link in the caller transaction. The newly prepared reply is not treated as independently reviewed; no HTTP, task close, external submission or lifecycle transition occurs.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` — direct prerequisite
  solely for serialized shared ownership of
  `backend/app/modules/documents/evidence_workflow_service.py`; it does not change OA
  business semantics.
- `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
- `FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): finalize-external-submission seam for shared-file serialization; OA copyable and noncopyable policy tasks

### Shared ownership serialization

- `backend/app/modules/documents/evidence_workflow_service.py` order key `3`: accepted
  `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01` →
  `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` → this task; project this
  order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md`
- `backend/app/modules/documents/evidence_workflow_service.py`
- `backend/tests/test_v8_prepare_oa_reply_seam.py`
- `artifacts/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_prepare_oa_reply_seam.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_prepare_oa_reply_seam.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py tests/test_v8_prepare_oa_reply_seam.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py tests/test_v8_prepare_oa_reply_seam.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py tests/test_v8_prepare_oa_reply_seam.py`
- `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/tests/test_v8_prepare_oa_reply_seam.py tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
- Evidence validation (single lane): `python3 scripts/atomic_evidence_validate.py FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- Any declared-peer run must append exactly one
  `--manifest <COMMON-EXECUTION-BATCH-MANIFEST>` and one
  `--concurrent-task <PEER-TASK-ID>` for every declared peer; that common manifest must
  list this task and every peer per the delta-3 G2 mandatory execution rule.

## Evidence Path

- `artifacts/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority and prerequisites

- Authority: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
  lines 423–441 and supplemental batch row `21 / M4-F / H4-1`.
- Risk is `HIGH`; this appendix is latest-wins only for the Delta-4 prerequisite, typed
  attachment, DRAFT closure, replay, conflict and transaction rules below.
- `chosen_runbook: P0-prereq-heavy-story` governs execution. Prior Delta overlays and all
  inherited task bytes remain history; the existing Allowed Files list is unchanged.
- Exact document order is accepted D4-06 → D4-07 → D4-08 → corrected row 20 / Task 72 →
  row 21 / Task 73. Each predecessor must reach independent accepted PASS before its
  consumer starts.
- D4-08 `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01` is the sole formal
  RAW-to-`OA_STRUCTURED_ATTACHMENT` promotion/derivation/link authority.
- Corrected Task 72 `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01` is the sole public
  typed manifest/version policy authority. Its rejected ORM-role shortcut remains history.
- The inherited noncopyable appendix policy and Delta-3 shared-service serialization
  prerequisites remain binding; this overlay adds no file or alternate policy seam.

### Exact DRAFT OA reply closure

- Task 73 changes only existing `prepare_oa_reply(command, transaction)`: validate the
  same-case source OA notice/evidence and selected attachment DTOs, then create or reuse
  exactly one `DRAFT` `OA_OUT` evidence version and its unique same-case OA reply
  package/link in the caller transaction.
- Every supplied attachment must carry typed version identity/hash and exact manifest
  identity/role/link. Never infer typed evidence from `DocAttachment.official_file_role`,
  filename, ORM role, latest row, database order or an ambiguous candidate.
- Every supplied version must be current `OA_STRUCTURED_ATTACHMENT`, independently
  `APPROVED`, same-case/package and exactly linked by its manifest.
- Cardinality is exact: one `OA_STATEMENT_WORD`; one `OA_MODIFIED_CLAIMS`; at most one
  `OA_AMENDMENT_COMPARISON`; zero-or-more `OA_OTHER_PROOF` and `OA_ADDITIONAL_FILE`.
- Duplicate evidence ID, duplicate manifest ID, cross-case/package identity, RAW or
  non-promoted evidence, hash/link/state/review mismatch, unknown role, missing singleton
  or excess optional singleton fails closed before any durable reply write.
- The prepared reply remains unreviewed `DRAFT`; preparation does not approve, finalize,
  externally submit, close a task or apply a lifecycle transition.

### Typed replay, conflict and transaction

- Exact replay resolves the same source notice, typed version/hash plus manifest/role/link
  set and the one persisted DRAFT `OA_OUT` version/package/link closure; it reuses those
  exact identities and creates no duplicate version, package, link, activity or side effect.
- A changed source or typed identity/hash/role/link/cardinality, stale or mutable lookup,
  missing/multiple persisted closure, non-DRAFT state, cross-case relation or replay
  contradiction fails closed through the accepted `BusinessError` status/code; never pick
  a candidate or remap conflict to success.
- The caller owns the single transaction. Validation, DRAFT version, package and link writes
  are all-or-nothing; the seam performs no internal commit/rollback and leaves no partial
  version, package, link or replay carrier after any failure.

### Materialization non-closure

- No external-submission, review, lifecycle, API/router/schema/model/migration/seed/UI, fee,
  deadline, permission, response-envelope or customer-decision behavior is implemented.
- No product/test/evidence artifact is edited or initialized; no allowlist or prior Delta
  overlay is rewritten. This materialization changes only Status and this EOF appendix.
- Only the repository atomic `check-task` runs now. Product TDD, targeted verification,
  Evidence 1.1, independent review and task gates remain deferred to High execution.
