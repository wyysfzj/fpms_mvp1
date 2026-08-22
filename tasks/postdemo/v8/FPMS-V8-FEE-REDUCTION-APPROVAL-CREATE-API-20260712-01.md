# FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `95`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `518`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-API`

- RED expectation: Exact API test fails with route/shape/permission/status mismatch.
- GREEN expectation: Exact API test passes named 200/201/400/401/403/404/409/422 semantics and response envelope.

## Exact Closure Slice

POST one approval and return its identifier; permission `Fee.Edit`; 201 create/200 idempotent/400 wrong case/409 conflict.

## Explicit Non-Closure

No second endpoint, router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): approval service

### Shared ownership serialization

- `backend/app/modules/fees/api.py` order key `1`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/fee_reduction_approval_schemas.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01.md`
- `backend/app/modules/fees/fee_reduction_approval_schemas.py`
- `backend/app/modules/fees/api.py`
- `backend/tests/test_v8_fee_reduction_approval_create_api.py`
- `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_create_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_create_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_create_api.py && .venv/bin/ruff format app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_create_api.py && .venv/bin/ruff check app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_create_api.py`
- `git diff --check -- backend/app/modules/fees/fee_reduction_approval_schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_reduction_approval_create_api.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 458–472.
- Supplemental authority: row `22 / M4-F / H4-4` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work and evidence remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact HTTP contract, dependency, transaction and acceptance rules below; every other inherited byte and the existing allowlist remain unchanged history.

### Exact fee-reduction approval create HTTP contract

- Route is exact `POST /api/v1/fees/cases/{case_id}/reduction-approvals`; permission is exact `Fee.Edit` through the existing permission dependency.
- The strict request body has this exact field order: `case_id`, `scope_type`, `applicant_ids`, `eligibility_attributes_version`, `eligibility_attributes_json`, `reduction_ratio`, `fee_codes`, `fee_year_from`, `fee_year_to`, `effective_from`, `effective_to`, `source_evidence_version_id`, `expected_source_content_hash`, `confirmed_at`.
- Body `case_id` is intentionally retained. A path/body mismatch fails before service invocation with 400 `FEE_REDUCTION_APPROVAL_CASE_MISMATCH` and both IDs in details.
- The confirmed actor is the server-owned current user. Never accept, infer or substitute a client, stored-evidence, fallback or system actor.
- `confirmed_at` is the exact naive, client-stable value; do not replace it with a server clock or timezone conversion.
- Delegate exactly once to accepted `record_fee_reduction_approval()` and return direct `{"approval_id":"<service.approval_id>"}` with no invented response envelope.
- Service result `CREATED` maps to 201; `REUSED` maps to 200. Commit once on either success and roll back once on error.
- Preserve 401/403 permission semantics, 404 missing-resource semantics, service evidence-case mismatch as 409, every other accepted 409 conflict, and strict 422 validation for missing, extra or malformed input.
- There is no client idempotency field in the body, path, query or header contract. Do not invent one; reuse remains the accepted service's deterministic identity/result behavior.

### Dependency and non-closure

- `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01` must retain independently accepted PASS evidence before High starts this API task.
- Keep business validation, snapshot/evidence identity, reuse and conflict decisions inside that accepted service; do not duplicate or weaken them in the API/schema adapter.
- Keep the existing Allowed Files list exact. Do not add or rewire a router, add a model/migration/seed/endpoint, alter fee truth or customer policy, or absorb another V8 row.
- This Ultra materialization changes no API, schema, router, test or product file and initializes no evidence.

### Scoped TDD, evidence and gates

- After the prerequisite is accepted, initialize Evidence 1.1 through the repository `./scripts/evidence_init.sh` entrypoint with this task file and every exact existing allowlist path before product/test edits.
- RED first through the public HTTP seam must prove route/permission, strict body, server actor, path/body 400 details, no client idempotency input, direct response, CREATED 201/REUSED 200, error mapping and commit/rollback behavior.
- GREEN is the smallest allowlisted API/schema/test change; run only the inherited targeted pytest, scoped Ruff/format/diff checks and serialized SQLite-writing verification named above.
- PASS requires latest required results/logs, scoped baseline-subtracted diff, dirty-baseline artifacts when applicable, independent approved zero-finding review, `./scripts/task_validate.sh`, and `scripts/atomic_evidence_validate.py` through the shared Evidence 1.1 consumer.
- This contract-freeze turn runs only the repository atomic task check; it does not execute RED/GREEN, task/evidence gates, broad verification or release work.
