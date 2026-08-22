# FPMS-V8-DE-REVIEW-API-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `51`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `437`
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

One POST approve/reject endpoint using `Doc.Edit`; 200 idempotent and 400/401/403/404/409/422 semantics with maker/reviewer separation.

## Explicit Non-Closure

No second endpoint, router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
- `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): review service, attachment adapter; serialized after attachment API

### Shared ownership serialization

- `backend/app/modules/documents/api.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-API-20260712-01.md`
- `backend/app/modules/documents/evidence_review_schemas.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_v8_document_evidence_review_api.py`
- `artifacts/FPMS-V8-DE-REVIEW-API-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_review_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_review_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_review_schemas.py app/modules/documents/api.py tests/test_v8_document_evidence_review_api.py && .venv/bin/ruff format app/modules/documents/evidence_review_schemas.py app/modules/documents/api.py tests/test_v8_document_evidence_review_api.py && .venv/bin/ruff check app/modules/documents/evidence_review_schemas.py app/modules/documents/api.py tests/test_v8_document_evidence_review_api.py`
- `git diff --check -- backend/app/modules/documents/evidence_review_schemas.py backend/app/modules/documents/api.py backend/tests/test_v8_document_evidence_review_api.py tasks/postdemo/v8/FPMS-V8-DE-REVIEW-API-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-API-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-REVIEW-API-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-REVIEW-API-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-API-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

- Latest-wins authority is `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 444–457. Delta-4 selects `chosen_runbook: P0-prereq-heavy-story`; the historical runbook line above remains unchanged and is superseded only for this execution.
- Task 51 owns exactly `POST /api/v1/documents/evidence-versions/{evidence_version_id}/review` with function parameter `_perm: None = Depends(require_perm("Doc.Edit"))`.
- The strict body field order is exactly `case_id`, `decision`, `reviewed_at`, `idempotency_key`; `decision` is exactly `APPROVE | REJECT`, `reviewed_at` is naive, the evidence-version ID is path-only, and unknown, extra or missing fields return 422.
- The reviewer is the server-owned current user. No client body or other input may supply or replace that actor; maker/reviewer separation remains in the service.
- Delegate exactly once to `review_evidence_version()` and return its direct result with no invented envelope. Fresh success and exact replay return 200.
- The outer adapter commits once on fresh or replay success and rolls back once on every service error.
- Exact errors are 400 for invalid input or path/case mismatch, 404 for missing case or evidence version, and 409 for state, review, idempotency or self-review conflict, plus 401, 403 and 422. No 201 or 204 is allowed.
- This task depends on Task 50, `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`, reaching independently accepted PASS. Shared `backend/app/modules/documents/api.py` ownership is serialized in exact order Task 50 → Task 51; they must not execute concurrently.
- This materialization performs no router, service or product implementation and does not broaden the task allowlist or closure slice.
- The existing task-owned RED/GREEN, targeted checks, serialized SQLite verification, evidence artifacts, independent review, task gate, atomic validation and Done Definition remain unchanged.
