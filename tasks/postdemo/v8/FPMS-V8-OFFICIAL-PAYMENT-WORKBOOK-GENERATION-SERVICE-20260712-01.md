# FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01

Status: IMPLEMENTED / AWAITING INDEPENDENT REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `215`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `723`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-PAYMENT-WORKBOOK[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Call the verified adapter, persist one generated official artifact/hash/template version and append one FEE activity atomically; generation does not imply acceptance/payment/ticket.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-PAYMENT-WORKBOOK:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): workbook adapter, export artifact carrier

### Shared ownership serialization

- `backend/app/modules/annuity/service.py` order key `11`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01.md`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_official_payment_workbook_generation_service.py`
- `artifacts/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_official_payment_workbook_generation_service.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_official_payment_workbook_generation_service.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_official_payment_workbook_generation_service.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_official_payment_workbook_generation_service.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_official_payment_workbook_generation_service.py`
- `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_official_payment_workbook_generation_service.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01` pass. Only then may this task be reported PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

## C3 Lean Current Verification

- RED: the exact focused test failed `4` tests because the row215 generation service and
  resolver/adapter bindings were absent.
- GREEN before independent review: the exact focused test passed `5` tests; the focused dependency
  regression tranche passed `42` tests. Independent review then required the successor corrections
  frozen below; final counts must be recorded from the amended candidate.
- The service resolves the current workbook input for the supplied runtime profile before any
  product write. Non-test runtime accepts only a resolved `PRODUCTION` input; missing or
  `TEST_ONLY` production input returns `409` with no artifact or managed output.
- One `OFFICIAL_XLSM` artifact with server-computed hash and resolved template version is added to
  the caller-owned transaction. Its FEE activity records the exact input-version lineage and
  explicit `generated`/not-accepted/not-paid/not-ticket-verified boundary. Adapter or activity
  failure compensates the newly written managed file.
- Scoped Ruff and whitespace checks are required again on the exact commit before independent
  review. No endpoint, UI, schema, payment/acceptance mutation or production input was added.
- Amended candidate GREEN: the exact focused test passes `10` tests. The immediately preceding
  generation/adapter/input-governance/internal-export tranche passed `45` tests before the final
  focused conflict regression was added; it is historical support, not a claim over the amended
  bytes. These are implementation evidence only until independent review accepts the closure.

## Frozen Generation Successor Contract (2026-08-13)

- Production generation requires both the resolved current `PRODUCTION` workbook-input version and
  the current effective `DG-PAYMENT-WORKBOOK:GLOBAL` decision. The gate source reference is the
  resolved upload-proof managed path, its source version is the resolved template version, and its
  canonical decision value binds the exact workbook-input version ID, scope, template version/hash,
  upload-proof hash, structure-snapshot hash and effective interval. Missing, revoked, future,
  mismatched or corrupt authority is `PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED` / `409` / no write.
  The isolated `test` runtime continues to use only an explicitly resolved `TEST_ONLY` input and
  cannot activate or stand in for production authority.
- This row owns exactly one FEE activity. Therefore its atomic closure accepts only a PayList whose
  persisted GovPayment rows resolve to exactly one case. Empty or multi-case input is `409` with no
  artifact or managed output; a later separately contracted owner may define multi-case lineage.
- The durable FEE activity is linked to the artifact evidence and carries the resolved input-version
  ID, template version, template source hash, generated output hash and canonical requested-row
  snapshot hash. Generated status remains distinct from official acceptance, payment and ticket
  verification.
- The `(pay_list_id, idempotency_key)` identity supports exact replay only. Replay revalidates the
  current gate/input binding, artifact tuple, managed bytes/hash and the exact lifecycle activity
  command, then returns the same artifact, bytes and activity identity without rerendering or a new
  write. Any differing actor, time, rows, input version/hash, artifact/activity tuple or managed
  bytes is `OFFICIAL_PAYMENT_WORKBOOK_IDEMPOTENCY_CONFLICT` / `409`. A concurrent unique-write loss
  maps to the same conflict family; caller-owned commit/rollback remains unchanged.
