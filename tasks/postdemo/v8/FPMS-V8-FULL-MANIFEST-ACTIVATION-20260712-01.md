# FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `199`
Executor role: Team Lead / default

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `698`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-GRANT-EVIDENCE-SOURCE[GLOBAL], DG-GRANT-MANUAL-REVIEW[GLOBAL], DG-FEE-APPLICATION-DRAFT[GLOBAL], DG-FEE-GRANT-YEAR-DRAFT[GLOBAL], DG-FEE-FUTURE-ANNUITY[GLOBAL], DG-PAYMENT-WORKBOOK[GLOBAL], DG-SERVICE-RATE-VERSION[GLOBAL], DG-LEGACY-FORM-CLASS[ALL-22]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails on missing evidence or coverage.
- GREEN expectation: Exact audit/E2E/gate commands pass and any failure becomes a new task.

## Exact Closure Slice

Materialize the full-program manifest only when all eight gate codes have sufficient applicable persisted confirmation coverage, including a positive or negative value for every legacy-form scope; include every catalog task exactly once, require each per-form classification task to execute its recorded branch, reuse existing foundation/lane evidence and pass the catalog coverage gate. It does not implement or approve any product task.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-GRANT-MANUAL-REVIEW:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-FEE-APPLICATION-DRAFT:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-FEE-FUTURE-ANNUITY:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-PAYMENT-WORKBOOK:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-SERVICE-RATE-VERSION:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-LEGACY-FORM-CLASS:ALL-22`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `ALL_APPLICABLE_GATE_COVERAGE`: All eight gate codes and all 22 form scopes have sufficient persisted coverage.

- Approved source dependency cell (verbatim): complete applicable gate coverage; decision-gate read service; catalog coverage gate

### Shared ownership serialization

- `FULL_MANIFEST_OWNERSHIP` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-MITIGATION-20260712-01.md`
- `backend/tests/test_v8_full_manifest_activation_contract.py`
- `artifacts/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_full_manifest_activation_contract.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_full_manifest_activation_contract.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_full_manifest_activation_contract.py && .venv/bin/ruff format tests/test_v8_full_manifest_activation_contract.py && .venv/bin/ruff check tests/test_v8_full_manifest_activation_contract.py`
- `git diff --check -- tasks/batches/FPMS-POSTDEMO-V8-MITIGATION-20260712-01.md backend/tests/test_v8_full_manifest_activation_contract.py artifacts/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01/** tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01` pass. Only then may this task be reported PASS.
