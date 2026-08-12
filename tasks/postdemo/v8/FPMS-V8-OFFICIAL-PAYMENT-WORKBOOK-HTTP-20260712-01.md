# FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `216`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `724`
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

One generation/download endpoint calling the generation service; unresolved gate is 409 and zero artifact/state change.

## Explicit Non-Closure

No second endpoint, router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-PAYMENT-WORKBOOK:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): generation service

### Shared ownership serialization

- `backend/app/modules/annuity/api.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01.md`
- `backend/app/modules/annuity/api.py`
- `backend/tests/test_v8_official_payment_workbook_api.py`
- `artifacts/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_official_payment_workbook_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_official_payment_workbook_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/api.py tests/test_v8_official_payment_workbook_api.py && .venv/bin/ruff format app/modules/annuity/api.py tests/test_v8_official_payment_workbook_api.py && .venv/bin/ruff check app/modules/annuity/api.py tests/test_v8_official_payment_workbook_api.py`
- `git diff --check -- backend/app/modules/annuity/api.py backend/tests/test_v8_official_payment_workbook_api.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01` pass. Only then may this task be reported PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

## Frozen HTTP Contract (2026-08-13)

- Expose exactly one strict `POST /pay-lists/{pay_list_id}/official-workbook` download action under
  `PayList.Export`. The request contains `idempotency_key` and one-to-500 exact official workbook
  rows; extra fields fail `422`. Actor, naive server time and runtime profile come only from trusted
  dependencies/configuration. The adapter performs no gate, input, artifact or payment pre-read.
- Call only `generate_official_payment_workbook(...)`. A newly `CREATED` result returns `201`; an
  exact `REUSED` result returns `200`. Both return the service bytes and content type as an
  attachment, with server result headers for artifact ID, output hash, template version/source hash,
  workbook-input version and disposition. Generated does not mean accepted, paid or ticket-verified.
- The endpoint commits exactly once after a successful service result. On a service or outer-commit
  exception it rolls back exactly once. If and only if a `CREATED` result exists, commit failure also
  compensates that newly managed file; a `REUSED` result's durable file is never deleted. A
  compensation failure remains the service-owned 500 error. Service-owned 400/404/409 errors,
  framework 401/403/422 and standard error envelopes are preserved.
