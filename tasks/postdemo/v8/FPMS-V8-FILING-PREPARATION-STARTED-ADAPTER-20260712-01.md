# FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `59`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `445`
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

Resolving/creating the filing preparation package records `FILING_PREPARATION_STARTED` exactly once.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task05:FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/summary.md, artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_workpkg_resolve_key_schema.py.
- `inherited` — `Task06:FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_filing_ensure_service.py.
- `inherited` — `Task07:FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_filing_resolve_api.py.
- `inherited` — `Task08:FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts.
- `inherited` — `Task09:FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts.

- Approved source dependency cell (verbatim): preparation rule; Tasks05–09 regressions

### Shared ownership serialization

- `backend/app/modules/official_workflows/service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md`
- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/official_workflows/api.py`
- `backend/tests/test_v8_filing_preparation_started_adapter.py`
- `artifacts/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_filing_preparation_started_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_filing_preparation_started_adapter.py tests/test_addgap_workpkg_resolve_key_schema.py tests/test_addgap_filing_ensure_service.py tests/test_addgap_filing_resolve_api.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts src/tests/addgap-filing-case-entry.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py`
- `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_preparation_started_adapter.py tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, Task 59 lines 227–246.
- Supplemental authority: batch row `16 / M4-D / H4-2` in `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work and evidence are `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact closure, dependencies, allowlist, serialization and verification below; all other inherited bytes remain history.

### Exact actor, snapshot, replay and transaction contract

- Close only the existing filing-preparation adapter that ensures the package and records `FILING_PREPARATION_STARTED` exactly once.
- The existing API injects and propagates exact `current_user.id`; the service requires nonblank `actor_id`.
- A new package writes `created_by=actor_id` and `updated_by=actor_id`. An existing package must already have a stable nonblank creator or fail `409`; never infer the current user as its historical creator.
- The package snapshot has exactly `case_id`, `id`, `package_kind`, `resolve_key`; its canonical JSON hash is the `FILING_WORK_PACKAGE` / `OfficialWorkPackage` evidence hash.
- Activity payload is exactly `{"evidence_schema":"FPMS_FILING_PREPARATION_EVIDENCE_V1","source_snapshot":{"case_id":"<package.case_id>","id":"<package.id>","package_kind":"<package.package_kind>","resolve_key":"<package.resolve_key>"},"source_snapshot_hash":"sha256:<64-lower-hex>"}`.
- Serialize both nested snapshot and full payload as UTF-8, sorted-key, compact JSON with no ASCII escaping.
- `captured_at`, `effective_at` and `occurred_at` are exact package `created_at`; idempotency key is exact `filing-preparation-started:<package.id>`.
- Exact replay compares persisted payload and evidence bytes; it never reconstructs truth from a later mutable package.
- Ensure, refresh and event write stay in the caller transaction with no internal commit or rollback. Fresh execution and exact replay return the same package; changed provenance fails `409`.

### Dependencies and shared ownership

- `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` (`D4-05`) must have independently accepted PASS evidence before High starts this row.
- Official-workflow shared execution is strict: row 16 → row 18 → row 19. Each predecessor must be independently accepted and release ownership.
- Rows 16 and 18 alone add `backend/app/modules/official_workflows/api.py`; they never edit or verify that shared API concurrently.

### Explicit non-closure

- Do not implement or change D4-05, final-submission evidence, external-submission state, receipt state, lifecycle rule semantics or another V8 row.
- Do not add or change a router, schema, migration, seed, endpoint shape or UI; current-user injection uses the existing API seam.
- Do not refactor adjacent official-workflow behavior or alter inherited Tasks 05–09 regression inputs.

### TDD, verification and Evidence 1.1

- Initialize through `./scripts/evidence_init.sh FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01 --task-file tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md` with every exact allowlist path before product/test edits.
- RED first through the public adapter/API seam must prove missing actor propagation, exact creator rules, snapshot/hash/payload/timestamps/idempotency, exact replay, `409` provenance rejection and caller-owned rollback behavior.
- GREEN is the smallest allowlisted implementation; run the inherited task-local pytest, Tasks 05–09 targeted regressions, scoped Ruff/diff checks and SQLite-writing verification serially.
- PASS requires latest required-result/log validation, scoped baseline-subtracted diff, dirty-baseline artifacts when applicable, independent approved zero-finding review, `./scripts/task_validate.sh`, and `scripts/atomic_evidence_validate.py` through the shared Evidence 1.1 consumer.
