# FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `171`
Executor role: Team Lead / default

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `665`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-GRANT-EVIDENCE-SOURCE[GLOBAL], DG-GRANT-MANUAL-REVIEW[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails on missing evidence or coverage.
- GREEN expectation: Exact audit/E2E/gate commands pass and any failure becomes a new task.

## Exact Closure Slice

Create the grant-review lane manifest containing this activation plus exactly seven review/adapter/API/FE/UI tasks.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
- `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-GRANT-MANUAL-REVIEW:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): both grant gates; source-lane tasks and grant lifecycle rules PASS; coverage gate

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-GRANT-REVIEW-GATE-20260712-01.md`
- `backend/tests/test_v8_grant_review_gate_manifest_contract.py`
- `artifacts/FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_review_gate_manifest_contract.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_review_gate_manifest_contract.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_grant_review_gate_manifest_contract.py && .venv/bin/ruff format tests/test_v8_grant_review_gate_manifest_contract.py && .venv/bin/ruff check tests/test_v8_grant_review_gate_manifest_contract.py`
- `git diff --check -- tasks/batches/FPMS-POSTDEMO-V8-GRANT-REVIEW-GATE-20260712-01.md backend/tests/test_v8_grant_review_gate_manifest_contract.py artifacts/FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01/** tasks/postdemo/v8/FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01` pass. Only then may this task be reported PASS.
