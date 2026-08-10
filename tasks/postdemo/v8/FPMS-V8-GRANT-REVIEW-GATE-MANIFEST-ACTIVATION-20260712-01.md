# FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
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

## Re-frozen authority and activation boundary

- Scheme A customer source:
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`.
- Scheme A SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`.
- Policy status: `APPROVED_POLICY / CONFIG_REQUIRED`.
- Product development: `ELIGIBLE`.
- Runtime source configuration: `REQUIRED / NOT PROVIDED BY THIS MANIFEST`.
- Runtime role configuration: `REQUIRED / NOT PROVIDED BY THIS MANIFEST`.

This activation creates no source record, role binding, default or seed. Missing, stale,
unreviewed, revoked, inactive, future, expired, scope-mismatched, hash-mismatched or ambiguous
source or role authority remains `409 / NO WRITE / NO LEGAL-STATE CHANGE`. A candidate remains
unverified until the exact accepted review and dispatch chain runs; manifest membership never
proves grant or authorizes a direct case-status write.

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

The exact ordered membership is:

1. `FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01`;
2. `FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01`;
3. `FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01`;
4. `FPMS-V8-PATENT-REGISTER-EVIDENCE-ADAPTER-20260712-01`;
5. `FPMS-V8-GRANT-EVIDENCE-ACCEPTED-DISPATCH-ADAPTER-20260712-01`;
6. `FPMS-V8-GRANT-EVIDENCE-REVIEW-API-20260712-01`;
7. `FPMS-V8-GRANT-EVIDENCE-REVIEW-FE-ADAPTER-20260712-01`;
8. `FPMS-V8-GRANT-EVIDENCE-REVIEW-UI-20260712-01`.

Execution order is activation, review service, announcement adapter, patent-register adapter,
accepted dispatch, review API, FE adapter, then UI. The two `evidence_policy.py` adapters are
serialized in that order; review service precedes accepted dispatch in
`grant_evidence_review_service.py`; review API follows the ingestion API in `documents/api.py`
and `grant_evidence_schemas.py`; the review FE adapter follows the accepted document-review FE
adapter in `documents.ts` and `documents.types.ts`. All manifest/shared-file and SQLite-writing
verification remains serialized.

## Explicit Non-Closure

No product fix, schema change, runtime source/role publication, default, seed or test-assertion
weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer
policy or unrelated cleanup. Do not edit the catalog, coverage ledger, adoption records, router,
schema or product code.

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

No artifact, source, test, task, manifest, catalog, coverage-ledger, adoption or shared ownership
file outside these exact three paths is authorized. Inherited inputs are read-only. Preserve the
initial dirty baseline, which is only untracked `backend/uv.lock`; do not stage, edit or absorb it.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_review_gate_manifest_contract.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_review_gate_manifest_contract.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_grant_review_gate_manifest_contract.py && .venv/bin/ruff format tests/test_v8_grant_review_gate_manifest_contract.py && .venv/bin/ruff check tests/test_v8_grant_review_gate_manifest_contract.py`
- `git diff --check -- tasks/postdemo/v8/FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01.md tasks/batches/FPMS-POSTDEMO-V8-GRANT-REVIEW-GATE-20260712-01.md backend/tests/test_v8_grant_review_gate_manifest_contract.py`

Do not run repo-wide tests, broad frontend/backend builds, broad Playwright, milestone verification
or release checks for this activation.

## Independent review boundary

This `PROTECTED` activation requires an independent High reviewer of the exact implementation
commit/range. The reviewer independently reruns the focused GREEN, scoped Ruff and exact diff
check, verifies the manifest's eight current task hashes and reports one final
`Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`. This implementer does not edit the coverage ledger
or adoption record and does not self-approve.

## Done Definition

The exact RED is preserved; the minimum three-path change creates one manifest containing this
activation plus exactly catalog ordinals 204-210 in dependency/shared-file order; the focused
GREEN, scoped Ruff and exact diff check pass; the `backend/uv.lock` baseline remains untouched;
runtime source and role configuration remain required/fail-closed; no source, role, permission,
default, seed, product behavior, ledger or adoption is changed; and an independent High reviewer
approves the exact implementation commit/range with zero findings. Only then may the story be
adopted by its separately owned current-adoption change.
