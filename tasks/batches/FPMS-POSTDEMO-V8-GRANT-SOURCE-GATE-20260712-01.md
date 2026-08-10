# FPMS Post-demo V8 Grant-source Gate Lane Manifest

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Manifest phase: `lane`
Task count: 8
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
after the successor activation receives independent approval and each child's named prerequisites
pass. This manifest orders the accepted schema child but does not itself change schema, catalog,
coverage ledger, source registry, customer decision, production seed, or release state.

## Execution waves and shared ownership

1. Wave G0: independently review and accept the successor activation only.
2. Wave G1: accept the already implemented/reviewed source schema candidate without repeating
   RED/GREEN, then execute the source service.
3. Wave G2: execute the source API after the source service passes.
4. Wave G3: execute the ingestion service.
5. Wave G4: execute the ingestion API and candidate read service under separate owners.
6. Wave G5: execute the candidate list API after both Wave G4 tasks pass.

Shared files remain serialized even when dependency waves otherwise permit concurrency:

- `GLOBAL_ALEMBIC_HEAD`, `backend/app/modules/system/models.py`,
  `backend/app/modules/documents/models.py` and `backend/app/models/__init__.py`: source schema
  acceptance remains serialized.
- All source carrier service files complete before any importing consumer.
- All source carrier API router/schema files complete before ingestion/list API shared edits.
- `grant_evidence_ingestion_service.py`: ingestion service before candidate read service.
- `documents/api.py` and `grant_evidence_schemas.py`: ingestion API before candidate list API.
- All SQLite-writing verification remains serialized through the repository queue.
- Independent review is required per protected task and binds that task's exact patch/evidence.

## Task Entries

## 001. FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01.md`
- Task SHA-256: `3236a8ae708ee5740c4e19a49fbeaa377de0354d3b880c249b8c8dacefbd51f7`
- Owner role: Team Lead / default
- Profile: `TC-QA`
- Exact closure: Rebind this grant-source lane manifest from five rows to eight rows while
  preserving unverified archive status and zero legal-state effect.
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

## 002. FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md`
- Task SHA-256: `f3ec1e107fb8cba0f4c041d1949eb646c674a6609de78d9533d4784526874eb6`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Persist the three fail-closed grant-source lineage carriers using
  `v8_grant_evidence_source_carrier.py`: reviewed source version, active GLOBAL selection and
  immutable evidence candidate provenance.
- Non-closure: No source seed, service, API, role or legal-state behavior.
- Canonical dependencies:
  - `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Shared owner: `GLOBAL_ALEMBIC_HEAD` and the exact ORM/model registry files named in the task.
- Acceptance: use the already implemented and independently reviewed exact candidate; after this
  activation passes, adopt it without repeating RED/GREEN.

## 003. FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01.md`
- Task SHA-256: `954960141ba75465176b01ab262a257d9b9128ab70303453173db7483429c502`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Register, independently review and activate CNIPA source versions; publish,
  revoke and resolve exact GLOBAL source configurations with canonical audit lineage.
- Non-closure: No API, role binding, candidate ingestion or legal-state behavior.
- Canonical dependencies:
  - `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`
  - `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01`
- Allowed implementation: exact `grant_evidence_source_service.py` and focused task files only.
- Runtime gate: unresolved or corrupt authority returns 409 with no write and no legal-state
  change.
- Acceptance: targeted TDD, scoped checks, exact allowlist evidence and independent High review.

## 004. FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01.md`
- Task SHA-256: `252b73f40e21deebeeb1e44f61c94f7a4dee4c9106fc4d82e1a518529c8a3d52`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: Expose the six authenticated institution configuration endpoints over the
  accepted source service using `SystemParam.Edit`.
- Non-closure: No default source, business-rule duplication, candidate ingestion or UI.
- Canonical dependencies:
  - `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`
  - `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01`
- Allowed implementation: exact `grant_evidence_source_schemas.py`, system router and focused task
  files only.
- Acceptance: targeted TDD, scoped checks, exact allowlist evidence and independent High review.

## 005. FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
- Task SHA-256: `82f7fe3ac496716dfe315f6eb698457aebb7966e5d9de083998f11f0ce193230`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Ingest one announcement/register candidate only from the confirmed
  controlled-source contract, archive it unverified and never change legal state.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the
  row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01`
  - `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01`
  - `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01`
  - `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`
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

## 006. FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md`
- Task SHA-256: `537f0defe2e8116af73fdc47fc040c454c32c7fb1871624b5698a4f67ce83445`
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

## 007. FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md`
- Task SHA-256: `daa6fddb220045e0d0ca4744be50bc5969eb20ae0db93c727106153e91d1e69d`
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

## 008. FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md`
- Task SHA-256: `6f0c8ff6299f5f36bbdf05c6d5b7719501c7f2b00df64b481945732d9f5d3890`
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
