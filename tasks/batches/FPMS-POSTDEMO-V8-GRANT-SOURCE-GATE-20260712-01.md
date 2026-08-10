# FPMS Post-demo V8 Grant-source Gate Lane Manifest

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Manifest phase: `lane`
Task count: 5
Runbook: `P0-prereq-heavy-story`
Activation task: `FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01`
Gate requirement: `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`

## Authority and activation boundary

- Policy status: `APPROVED_POLICY / CONFIG_REQUIRED`.
- Accepted customer-decision commit:
  `e5a41c8d07f11d1b0dec68891ef7bef53312f883`.
- Accepted current-owner adoption commit:
  `72877386974cd57c720b7c622e6b00ca49c03d7d`.
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`.
- Customer-source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Product development: ELIGIBLE.
- Runtime source configuration: REQUIRED / NOT PROVIDED BY THIS MANIFEST.

This manifest activates only the exact development lane below. It does not publish or confirm a
runtime source record. No concrete CNIPA source is selected, defaulted or seeded by this manifest.
At runtime, missing, stale or unreviewed source configuration remains
`409 / NO WRITE / NO LEGAL-STATE CHANGE`. Archive every candidate as unverified; ingestion or read
availability never proves a grant, changes patent legal state, or enters a patent in force.

Every task retains its own exact owner, allowlist, RED/GREEN evidence and independent protected
review. The activation task cannot approve itself or any child. Product execution begins only
after this activation receives independent approval and each child's named prerequisites pass.
No task in this manifest changes a schema, catalog, coverage ledger, source registry, customer
decision, production seed, or release state.

## Execution waves and shared ownership

1. Wave G0: independently review and accept the activation task only.
2. Wave G1: execute the ingestion service.
3. Wave G2: execute the ingestion API and candidate read service under separate owners.
4. Wave G3: execute the candidate list API after both Wave G2 tasks pass.

Shared files remain serialized even when dependency waves otherwise permit concurrency:

- `grant_evidence_ingestion_service.py`: ingestion service before candidate read service.
- `documents/api.py` and `grant_evidence_schemas.py`: ingestion API before candidate list API.
- All SQLite-writing verification remains serialized through the repository queue.
- Independent review is required per protected task and binds that task's exact patch/evidence.

## Task Entries

## 001. FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01.md`
- Owner role: Team Lead / default
- Profile: `TC-QA`
- Exact closure: Create only this five-row grant-source lane manifest containing the activation
  plus the four candidate ingestion/read service/API tasks, while preserving unverified archive
  status and zero legal-state effect.
- Non-closure: No product code, schema, catalog or coverage-ledger change; no source publication,
  customer-policy invention, test weakening, second lane, or release action.
- Canonical dependencies:
  - `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
  - `FPMS-V8-DE-CONTRACTS-20260712-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
  - `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01.md`
  - `tasks/batches/FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md`
  - `backend/tests/test_v8_grant_source_gate_manifest_contract.py`
  - `artifacts/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_source_gate_manifest_contract.py`
  - `cd backend && .venv/bin/ruff check tests/test_v8_grant_source_gate_manifest_contract.py`
  - `git diff --check -- tasks/batches/FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md backend/tests/test_v8_grant_source_gate_manifest_contract.py artifacts/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01/** tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01.md`
- Acceptance: exact RED/GREEN, scope/evidence checks and one independent High zero-finding review.

## 002. FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Ingest one announcement/register candidate only from the confirmed
  controlled-source contract, archive it unverified and never change legal state.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the
  row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
  - `backend/app/modules/documents/grant_evidence_ingestion_service.py`
  - `backend/tests/test_v8_grant_evidence_ingestion_service.py`
  - `artifacts/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_ingestion_service.py`
  - `cd backend && .venv/bin/ruff check app/modules/documents/grant_evidence_ingestion_service.py tests/test_v8_grant_evidence_ingestion_service.py`
  - `git diff --check -- backend/app/modules/documents/grant_evidence_ingestion_service.py backend/tests/test_v8_grant_evidence_ingestion_service.py tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
- Runtime gate: source configuration that is absent, revoked, future-dated, stale, unreviewed or
  scope-mismatched returns 409 with no write and no legal-state change.
- Acceptance: targeted TDD, scoped checks, exact allowlist evidence and independent High review.

## 003. FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: One POST candidate endpoint using `Doc.Edit`; return 201 candidate, 409 unresolved gate/source conflict and no legal-state change.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01`
  - `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md`
  - `backend/app/modules/documents/grant_evidence_schemas.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_grant_evidence_ingestion_api.py`
  - `artifacts/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_ingestion_api.py`
  - `cd backend && .venv/bin/ruff check app/modules/documents/grant_evidence_schemas.py app/modules/documents/api.py tests/test_v8_grant_evidence_ingestion_api.py`
  - `git diff --check -- backend/app/modules/documents/grant_evidence_schemas.py backend/app/modules/documents/api.py backend/tests/test_v8_grant_evidence_ingestion_api.py tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md`
- Runtime gate: source configuration that is absent, revoked, future-dated, stale, unreviewed or
  scope-mismatched returns 409 with no write and no legal-state change.
- Acceptance: targeted TDD, scoped checks, exact allowlist evidence and independent High review.

## 004. FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Read persisted candidates for one document with source/version/proposer/reviewer/
  review/conflict data; no legal-state inference or write.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the
  row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01`
  - `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md`
  - `backend/app/modules/documents/grant_evidence_ingestion_service.py`
  - `backend/tests/test_v8_grant_evidence_candidate_read_service.py`
  - `artifacts/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_candidate_read_service.py`
  - `cd backend && .venv/bin/ruff check app/modules/documents/grant_evidence_ingestion_service.py tests/test_v8_grant_evidence_candidate_read_service.py`
  - `git diff --check -- backend/app/modules/documents/grant_evidence_ingestion_service.py backend/tests/test_v8_grant_evidence_candidate_read_service.py tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md`
- Runtime gate: source configuration that is absent, revoked, future-dated, stale, unreviewed or
  scope-mismatched returns 409 with no write and no legal-state change.
- Acceptance: targeted TDD, scoped checks, exact allowlist evidence and independent High review.

## 005. FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: One bodyless GET `/documents/{document_id}/grant-evidence-candidates` using
  `Doc.Read`; 200/401/403/404/409/422 and no request body.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01`
  - `FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01`
  - `FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md`
  - `backend/app/modules/documents/grant_evidence_schemas.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_grant_evidence_candidate_list_api.py`
  - `artifacts/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_candidate_list_api.py`
  - `cd backend && .venv/bin/ruff check app/modules/documents/grant_evidence_schemas.py app/modules/documents/api.py tests/test_v8_grant_evidence_candidate_list_api.py`
  - `git diff --check -- backend/app/modules/documents/grant_evidence_schemas.py backend/app/modules/documents/api.py backend/tests/test_v8_grant_evidence_candidate_list_api.py tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md`
- Runtime gate: source configuration that is absent, revoked, future-dated, stale, unreviewed or
  scope-mismatched returns 409 with no write and no legal-state change.
- Acceptance: targeted TDD, scoped checks, exact allowlist evidence and independent High review.

## Lane done boundary

This manifest is accepted only after its own scoped checks and independent High review. Each child
then closes independently in the declared wave/serialization order. The lane does not change a
legal state, publish a production source, approve a child task, close the full V8 program, or run
the release gate.
