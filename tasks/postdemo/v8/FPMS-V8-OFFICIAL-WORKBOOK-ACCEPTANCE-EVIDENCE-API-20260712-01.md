# FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `220`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `728`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-PAYMENT-WORKBOOK[GLOBAL]`

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

One POST acceptance-evidence action using `Fee.Edit`; 200 idempotent and 400/401/403/404/409/422 semantics.

## Explicit Non-Closure

No second endpoint, router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-PAYMENT-WORKBOOK:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): acceptance service

### Shared ownership serialization

- `backend/app/modules/annuity/api.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01.md`
- `backend/app/modules/annuity/schemas.py`
- `backend/app/modules/annuity/api.py`
- `backend/tests/test_v8_official_workbook_acceptance_api.py`
- `artifacts/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_official_workbook_acceptance_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_official_workbook_acceptance_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/schemas.py app/modules/annuity/api.py tests/test_v8_official_workbook_acceptance_api.py && .venv/bin/ruff format app/modules/annuity/schemas.py app/modules/annuity/api.py tests/test_v8_official_workbook_acceptance_api.py && .venv/bin/ruff check app/modules/annuity/schemas.py app/modules/annuity/api.py tests/test_v8_official_workbook_acceptance_api.py`
- `git diff --check -- backend/app/modules/annuity/schemas.py backend/app/modules/annuity/api.py backend/tests/test_v8_official_workbook_acceptance_api.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01` pass. Only then may this task be reported PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

## Frozen API Contract (2026-08-13)

- Expose exactly one strict
  `POST /pay-lists/{pay_list_id}/official-workbook/acceptance` action under `Fee.Edit`.
  The body contains only `artifact_id`, `evidence_ref`, lowercase `evidence_sha256`, naive
  `accepted_at` and `idempotency_key`; actor and runtime profile come from trusted server
  dependencies/configuration.
- Call only `record_official_workbook_acceptance(...)` with the caller-owned transaction. A new
  `CREATED` result returns `201`; an exact `REUSED` result returns `200`. The response preserves the
  service result as distinct generated/accepted/paid/ticket facts and adds no rule, payment or
  ticket inference.
- Commit exactly once after a successful service result. Any service, response-validation or
  outer-commit exception rolls back exactly once. Preserve service-owned `400/404/409`, framework
  `401/403/422` and the standard error envelope without endpoint pre-reads or rule duplication.
