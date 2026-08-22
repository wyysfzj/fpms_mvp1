# FPMS Post-demo V8 Foundation Batch Manifest

Status: FROZEN / READY FOR WAVE 0 EXECUTION
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Task count: 197
Runbook: `P0-prereq-heavy-story`

## Authority and Boundary

This manifest is the immutable foundation projection of the independently approved 283-row V8 catalog. It contains all 197 customer-independent rows and excludes all 86 customer-dependent/full-only rows. Tasks01–70 are inherited regression/evidence inputs and are not rescheduled.

It authorizes only its two Wave 0 parser/coverage tasks initially; no product task begins until both pass. Every agent owns exactly one listed task file. Shared ownership and every SQLite-writing verification are serialized through the machine-readable indexes. This manifest ends with `FPMS-V8-FOUNDATION-CLOSE-20260712-01`, never contains `FPMS-V8-FINAL-CLOSE-20260712-01`, and may report only `FOUNDATION PASS / FULL PROGRAM OPEN`.

## Task Entries

## 001. FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-QA`
- Exact closure: Extend manifest parsing to accept exact `tasks/postdemo/v8/*.md` declarations while preserving the accepted Additional-GAP path, duplicate detection and self-exclusion. It does not run the V8 release gate.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - None; Wave 0 materialization PASS is the external prerequisite.
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01.md`
  - `scripts/release_gate.sh`
  - `backend/tests/test_v8_manifest_release_gate.py`
  - `artifacts/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_manifest_release_gate.py tests/test_addgap_manifest_release_gate.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_manifest_release_gate.py && .venv/bin/ruff format tests/test_v8_manifest_release_gate.py && .venv/bin/ruff check tests/test_v8_manifest_release_gate.py`
  - `git diff --check -- scripts/release_gate.sh backend/tests/test_v8_manifest_release_gate.py tasks/postdemo/v8/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 002. FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-QA`
- Exact closure: Phase-aware validation: foundation lists every non-gated row and may classify omitted gated rows as unresolved, confirmed-pending, activated or prior-PASS; a lane manifest validates only its exact activation/tasks, confirmed gate(s), declared prerequisite PASS evidence and catalog membership while unrelated rows may remain pending; full manifest lists every catalog row with zero omissions. Permit `SELF_PENDING` only for the exact manifest-activation or close task currently producing its own evidence; reject every other undeclared/duplicate/pending-self row. It does not run product tests or the release gate.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - `FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01.md`
  - `scripts/v8_catalog_manifest_gate.py`
  - `backend/tests/test_v8_catalog_manifest_coverage_gate.py`
  - `artifacts/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_catalog_manifest_coverage_gate.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_catalog_manifest_coverage_gate.py && .venv/bin/ruff format tests/test_v8_catalog_manifest_coverage_gate.py && .venv/bin/ruff check tests/test_v8_catalog_manifest_coverage_gate.py`
  - `git diff --check -- scripts/v8_catalog_manifest_gate.py backend/tests/test_v8_catalog_manifest_coverage_gate.py tasks/postdemo/v8/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 003. FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only five nullable lifecycle projection/revision/verification columns to `t_case`.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
  - `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_l1_case_lifecycle_projection.py`
  - `backend/app/modules/cases/models.py`
  - `backend/tests/test_v8_w1_l1_case_lifecycle_projection.py`
  - `artifacts/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l1_case_lifecycle_projection.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_l1_case_lifecycle_projection.py app/modules/cases/models.py tests/test_v8_w1_l1_case_lifecycle_projection.py && .venv/bin/ruff format alembic/versions/v8_w1_l1_case_lifecycle_projection.py app/modules/cases/models.py tests/test_v8_w1_l1_case_lifecycle_projection.py && .venv/bin/ruff check alembic/versions/v8_w1_l1_case_lifecycle_projection.py app/modules/cases/models.py tests/test_v8_w1_l1_case_lifecycle_projection.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_l1_case_lifecycle_projection.py backend/app/modules/cases/models.py backend/tests/test_v8_w1_l1_case_lifecycle_projection.py tasks/postdemo/v8/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 004. FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only `t_case_activity_event`, sequence/idempotency uniqueness, composite parent key `(case_id,id)` and nullable same-case composite self-FK `(case_id,source_activity_id) → (case_id,id)`; SQLite test accepts NULL/same-case and rejects missing/cross-case sources.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_l2_case_activity_event.py`
  - `backend/app/modules/cases/models.py`
  - `backend/tests/test_v8_w1_l2_case_activity_event.py`
  - `artifacts/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l2_case_activity_event.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_l2_case_activity_event.py app/modules/cases/models.py tests/test_v8_w1_l2_case_activity_event.py && .venv/bin/ruff format alembic/versions/v8_w1_l2_case_activity_event.py app/modules/cases/models.py tests/test_v8_w1_l2_case_activity_event.py && .venv/bin/ruff check alembic/versions/v8_w1_l2_case_activity_event.py app/modules/cases/models.py tests/test_v8_w1_l2_case_activity_event.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_l2_case_activity_event.py backend/app/modules/cases/models.py backend/tests/test_v8_w1_l2_case_activity_event.py tasks/postdemo/v8/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 005. FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only `t_case_activity_event_evidence`, composite same-case FK and exact evidence-link uniqueness.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_l3_case_activity_evidence.py`
  - `backend/app/modules/cases/models.py`
  - `backend/tests/test_v8_w1_l3_case_activity_evidence.py`
  - `artifacts/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l3_case_activity_evidence.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_l3_case_activity_evidence.py app/modules/cases/models.py tests/test_v8_w1_l3_case_activity_evidence.py && .venv/bin/ruff format alembic/versions/v8_w1_l3_case_activity_evidence.py app/modules/cases/models.py tests/test_v8_w1_l3_case_activity_evidence.py && .venv/bin/ruff check alembic/versions/v8_w1_l3_case_activity_evidence.py app/modules/cases/models.py tests/test_v8_w1_l3_case_activity_evidence.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_l3_case_activity_evidence.py backend/app/modules/cases/models.py backend/tests/test_v8_w1_l3_case_activity_evidence.py tasks/postdemo/v8/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 006. FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only document evidence versions, creator/reviewer fields and nullable unique current-identity key.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
  - `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_d1_document_evidence_version.py`
  - `backend/app/modules/documents/models.py`
  - `backend/tests/test_v8_w1_d1_document_evidence_version.py`
  - `artifacts/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d1_document_evidence_version.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_d1_document_evidence_version.py app/modules/documents/models.py tests/test_v8_w1_d1_document_evidence_version.py && .venv/bin/ruff format alembic/versions/v8_w1_d1_document_evidence_version.py app/modules/documents/models.py tests/test_v8_w1_d1_document_evidence_version.py && .venv/bin/ruff check alembic/versions/v8_w1_d1_document_evidence_version.py app/modules/documents/models.py tests/test_v8_w1_d1_document_evidence_version.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_d1_document_evidence_version.py backend/app/modules/documents/models.py backend/tests/test_v8_w1_d1_document_evidence_version.py tasks/postdemo/v8/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 007. FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only parent-child evidence derivation rows.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_d2_document_evidence_derivation.py`
  - `backend/app/modules/documents/models.py`
  - `backend/tests/test_v8_w1_d2_document_evidence_derivation.py`
  - `artifacts/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d2_document_evidence_derivation.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_d2_document_evidence_derivation.py app/modules/documents/models.py tests/test_v8_w1_d2_document_evidence_derivation.py && .venv/bin/ruff format alembic/versions/v8_w1_d2_document_evidence_derivation.py app/modules/documents/models.py tests/test_v8_w1_d2_document_evidence_derivation.py && .venv/bin/ruff check alembic/versions/v8_w1_d2_document_evidence_derivation.py app/modules/documents/models.py tests/test_v8_w1_d2_document_evidence_derivation.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_d2_document_evidence_derivation.py backend/app/modules/documents/models.py backend/tests/test_v8_w1_d2_document_evidence_derivation.py tasks/postdemo/v8/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 008. FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only nullable manifest `evidence_version_id`, retaining `attachment_id`.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
  - `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_d3_work_package_evidence_link.py`
  - `backend/app/modules/official_workflows/models.py`
  - `backend/tests/test_v8_w1_d3_work_package_evidence_link.py`
  - `artifacts/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d3_work_package_evidence_link.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_d3_work_package_evidence_link.py app/modules/official_workflows/models.py tests/test_v8_w1_d3_work_package_evidence_link.py && .venv/bin/ruff format alembic/versions/v8_w1_d3_work_package_evidence_link.py app/modules/official_workflows/models.py tests/test_v8_w1_d3_work_package_evidence_link.py && .venv/bin/ruff check alembic/versions/v8_w1_d3_work_package_evidence_link.py app/modules/official_workflows/models.py tests/test_v8_w1_d3_work_package_evidence_link.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_d3_work_package_evidence_link.py backend/app/modules/official_workflows/models.py backend/tests/test_v8_w1_d3_work_package_evidence_link.py tasks/postdemo/v8/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 009. FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only itemized obligation headers and source/supersede fields; no line identity.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
  - `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_f1_fee_obligation.py`
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_v8_w1_f1_fee_obligation.py`
  - `artifacts/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f1_fee_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f1_fee_obligation.py app/modules/fees/models.py tests/test_v8_w1_f1_fee_obligation.py && .venv/bin/ruff format alembic/versions/v8_w1_f1_fee_obligation.py app/modules/fees/models.py tests/test_v8_w1_f1_fee_obligation.py && .venv/bin/ruff check alembic/versions/v8_w1_f1_fee_obligation.py app/modules/fees/models.py tests/test_v8_w1_f1_fee_obligation.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_f1_fee_obligation.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f1_fee_obligation.py tasks/postdemo/v8/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 010. FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only obligation lines, normalized year/source fields and nullable unique current identity key.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_f2_fee_obligation_line.py`
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_v8_w1_f2_fee_obligation_line.py`
  - `artifacts/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f2_fee_obligation_line.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f2_fee_obligation_line.py app/modules/fees/models.py tests/test_v8_w1_f2_fee_obligation_line.py && .venv/bin/ruff format alembic/versions/v8_w1_f2_fee_obligation_line.py app/modules/fees/models.py tests/test_v8_w1_f2_fee_obligation_line.py && .venv/bin/ruff check alembic/versions/v8_w1_f2_fee_obligation_line.py app/modules/fees/models.py tests/test_v8_w1_f2_fee_obligation_line.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_f2_fee_obligation_line.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f2_fee_obligation_line.py tasks/postdemo/v8/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 011. FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only obligation-line to draft-item linkage.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_f3_obligation_draft_link.py`
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_v8_w1_f3_obligation_draft_link.py`
  - `artifacts/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f3_obligation_draft_link.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py && .venv/bin/ruff format alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py && .venv/bin/ruff check alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_f3_obligation_draft_link.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f3_obligation_draft_link.py tasks/postdemo/v8/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 012. FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only obligation-line to payment-evidence linkage.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
  - `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_f4_obligation_payment_link.py`
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_v8_w1_f4_obligation_payment_link.py`
  - `artifacts/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f4_obligation_payment_link.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f4_obligation_payment_link.py app/modules/fees/models.py tests/test_v8_w1_f4_obligation_payment_link.py && .venv/bin/ruff format alembic/versions/v8_w1_f4_obligation_payment_link.py app/modules/fees/models.py tests/test_v8_w1_f4_obligation_payment_link.py && .venv/bin/ruff check alembic/versions/v8_w1_f4_obligation_payment_link.py app/modules/fees/models.py tests/test_v8_w1_f4_obligation_payment_link.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_f4_obligation_payment_link.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f4_obligation_payment_link.py tasks/postdemo/v8/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 013. FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only deterministic CASE/APPLICANT_SET approval source/scope/snapshot/interval carrier and exclusivity/identity constraints.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
  - `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w1_f5_fee_reduction_approval.py`
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_v8_w1_f5_fee_reduction_approval.py`
  - `artifacts/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f5_fee_reduction_approval.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f5_fee_reduction_approval.py app/modules/fees/models.py tests/test_v8_w1_f5_fee_reduction_approval.py && .venv/bin/ruff format alembic/versions/v8_w1_f5_fee_reduction_approval.py app/modules/fees/models.py tests/test_v8_w1_f5_fee_reduction_approval.py && .venv/bin/ruff check alembic/versions/v8_w1_f5_fee_reduction_approval.py app/modules/fees/models.py tests/test_v8_w1_f5_fee_reduction_approval.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w1_f5_fee_reduction_approval.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f5_fee_reduction_approval.py tasks/postdemo/v8/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 014. FPMS-V8-LC-CONTRACTS-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-CONTRACTS-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-INTERFACE`
- Exact closure: Define the three axes, lanes, confirmation states, command/result and evidence-reference interface only.
- Non-closure: No persistence, business adapter, endpoint or UI.
- Canonical dependencies:
  - `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
  - `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
  - `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-CONTRACTS-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_contracts.py`
  - `backend/tests/test_v8_lifecycle_contracts.py`
  - `artifacts/FPMS-V8-LC-CONTRACTS-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_contracts.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_contracts.py tests/test_v8_lifecycle_contracts.py && .venv/bin/ruff format app/modules/cases/lifecycle_contracts.py tests/test_v8_lifecycle_contracts.py && .venv/bin/ruff check app/modules/cases/lifecycle_contracts.py tests/test_v8_lifecycle_contracts.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_contracts.py backend/tests/test_v8_lifecycle_contracts.py tasks/postdemo/v8/FPMS-V8-LC-CONTRACTS-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-CONTRACTS-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-CONTRACTS-20260712-01` all PASS; exact closure complete and non-closure respected.

## 015. FPMS-V8-LC-ACTIVITY-APPEND-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: `append_case_activity()` allocates sequence, enforces idempotency, rejects a missing/cross-case `source_activity_id`, enforces same-case evidence and increments revision in the caller transaction.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
  - `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
  - `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
  - `FPMS-V8-LC-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_activity_service.py`
  - `backend/tests/test_v8_lifecycle_activity_append.py`
  - `artifacts/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_activity_append.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_activity_service.py tests/test_v8_lifecycle_activity_append.py && .venv/bin/ruff format app/modules/cases/lifecycle_activity_service.py tests/test_v8_lifecycle_activity_append.py && .venv/bin/ruff check app/modules/cases/lifecycle_activity_service.py tests/test_v8_lifecycle_activity_append.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_activity_service.py backend/tests/test_v8_lifecycle_activity_append.py tasks/postdemo/v8/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-ACTIVITY-APPEND-20260712-01` all PASS; exact closure complete and non-closure respected.

## 016. FPMS-V8-LC-LEGACY-PROJECTION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Implement the approved one-way `LegacyCaseStatusProjection` precedence, including unverified/conflict retention.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-LC-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_projection.py`
  - `backend/tests/test_v8_lifecycle_legacy_projection.py`
  - `artifacts/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_legacy_projection.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_projection.py tests/test_v8_lifecycle_legacy_projection.py && .venv/bin/ruff format app/modules/cases/lifecycle_projection.py tests/test_v8_lifecycle_legacy_projection.py && .venv/bin/ruff check app/modules/cases/lifecycle_projection.py tests/test_v8_lifecycle_legacy_projection.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_projection.py backend/tests/test_v8_lifecycle_legacy_projection.py tasks/postdemo/v8/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-LEGACY-PROJECTION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 017. FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Implement generic `apply_lifecycle_event()` orchestration without adding a generic HTTP endpoint or absorbing any event rule.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_service.py`
  - `backend/tests/test_v8_lifecycle_apply_event.py`
  - `artifacts/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_apply_event.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_service.py tests/test_v8_lifecycle_apply_event.py && .venv/bin/ruff format app/modules/cases/lifecycle_service.py tests/test_v8_lifecycle_apply_event.py && .venv/bin/ruff check app/modules/cases/lifecycle_service.py tests/test_v8_lifecycle_apply_event.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_service.py backend/tests/test_v8_lifecycle_apply_event.py tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01` all PASS; exact closure complete and non-closure respected.

## 018. FPMS-V8-LC-CASE-OPENED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: `CASE_OPENED`: initialize new case, not submitted, not established.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_case_opened.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-CASE-OPENED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_case_opened.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_case_opened.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_case_opened.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_case_opened.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_case_opened.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-CASE-OPENED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-CASE-OPENED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 019. FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: `FILING_PREPARATION_STARTED`: business stage only.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-CASE-OPENED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_filing_preparation_started.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_filing_preparation_started.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_filing_preparation_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_filing_preparation_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_filing_preparation_started.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_filing_preparation_started.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 020. FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Final submission evidence moves business to waiting receipt and official to submitted/waiting receipt.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_filing_external_submission.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_filing_external_submission.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_filing_external_submission.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_filing_external_submission.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_filing_external_submission.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_filing_external_submission.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 021. FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Owned receipt moves to prosecution, submission confirmed/waiting acceptance and application pending.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_filing_receipt_archived.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_filing_receipt_archived.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_filing_receipt_archived.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_filing_receipt_archived.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_filing_receipt_archived.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_filing_receipt_archived.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 022. FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Confirmed acceptance notice moves official stage to accepted only.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_acceptance_notice.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_acceptance_notice.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_acceptance_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_acceptance_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_acceptance_notice.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_acceptance_notice.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 023. FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Enter preliminary examination.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_preliminary_started.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_preliminary_started.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_preliminary_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_preliminary_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_preliminary_started.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_preliminary_started.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 024. FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Record pass evidence while keeping official preliminary stage and projecting legacy `PRELIM_PASS`.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_preliminary_passed.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_preliminary_passed.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_preliminary_passed.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_preliminary_passed.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_preliminary_passed.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_preliminary_passed.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 025. FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Confirmed rectification notice enters rectification response without changing legal status.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_rectification_notice.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_rectification_notice.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_rectification_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_rectification_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_rectification_notice.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_rectification_notice.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 026. FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Confirmed publication evidence enters published; application remains pending.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_publication_notice.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_publication_notice.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_publication_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_publication_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_publication_notice.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_publication_notice.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 027. FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Confirmed entry evidence enters substantive examination.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_substantive_started.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_substantive_started.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_substantive_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_substantive_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_substantive_started.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_substantive_started.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 028. FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: OA notice enters OA response with `oa_sequence`; legal status unchanged.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_oa_notice.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_oa_notice.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_oa_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_oa_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_oa_notice.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_oa_notice.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 029. FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Owned receipt returns official stage to substantive examination and business to prosecution.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_oa_receipt.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_oa_receipt.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_oa_receipt.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_oa_receipt.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_oa_receipt.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_oa_receipt.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 030. FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: From rejected or pending, enter reexamination; rejected returns to application pending and legacy `REEXAM`.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_reexamination_started.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_reexamination_started.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_reexamination_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_reexamination_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_reexamination_started.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_reexamination_started.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 031. FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Enter grant registration; legal status remains application pending.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_grant_registration_notice.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_grant_registration_notice.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_grant_registration_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_grant_registration_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_grant_registration_notice.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_grant_registration_notice.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 032. FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Controlled announcement, effective on announcement date, enters patent in force.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_grant_announcement.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_grant_announcement.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_grant_announcement.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_grant_announcement.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_grant_announcement.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_grant_announcement.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 033. FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Record same-status verification only; a differing register status returns a typed conflict/requires-specific-event result with no central change and performs no dispatch.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_register_status.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_register_status.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_register_status.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_register_status.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_register_status.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_register_status.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 034. FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Pending application enters rejected and closed.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_application_rejection.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_application_rejection.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_application_rejection.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_application_rejection.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_application_rejection.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_application_rejection.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 035. FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Un-granted application enters withdrawn and closed.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_application_withdrawal.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_application_withdrawal.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_application_withdrawal.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_application_withdrawal.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_application_withdrawal.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_application_withdrawal.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 036. FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Un-granted application enters abandoned and closed.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_application_abandonment.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_application_abandonment.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_application_abandonment.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_application_abandonment.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_application_abandonment.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_application_abandonment.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 037. FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Patent in force enters terminated and closed.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_patent_termination.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_patent_termination.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_patent_termination.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_patent_termination.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_patent_termination.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_patent_termination.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 038. FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Patent in force enters expired and closed.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_patent_expiry.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_patent_expiry.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_patent_expiry.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_patent_expiry.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_patent_expiry.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_patent_expiry.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 039. FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Patent in force enters invalidated and closed.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_patent_invalidation.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_patent_invalidation.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_patent_invalidation.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_patent_invalidation.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_patent_invalidation.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_patent_invalidation.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 040. FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Abandoned application returns to pending at the confirmed restored procedure stage.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_application_restoration.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_application_restoration.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_application_restoration.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_application_restoration.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_application_restoration.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_application_restoration.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 041. FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Terminated patent returns to in-force/post-grant state.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01.md`
  - `backend/tests/test_v8_lifecycle_patent_restoration.py`
  - `backend/app/modules/cases/lifecycle_rules.py`
  - `artifacts/FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_patent_restoration.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_patent_restoration.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_patent_restoration.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_patent_restoration.py app/modules/cases/lifecycle_rules.py`
  - `git diff --check -- backend/tests/test_v8_lifecycle_patent_restoration.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 042. FPMS-V8-DE-CONTRACTS-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-INTERFACE`
- Exact closure: Define evidence roles, states and version/derivation commands only.
- Non-closure: No persistence, business adapter, endpoint or UI.
- Canonical dependencies:
  - `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
  - `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
  - `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`
  - `backend/app/modules/documents/evidence_contracts.py`
  - `backend/tests/test_v8_document_evidence_contracts.py`
  - `artifacts/FPMS-V8-DE-CONTRACTS-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py && .venv/bin/ruff format app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py && .venv/bin/ruff check app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py`
  - `git diff --check -- backend/app/modules/documents/evidence_contracts.py backend/tests/test_v8_document_evidence_contracts.py tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-CONTRACTS-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-CONTRACTS-20260712-01` all PASS; exact closure complete and non-closure respected.

## 043. FPMS-V8-DE-REGISTER-VERSION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-REGISTER-VERSION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Register one immutable version and reject wrong-case attachment/document relations.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-REGISTER-VERSION-20260712-01.md`
  - `backend/app/modules/documents/evidence_service.py`
  - `backend/tests/test_v8_document_evidence_register_version.py`
  - `artifacts/FPMS-V8-DE-REGISTER-VERSION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_register_version.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_register_version.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_register_version.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_register_version.py`
  - `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_register_version.py tasks/postdemo/v8/FPMS-V8-DE-REGISTER-VERSION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-VERSION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 044. FPMS-V8-DE-REGISTER-DERIVATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Register one same-case parent-child derivation.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_service.py`
  - `backend/tests/test_v8_document_evidence_derivation.py`
  - `artifacts/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_derivation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_derivation.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_derivation.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_derivation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_derivation.py tasks/postdemo/v8/FPMS-V8-DE-REGISTER-DERIVATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-DERIVATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 045. FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Switch current working version; final version linked to a receipt cannot be ordinarily replaced.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01.md`
  - `backend/app/modules/documents/evidence_service.py`
  - `backend/tests/test_v8_document_evidence_current_version.py`
  - `artifacts/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_current_version.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_current_version.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_current_version.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_current_version.py`
  - `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_current_version.py tasks/postdemo/v8/FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 046. FPMS-V8-DE-REVIEW-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-SERVICE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Approve/reject one evidence version, require reviewer != creator, preserve review history and reject final/current promotion of rejected evidence.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-SERVICE-20260712-01.md`
  - `backend/app/modules/documents/evidence_service.py`
  - `backend/tests/test_v8_document_evidence_review_service.py`
  - `artifacts/FPMS-V8-DE-REVIEW-SERVICE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_review_service.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py tests/test_v8_document_evidence_review_service.py && .venv/bin/ruff format app/modules/documents/evidence_service.py tests/test_v8_document_evidence_review_service.py && .venv/bin/ruff check app/modules/documents/evidence_service.py tests/test_v8_document_evidence_review_service.py`
  - `git diff --check -- backend/app/modules/documents/evidence_service.py backend/tests/test_v8_document_evidence_review_service.py tasks/postdemo/v8/FPMS-V8-DE-REVIEW-SERVICE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-SERVICE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 047. FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Implement only `finalize_external_submission(command, transaction)`: validate same-case current independently reviewed final evidence, persist/reuse the exact external-submission evidence result and append its `DOCUMENT` activity with `center_changes={}`; no filing/OA lifecycle event, receipt handling or HTTP.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
  - `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/tests/test_v8_finalize_external_submission_seam.py`
  - `artifacts/FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_finalize_external_submission_seam.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py tests/test_v8_finalize_external_submission_seam.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py tests/test_v8_finalize_external_submission_seam.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py tests/test_v8_finalize_external_submission_seam.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/tests/test_v8_finalize_external_submission_seam.py tasks/postdemo/v8/FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01` all PASS; exact closure complete and non-closure respected.

## 048. FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Implement only `prepare_oa_reply(command, transaction)`: validate the same-case source OA notice/evidence and selected copyable/noncopyable attachment policy, then atomically create/reuse exactly one DRAFT OA_OUT evidence version and its unique OA reply package/link in the caller transaction. The newly prepared reply is not treated as independently reviewed; no HTTP, task close, external submission or lifecycle transition occurs.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
  - `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
  - `FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/tests/test_v8_prepare_oa_reply_seam.py`
  - `artifacts/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_prepare_oa_reply_seam.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py tests/test_v8_prepare_oa_reply_seam.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py tests/test_v8_prepare_oa_reply_seam.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py tests/test_v8_prepare_oa_reply_seam.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/tests/test_v8_prepare_oa_reply_seam.py tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` all PASS; exact closure complete and non-closure respected.

## 049. FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing attachment POST records the authenticated creator and registers one evidence version in the same transaction; file/attachment/version all succeed or roll back together.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/tests/test_v8_attachment_evidence_atomic_adapter.py`
  - `artifacts/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_attachment_evidence_atomic_adapter.py tests/test_document_attachment_upload_metadata_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/api.py app/modules/documents/service.py app/modules/documents/schemas.py tests/test_v8_attachment_evidence_atomic_adapter.py && .venv/bin/ruff format app/modules/documents/api.py app/modules/documents/service.py app/modules/documents/schemas.py tests/test_v8_attachment_evidence_atomic_adapter.py && .venv/bin/ruff check app/modules/documents/api.py app/modules/documents/service.py app/modules/documents/schemas.py tests/test_v8_attachment_evidence_atomic_adapter.py`
  - `git diff --check -- backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_v8_attachment_evidence_atomic_adapter.py tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 050. FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing generated-attachment service registers its evidence version in the same transaction, without changing template rendering behavior.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_v8_generated_attachment_evidence_adapter.py`
  - `artifacts/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_generated_attachment_evidence_adapter.py tests/test_document_generated_attachment_persist.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_template_source_resolution.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_v8_generated_attachment_evidence_adapter.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_v8_generated_attachment_evidence_adapter.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_v8_generated_attachment_evidence_adapter.py`
  - `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_v8_generated_attachment_evidence_adapter.py tasks/postdemo/v8/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 051. FPMS-V8-DE-REVIEW-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: One POST approve/reject endpoint using `Doc.Edit`; 200 idempotent and 400/401/403/404/409/422 semantics with maker/reviewer separation.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-API-20260712-01.md`
  - `backend/app/modules/documents/evidence_review_schemas.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_document_evidence_review_api.py`
  - `artifacts/FPMS-V8-DE-REVIEW-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_review_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_review_schemas.py app/modules/documents/api.py tests/test_v8_document_evidence_review_api.py && .venv/bin/ruff format app/modules/documents/evidence_review_schemas.py app/modules/documents/api.py tests/test_v8_document_evidence_review_api.py && .venv/bin/ruff check app/modules/documents/evidence_review_schemas.py app/modules/documents/api.py tests/test_v8_document_evidence_review_api.py`
  - `git diff --check -- backend/app/modules/documents/evidence_review_schemas.py backend/app/modules/documents/api.py backend/tests/test_v8_document_evidence_review_api.py tasks/postdemo/v8/FPMS-V8-DE-REVIEW-API-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-API-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-API-20260712-01` all PASS; exact closure complete and non-closure respected.

## 052. FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing bodyless document-detail read returns each attachment's current evidence-version ID, role, creator and review/current/final state without inferring readiness.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01.md`
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_v8_attachment_evidence_read_projection.py`
  - `artifacts/FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_attachment_evidence_read_projection.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/api.py app/modules/documents/schemas.py app/modules/documents/service.py tests/test_v8_attachment_evidence_read_projection.py && .venv/bin/ruff format app/modules/documents/api.py app/modules/documents/schemas.py app/modules/documents/service.py tests/test_v8_attachment_evidence_read_projection.py && .venv/bin/ruff check app/modules/documents/api.py app/modules/documents/schemas.py app/modules/documents/service.py tests/test_v8_attachment_evidence_read_projection.py`
  - `git diff --check -- backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_v8_attachment_evidence_read_projection.py tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 053. FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-FE-ADAPTER`
- Exact closure: Type evidence-version projection and one review action/result without inferring review/current/final state.
- Non-closure: No page behavior, server-state inference or backend change.
- Canonical dependencies:
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01.md`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/api/contracts/v8_document_evidence_review.contract.ts`
  - `artifacts/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/api/documents.ts src/api/documents.types.ts src/api/contracts/v8_document_evidence_review.contract.ts --max-warnings 0`
  - `git diff --check -- frontend/src/api/documents.ts frontend/src/api/documents.types.ts frontend/src/api/contracts/v8_document_evidence_review.contract.ts tasks/postdemo/v8/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 054. FPMS-V8-DE-REVIEW-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Attachment list shows creator/reviewer/status and one approve/reject capability; the creator cannot self-review and errors are Simplified Chinese.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-UI-20260712-01.md`
  - `frontend/src/modules/documents/components/AttachmentList.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-document-evidence-review-ui.spec.ts`
  - `artifacts/FPMS-V8-DE-REVIEW-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-document-evidence-review-ui.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/documents/components/AttachmentList.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/documents/components/AttachmentList.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-document-evidence-review-ui.spec.ts tasks/postdemo/v8/FPMS-V8-DE-REVIEW-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 055. FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Case POST no longer accepts arbitrary legacy status; it initializes through `CASE_OPENED`.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-CASE-OPENED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01.md`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_v8_case_create_status_gate.py`
  - `artifacts/FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_case_create_status_gate.py tests/test_case_missing_fields_crud.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_create_status_gate.py && .venv/bin/ruff format app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_create_status_gate.py && .venv/bin/ruff check app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_create_status_gate.py`
  - `git diff --check -- backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_v8_case_create_status_gate.py tasks/postdemo/v8/FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 056. FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Full case update cannot directly change legacy status once lifecycle is active; conflict is 409 with no partial update.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_v8_case_update_status_gate.py`
  - `artifacts/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_case_update_status_gate.py tests/test_case_missing_fields_crud.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/service.py tests/test_v8_case_update_status_gate.py && .venv/bin/ruff format app/modules/cases/service.py tests/test_v8_case_update_status_gate.py && .venv/bin/ruff check app/modules/cases/service.py tests/test_v8_case_update_status_gate.py`
  - `git diff --check -- backend/app/modules/cases/service.py backend/tests/test_v8_case_update_status_gate.py tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 057. FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Case create page cannot select/send arbitrary legacy status and explains lifecycle initialization in Chinese.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01.md`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-create-status-gate.spec.ts`
  - `artifacts/FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-create-status-gate.spec.ts --workers=1`
  - `cd frontend && npx eslint src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseCreate.vue --max-warnings 0`
  - `git diff --check -- frontend/src/api/cases.ts frontend/src/api/cases.types.ts frontend/src/modules/cases/pages/CaseCreate.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-create-status-gate.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 058. FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Case edit page displays compatibility status read-only and never submits it.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01.md`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-edit-status-gate.spec.ts`
  - `artifacts/FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-edit-status-gate.spec.ts --workers=1`
  - `cd frontend && npx eslint src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseEdit.vue --max-warnings 0`
  - `git diff --check -- frontend/src/api/cases.ts frontend/src/api/cases.types.ts frontend/src/modules/cases/pages/CaseEdit.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-edit-status-gate.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 059. FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Resolving/creating the filing preparation package records `FILING_PREPARATION_STARTED` exactly once.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_filing_preparation_started_adapter.py`
  - `artifacts/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_filing_preparation_started_adapter.py tests/test_addgap_workpkg_resolve_key_schema.py tests/test_addgap_filing_ensure_service.py tests/test_addgap_filing_resolve_api.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts src/tests/addgap-filing-case-entry.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_preparation_started_adapter.py tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 060. FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Batch filing calls external-submission lifecycle event instead of assigning `WAITING_RECEIPT`.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01.md`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_v8_batch_filing_lifecycle_adapter.py`
  - `artifacts/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_batch_filing_lifecycle_adapter.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts src/tests/addgap-filing-case-entry.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/service.py tests/test_v8_batch_filing_lifecycle_adapter.py && .venv/bin/ruff format app/modules/cases/service.py tests/test_v8_batch_filing_lifecycle_adapter.py && .venv/bin/ruff check app/modules/cases/service.py tests/test_v8_batch_filing_lifecycle_adapter.py`
  - `git diff --check -- backend/app/modules/cases/service.py backend/tests/test_v8_batch_filing_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 061. FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Resolver emits `lifecycle_event_type`; document create stops direct `Case.status` writes and dispatches supported non-grant semantics exactly once. For `GRANT_NOTICE`, it passes the frozen resolved semantics/source to the grant adapter and appends no lifecycle event itself.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-CASE-OPENED-20260712-01`
  - `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
  - `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
  - `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
  - `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/semantics.py`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_v8_document_semantics_event_adapter.py`
  - `artifacts/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_document_semantics_event_adapter.py tests/test_addgap_document_create_atomicity.py tests/test_addgap_document_semantics.py tests/test_addgap_document_semantic_state_effect.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_oa_alias_reply_validation.py tests/test_addgap_notice_grant_activation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py app/modules/documents/service.py tests/test_v8_document_semantics_event_adapter.py && .venv/bin/ruff format app/modules/documents/semantics.py app/modules/documents/service.py tests/test_v8_document_semantics_event_adapter.py && .venv/bin/ruff check app/modules/documents/semantics.py app/modules/documents/service.py tests/test_v8_document_semantics_event_adapter.py`
  - `git diff --check -- backend/app/modules/documents/semantics.py backend/app/modules/documents/service.py backend/tests/test_v8_document_semantics_event_adapter.py tasks/postdemo/v8/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 062. FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Manifest writes/reads evidence-version identity while retaining attachment compatibility.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
  - `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_work_package_manifest_evidence_version.py`
  - `artifacts/FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_work_package_manifest_evidence_version.py tests/test_addgap_workpkg_resolve_key_schema.py tests/test_addgap_filing_ensure_service.py tests/test_addgap_filing_resolve_api.py tests/test_addgap_oa_ensure_service.py tests/test_addgap_oa_resolve_api.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts src/tests/addgap-filing-case-entry.spec.ts src/tests/addgap-oa-page-resolve.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_work_package_manifest_evidence_version.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_work_package_manifest_evidence_version.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_work_package_manifest_evidence_version.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_work_package_manifest_evidence_version.py tasks/postdemo/v8/FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 063. FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Filing readiness requires current independently reviewed `FILING_FULL_WORD`; arbitrary/unreviewed/self-reviewed Word attachment is insufficient.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01.md`
  - `backend/app/modules/documents/evidence_policy.py`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_filing_full_word_gate.py`
  - `artifacts/FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_filing_full_word_gate.py tests/test_addgap_workpkg_resolve_key_schema.py tests/test_addgap_filing_ensure_service.py tests/test_addgap_filing_resolve_api.py tests/test_addgap_oa_ensure_service.py tests/test_addgap_oa_resolve_api.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts src/tests/addgap-filing-case-entry.spec.ts src/tests/addgap-oa-page-resolve.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_policy.py app/modules/official_workflows/service.py tests/test_v8_filing_full_word_gate.py && .venv/bin/ruff format app/modules/documents/evidence_policy.py app/modules/official_workflows/service.py tests/test_v8_filing_full_word_gate.py && .venv/bin/ruff check app/modules/documents/evidence_policy.py app/modules/official_workflows/service.py tests/test_v8_filing_full_word_gate.py`
  - `git diff --check -- backend/app/modules/documents/evidence_policy.py backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_full_word_gate.py tasks/postdemo/v8/FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 064. FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: XML zip/final XML must derive from the current reviewed Word lineage; no real XML generation.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01.md`
  - `backend/app/modules/documents/evidence_policy.py`
  - `backend/tests/test_v8_filing_xml_derivation_gate.py`
  - `artifacts/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_filing_xml_derivation_gate.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_policy.py tests/test_v8_filing_xml_derivation_gate.py && .venv/bin/ruff format app/modules/documents/evidence_policy.py tests/test_v8_filing_xml_derivation_gate.py && .venv/bin/ruff check app/modules/documents/evidence_policy.py tests/test_v8_filing_xml_derivation_gate.py`
  - `git diff --check -- backend/app/modules/documents/evidence_policy.py backend/tests/test_v8_filing_xml_derivation_gate.py tasks/postdemo/v8/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 065. FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing filing entrypoint calls `finalize_external_submission()` and records the filing submission lifecycle event in the same transaction; it does not duplicate evidence validation.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
  - `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
  - `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`
  - `FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_filing_external_submission_adapter.py`
  - `artifacts/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_filing_external_submission_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_filing_external_submission_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_filing_external_submission_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_filing_external_submission_adapter.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_external_submission_adapter.py tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 066. FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Valid filing receipt links to final submission and records receipt lifecycle event in the same transaction.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_filing_receipt_lifecycle_adapter.py`
  - `artifacts/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_filing_receipt_lifecycle_adapter.py tests/test_addgap_receipt_same_case_gate.py tests/test_addgap_oa_receipt_source_gate.py tests/test_addgap_receipt_history_scan.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_filing_receipt_lifecycle_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_filing_receipt_lifecycle_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_filing_receipt_lifecycle_adapter.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_receipt_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 067. FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing OA_OUT entrypoint calls `prepare_oa_reply()` so OA_OUT creation and its unique package reply link succeed or roll back together; task remains open and no seam logic is duplicated.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01.md`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_oa_out_package_atomic_link.py`
  - `artifacts/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_oa_out_package_atomic_link.py tests/test_addgap_oa_ensure_service.py tests/test_addgap_oa_resolve_api.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py tests/test_document_ui_deadline_generation.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-oa-page-resolve.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_out_package_atomic_link.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_out_package_atomic_link.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_out_package_atomic_link.py`
  - `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/official_workflows/service.py backend/tests/test_v8_oa_out_package_atomic_link.py tasks/postdemo/v8/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01` all PASS; exact closure complete and non-closure respected.

## 068. FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: OA_OUT/package preparation appends `OA_REPLY_PREPARED` DOCUMENT activity without central changes.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_oa_prepared_activity.py`
  - `artifacts/FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_oa_prepared_activity.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_oa_prepared_activity.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_oa_prepared_activity.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_oa_prepared_activity.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_oa_prepared_activity.py tasks/postdemo/v8/FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01` all PASS; exact closure complete and non-closure respected.

## 069. FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing OA submission entrypoint calls `finalize_external_submission()` for the exact reviewed OA package/final evidence; it does not close the task or duplicate seam validation.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
  - `FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_oa_external_submission_evidence.py`
  - `artifacts/FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_oa_external_submission_evidence.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_oa_external_submission_evidence.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_oa_external_submission_evidence.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_oa_external_submission_evidence.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_oa_external_submission_evidence.py tasks/postdemo/v8/FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 070. FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing receipt transaction also calls `OA_RECEIPT_ARCHIVED`, preserving exactly-one task close and legacy SUB_EXAM.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_oa_receipt_lifecycle_adapter.py`
  - `artifacts/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_oa_receipt_lifecycle_adapter.py tests/test_addgap_receipt_same_case_gate.py tests/test_addgap_oa_receipt_source_gate.py tests/test_addgap_receipt_history_scan.py tests/test_addgap_oa_receipt_archive_event.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_document_ui_deadline_generation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_oa_receipt_lifecycle_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_oa_receipt_lifecycle_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_oa_receipt_lifecycle_adapter.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_oa_receipt_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 071. FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: OA_OUT no longer writes source `reply_date`; the valid owned receipt transaction sets the formal reply projection exactly once.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01.md`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_oa_reply_date_receipt_projection.py`
  - `artifacts/FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_oa_reply_date_receipt_projection.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py tests/test_addgap_oa_receipt_archive_event.py tests/test_document_ui_deadline_generation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_reply_date_receipt_projection.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_reply_date_receipt_projection.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_reply_date_receipt_projection.py`
  - `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/official_workflows/service.py backend/tests/test_v8_oa_reply_date_receipt_projection.py tasks/postdemo/v8/FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 072. FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Copyable OA permits the frozen structured attachment combination only.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01.md`
  - `backend/app/modules/documents/evidence_policy.py`
  - `backend/tests/test_v8_oa_copyable_attachment_policy.py`
  - `artifacts/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_oa_copyable_attachment_policy.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_policy.py tests/test_v8_oa_copyable_attachment_policy.py && .venv/bin/ruff format app/modules/documents/evidence_policy.py tests/test_v8_oa_copyable_attachment_policy.py && .venv/bin/ruff check app/modules/documents/evidence_policy.py tests/test_v8_oa_copyable_attachment_policy.py`
  - `git diff --check -- backend/app/modules/documents/evidence_policy.py backend/tests/test_v8_oa_copyable_attachment_policy.py tasks/postdemo/v8/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01` all PASS; exact closure complete and non-closure respected.

## 073. FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Preserve full reply PDF → extracted appendix derivation; only appendix may be “其他证明文件”.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01.md`
  - `backend/app/modules/documents/evidence_policy.py`
  - `backend/tests/test_v8_oa_noncopyable_appendix_policy.py`
  - `artifacts/FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_oa_noncopyable_appendix_policy.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_policy.py tests/test_v8_oa_noncopyable_appendix_policy.py && .venv/bin/ruff format app/modules/documents/evidence_policy.py tests/test_v8_oa_noncopyable_appendix_policy.py && .venv/bin/ruff check app/modules/documents/evidence_policy.py tests/test_v8_oa_noncopyable_appendix_policy.py`
  - `git diff --check -- backend/app/modules/documents/evidence_policy.py backend/tests/test_v8_oa_noncopyable_appendix_policy.py tasks/postdemo/v8/FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01` all PASS; exact closure complete and non-closure respected.

## 074. FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Consume the resolver's frozen grant semantics and act as the sole dispatcher of the grant-registration event while retaining confirmed due/source lineage; prove exactly one activity/revision and no second append by the generic document adapter.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_v8_grant_notice_lifecycle_adapter.py`
  - `artifacts/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_notice_lifecycle_adapter.py tests/test_addgap_grant_lineage_schema.py tests/test_addgap_grant_source_deadline.py tests/test_addgap_grant_auto_draft_gate.py tests/test_addgap_notice_grant_activation.py tests/test_addgap_grant_replacement_service.py tests/test_addgap_grant_replacement_api.py tests/test_addgap_grant_list_lineage_projection.py tests/test_addgap_grant_state_lineage_gate.py tests/test_b3_fee_linking.py tests/test_grant_fee_notice_task_creation.py tests/test_addgap_document_semantic_state_effect.py tests/test_document_impact_preview_api.py tests/test_addgap_grant_preview_no_auto_draft.py tests/test_spec_alignment_e2e.py tests/test_b_official_due_date_task_generation.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_grant_fee_worklist_api.py tests/test_grant_fee_state_machine_api.py tests/test_addgap_grant_mutation_lineage_gate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_document_api.py tests/test_grant_fee_prereq_schema.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_v8_grant_notice_lifecycle_adapter.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_v8_grant_notice_lifecycle_adapter.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_v8_grant_notice_lifecycle_adapter.py`
  - `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_notice_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 075. FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Remove only document attachment → `GRANTED` side effect.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01.md`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_v8_grant_attachment_no_legal_effect.py`
  - `artifacts/FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_attachment_no_legal_effect.py tests/test_addgap_grant_lineage_schema.py tests/test_addgap_grant_source_deadline.py tests/test_addgap_grant_auto_draft_gate.py tests/test_addgap_notice_grant_activation.py tests/test_addgap_grant_replacement_service.py tests/test_addgap_grant_replacement_api.py tests/test_addgap_grant_list_lineage_projection.py tests/test_addgap_grant_state_lineage_gate.py tests/test_b3_fee_linking.py tests/test_grant_fee_notice_task_creation.py tests/test_addgap_grant_preview_no_auto_draft.py tests/test_spec_alignment_e2e.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_grant_fee_worklist_api.py tests/test_grant_fee_state_machine_api.py tests/test_addgap_grant_mutation_lineage_gate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_document_api.py tests/test_addgap_document_create_atomicity.py tests/test_grant_fee_prereq_schema.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_v8_grant_attachment_no_legal_effect.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_v8_grant_attachment_no_legal_effect.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_v8_grant_attachment_no_legal_effect.py`
  - `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_v8_grant_attachment_no_legal_effect.py tasks/postdemo/v8/FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 076. FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Replace the grant-fee `mark_done` → `GRANTED` shortcut with exactly one idempotent `GRANT_FEE_TASK_DONE` FEE activity carrying `center_changes={}` in the same transaction; no legal-state change.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01.md`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_v8_grant_fee_done_no_legal_effect.py`
  - `artifacts/FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_fee_done_no_legal_effect.py tests/test_addgap_grant_lineage_schema.py tests/test_addgap_grant_source_deadline.py tests/test_addgap_grant_auto_draft_gate.py tests/test_addgap_notice_grant_activation.py tests/test_addgap_grant_replacement_service.py tests/test_addgap_grant_replacement_api.py tests/test_addgap_grant_list_lineage_projection.py tests/test_addgap_grant_state_lineage_gate.py tests/test_b3_fee_linking.py tests/test_grant_fee_notice_task_creation.py tests/test_addgap_grant_preview_no_auto_draft.py tests/test_spec_alignment_e2e.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_grant_fee_worklist_api.py tests/test_grant_fee_state_machine_api.py tests/test_addgap_grant_mutation_lineage_gate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_document_api.py tests/test_addgap_document_create_atomicity.py tests/test_grant_fee_prereq_schema.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_v8_grant_fee_done_no_legal_effect.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_v8_grant_fee_done_no_legal_effect.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_v8_grant_fee_done_no_legal_effect.py`
  - `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_fee_done_no_legal_effect.py tasks/postdemo/v8/FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01` all PASS; exact closure complete and non-closure respected.

## 077. FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Archive certificate as DOCUMENT activity/evidence without changing grant effective date.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01.md`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_v8_certificate_archived_activity.py`
  - `artifacts/FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_certificate_archived_activity.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_v8_certificate_archived_activity.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_v8_certificate_archived_activity.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_v8_certificate_archived_activity.py`
  - `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_v8_certificate_archived_activity.py tasks/postdemo/v8/FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01` all PASS; exact closure complete and non-closure respected.

## 078. FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/preliminary-start`: confirmed preliminary-examination source invokes only `PRELIMINARY_EXAMINATION_STARTED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_preliminary_started_evidence_api.py`
  - `artifacts/FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_preliminary_started_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_preliminary_started_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_preliminary_started_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_preliminary_started_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_preliminary_started_evidence_api.py tasks/postdemo/v8/FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 079. FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/preliminary-pass`: confirmed preliminary-pass evidence invokes only `PRELIMINARY_EXAMINATION_PASSED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_preliminary_passed_evidence_api.py`
  - `artifacts/FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_preliminary_passed_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_preliminary_passed_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_preliminary_passed_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_preliminary_passed_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_preliminary_passed_evidence_api.py tasks/postdemo/v8/FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 080. FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/rectification-notice`: executable rectification notice plus confirmed due date invokes only `RECTIFICATION_NOTICE_RECORDED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_rectification_notice_evidence_api.py`
  - `artifacts/FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_rectification_notice_evidence_api.py tests/test_addgap_document_deadline_carrier.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_rectification_notice_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_rectification_notice_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_rectification_notice_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_rectification_notice_evidence_api.py tasks/postdemo/v8/FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 081. FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/publication-notice`: controlled publication notice/date invokes only `PUBLICATION_NOTICE_RECORDED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_publication_notice_evidence_api.py`
  - `artifacts/FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_publication_notice_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_publication_notice_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_publication_notice_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_publication_notice_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_publication_notice_evidence_api.py tasks/postdemo/v8/FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 082. FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/substantive-start`: confirmed entry-into-examination evidence invokes only `SUBSTANTIVE_EXAMINATION_STARTED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_substantive_started_evidence_api.py`
  - `artifacts/FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_substantive_started_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_substantive_started_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_substantive_started_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_substantive_started_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_substantive_started_evidence_api.py tasks/postdemo/v8/FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 083. FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/reexamination-start`: confirmed reexamination acceptance/executable source invokes only `REEXAMINATION_STARTED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_reexamination_started_evidence_api.py`
  - `artifacts/FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_reexamination_started_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_reexamination_started_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_reexamination_started_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_reexamination_started_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_reexamination_started_evidence_api.py tasks/postdemo/v8/FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 084. FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/application-rejection`: effective rejection decision invokes only `APPLICATION_REJECTION_CONFIRMED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_application_rejection_evidence_api.py`
  - `artifacts/FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_application_rejection_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_rejection_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_rejection_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_rejection_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_application_rejection_evidence_api.py tasks/postdemo/v8/FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 085. FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/application-withdrawal`: withdrawal request plus official confirmation/registration evidence invokes only `APPLICATION_WITHDRAWAL_CONFIRMED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_application_withdrawal_evidence_api.py`
  - `artifacts/FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_application_withdrawal_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_withdrawal_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_withdrawal_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_withdrawal_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_application_withdrawal_evidence_api.py tasks/postdemo/v8/FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 086. FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/application-abandonment`: effective deemed-abandonment/abandon-right evidence invokes only `APPLICATION_ABANDONMENT_CONFIRMED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_application_abandonment_evidence_api.py`
  - `artifacts/FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_application_abandonment_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_abandonment_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_abandonment_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_abandonment_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_application_abandonment_evidence_api.py tasks/postdemo/v8/FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 087. FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST `/documents/{id}/lifecycle/application-restoration`: official restoration decision plus explicit restored procedure stage invokes only `APPLICATION_RIGHT_RESTORATION_CONFIRMED`.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/lifecycle_evidence_adapters.py`
  - `backend/app/modules/documents/api.py`
  - `backend/tests/test_v8_application_restoration_evidence_api.py`
  - `artifacts/FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_application_restoration_evidence_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_restoration_evidence_api.py && .venv/bin/ruff format app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_restoration_evidence_api.py && .venv/bin/ruff check app/modules/documents/lifecycle_evidence_adapters.py app/modules/documents/api.py tests/test_v8_application_restoration_evidence_api.py`
  - `git diff --check -- backend/app/modules/documents/lifecycle_evidence_adapters.py backend/app/modules/documents/api.py backend/tests/test_v8_application_restoration_evidence_api.py tasks/postdemo/v8/FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 088. FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Replace generated placeholders with the frozen eight customer templates and exact mappings as one versioned seed dataset.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01.md`
  - `backend/scripts/seed_dev.py`
  - `backend/tests/test_v8_format_letter_real_template_set.py`
  - `backend/storage/templates/format_letters/format_letter_001.docx`
  - `backend/storage/templates/format_letters/format_letter_002.docx`
  - `backend/storage/templates/format_letters/format_letter_003.docx`
  - `backend/storage/templates/format_letters/format_letter_004.docx`
  - `backend/storage/templates/format_letters/format_letter_005.docx`
  - `backend/storage/templates/format_letters/format_letter_006.docx`
  - `backend/storage/templates/format_letters/format_letter_007.docx`
  - `backend/storage/templates/format_letters/format_letter_008.docx`
  - `artifacts/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_real_template_set.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/seed_dev.py tests/test_v8_format_letter_real_template_set.py && .venv/bin/ruff format scripts/seed_dev.py tests/test_v8_format_letter_real_template_set.py && .venv/bin/ruff check scripts/seed_dev.py tests/test_v8_format_letter_real_template_set.py`
  - `git diff --check -- backend/scripts/seed_dev.py backend/tests/test_v8_format_letter_real_template_set.py backend/storage/templates/format_letters/format_letter_001.docx backend/storage/templates/format_letters/format_letter_002.docx backend/storage/templates/format_letters/format_letter_003.docx backend/storage/templates/format_letters/format_letter_004.docx backend/storage/templates/format_letters/format_letter_005.docx backend/storage/templates/format_letters/format_letter_006.docx backend/storage/templates/format_letters/format_letter_007.docx backend/storage/templates/format_letters/format_letter_008.docx tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01` all PASS; exact closure complete and non-closure respected.

## 089. FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Build source notice, case/applicant, selected contact, default/selected salutation, amount/deadline and template-variant context.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01.md`
  - `backend/app/modules/documents/letter_context.py`
  - `backend/tests/test_v8_format_letter_context.py`
  - `artifacts/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_context.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/letter_context.py tests/test_v8_format_letter_context.py && .venv/bin/ruff format app/modules/documents/letter_context.py tests/test_v8_format_letter_context.py && .venv/bin/ruff check app/modules/documents/letter_context.py tests/test_v8_format_letter_context.py`
  - `git diff --check -- backend/app/modules/documents/letter_context.py backend/tests/test_v8_format_letter_context.py tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01` all PASS; exact closure complete and non-closure respected.

## 090. FPMS-V8-FORMAT-LETTER-RENDER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-RENDER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Render a real readable Word with the required output name and content hash; no email send.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-RENDER-20260712-01.md`
  - `backend/app/modules/documents/letter_render_service.py`
  - `backend/tests/test_v8_format_letter_render.py`
  - `artifacts/FPMS-V8-FORMAT-LETTER-RENDER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_render.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/letter_render_service.py tests/test_v8_format_letter_render.py && .venv/bin/ruff format app/modules/documents/letter_render_service.py tests/test_v8_format_letter_render.py && .venv/bin/ruff check app/modules/documents/letter_render_service.py tests/test_v8_format_letter_render.py`
  - `git diff --check -- backend/app/modules/documents/letter_render_service.py backend/tests/test_v8_format_letter_render.py tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-RENDER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-RENDER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-RENDER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 091. FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Archive rendered Word as a new evidence version linked to latest IN source and handoff.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-RENDER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01.md`
  - `backend/app/modules/official_workflows/service.py`
  - `backend/tests/test_v8_format_letter_archive.py`
  - `artifacts/FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_archive.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_format_letter_archive.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_format_letter_archive.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_format_letter_archive.py`
  - `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_format_letter_archive.py tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 092. FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Existing handoff panel exposes the Chinese format-letter action on eligible IN source, not arbitrary OUT, and displays the actual archived version/hash.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01.md`
  - `frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-format-letter-in-source-ui.spec.ts`
  - `artifacts/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_pd_p1_letter_handoff_api.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-format-letter-in-source-ui.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/officialWorkflows/components/LetterHandoffPanel.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-format-letter-in-source-ui.spec.ts tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 093. FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Pure rule accepts explicit `0`; requires confirmed scoped approval for `0.7/0.85`; rejects missing/illegal/ambiguous values.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01.md`
  - `backend/app/modules/fees/fee_reduction.py`
  - `backend/tests/test_v8_fee_reduction_validator.py`
  - `artifacts/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_validator.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction.py tests/test_v8_fee_reduction_validator.py && .venv/bin/ruff format app/modules/fees/fee_reduction.py tests/test_v8_fee_reduction_validator.py && .venv/bin/ruff check app/modules/fees/fee_reduction.py tests/test_v8_fee_reduction_validator.py`
  - `git diff --check -- backend/app/modules/fees/fee_reduction.py backend/tests/test_v8_fee_reduction_validator.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01` all PASS; exact closure complete and non-closure respected.

## 094. FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Record/reuse one confirmed CASE or canonical APPLICANT_SET approval with source/snapshot evidence, ratio, fee/year scope and interval; reject mixed scope and hash/snapshot conflicts.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md`
  - `backend/app/modules/fees/fee_reduction_approval_service.py`
  - `backend/tests/test_v8_fee_reduction_approval_record.py`
  - `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_record.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction_approval_service.py tests/test_v8_fee_reduction_approval_record.py && .venv/bin/ruff format app/modules/fees/fee_reduction_approval_service.py tests/test_v8_fee_reduction_approval_record.py && .venv/bin/ruff check app/modules/fees/fee_reduction_approval_service.py tests/test_v8_fee_reduction_approval_record.py`
  - `git diff --check -- backend/app/modules/fees/fee_reduction_approval_service.py backend/tests/test_v8_fee_reduction_approval_record.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 095. FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: POST one approval and return its identifier; permission `Fee.Edit`; 201 create/200 idempotent/400 wrong case/409 conflict.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01.md`
  - `backend/app/modules/fees/fee_reduction_approval_schemas.py`
  - `backend/app/modules/fees/api.py`
  - `backend/tests/test_v8_fee_reduction_approval_create_api.py`
  - `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_create_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_create_api.py && .venv/bin/ruff format app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_create_api.py && .venv/bin/ruff check app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_create_api.py`
  - `git diff --check -- backend/app/modules/fees/fee_reduction_approval_schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_reduction_approval_create_api.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01` all PASS; exact closure complete and non-closure respected.

## 096. FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: Bodyless GET lists confirmed/current approvals for one case without inferring a ratio.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01.md`
  - `backend/app/modules/fees/fee_reduction_approval_schemas.py`
  - `backend/app/modules/fees/api.py`
  - `backend/tests/test_v8_fee_reduction_approval_list_api.py`
  - `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_list_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_list_api.py && .venv/bin/ruff format app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_list_api.py && .venv/bin/ruff check app/modules/fees/fee_reduction_approval_schemas.py app/modules/fees/api.py tests/test_v8_fee_reduction_approval_list_api.py`
  - `git diff --check -- backend/app/modules/fees/fee_reduction_approval_schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_reduction_approval_list_api.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01` all PASS; exact closure complete and non-closure respected.

## 097. FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Case edit records/selects approval evidence before enabling `0.7/0.85`, and shows source/scope in Chinese.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01.md`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-reduction-approval-case-edit.spec.ts`
  - `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-fee-reduction-approval-case-edit.spec.ts --workers=1`
  - `cd frontend && npx eslint src/api/fees.ts src/api/fees.types.ts src/modules/cases/pages/CaseEdit.vue --max-warnings 0`
  - `git diff --check -- frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/modules/cases/pages/CaseEdit.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-reduction-approval-case-edit.spec.ts tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 098. FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: Case POST rejects a missing/ambiguous reduction value; persists canonical `0` only when the request explicitly selects no reduction; `0.7/0.85` requires an existing applicant-scoped approval matching the submitted applicant composition and otherwise returns 409.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01.md`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_v8_case_create_fee_reduction.py`
  - `artifacts/FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_case_create_fee_reduction.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_create_fee_reduction.py && .venv/bin/ruff format app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_create_fee_reduction.py && .venv/bin/ruff check app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_create_fee_reduction.py`
  - `git diff --check -- backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_v8_case_create_fee_reduction.py tasks/postdemo/v8/FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01` all PASS; exact closure complete and non-closure respected.

## 099. FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: Case PUT rejects missing/ambiguous input, persists `0` only from an explicit no-reduction replacement with actor/time audit, and requires a matching confirmed approval for `0.7/0.85`; it never coerces unknown legacy data.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01.md`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_v8_case_update_fee_reduction.py`
  - `artifacts/FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_case_update_fee_reduction.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_update_fee_reduction.py && .venv/bin/ruff format app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_update_fee_reduction.py && .venv/bin/ruff check app/modules/cases/schemas.py app/modules/cases/service.py tests/test_v8_case_update_fee_reduction.py`
  - `git diff --check -- backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_v8_case_update_fee_reduction.py tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01` all PASS; exact closure complete and non-closure respected.

## 100. FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Create page starts unset and requires an explicit selection; it sends `0` only after the user selects no reduction, never sends `NONE/PARTIAL/FULL`, and explains that reduced ratios require recorded approval.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01.md`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-create-fee-reduction.spec.ts`
  - `artifacts/FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-create-fee-reduction.spec.ts --workers=1`
  - `cd frontend && npx eslint src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseCreate.vue --max-warnings 0`
  - `git diff --check -- frontend/src/api/cases.ts frontend/src/api/cases.types.ts frontend/src/modules/cases/pages/CaseCreate.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-create-fee-reduction.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 101. FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Edit page preserves unknown/unset legacy input as a blocking warning, displays/sends only an explicit canonical selection, and never coerces missing data to `0`.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01`
  - `FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01.md`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-edit-fee-reduction.spec.ts`
  - `artifacts/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-edit-fee-reduction.spec.ts --workers=1`
  - `cd frontend && npx eslint src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseEdit.vue --max-warnings 0`
  - `git diff --check -- frontend/src/api/cases.ts frontend/src/api/cases.types.ts frontend/src/modules/cases/pages/CaseEdit.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-edit-fee-reduction.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 102. FPMS-V8-FO-CONTRACTS-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-CONTRACTS-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-INTERFACE`
- Exact closure: Define obligation/line/status/source and command/result interface only.
- Non-closure: No persistence, business adapter, endpoint or UI.
- Canonical dependencies:
  - `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
  - `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
  - `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-CONTRACTS-20260712-01.md`
  - `backend/app/modules/fees/obligation_contracts.py`
  - `backend/tests/test_v8_fee_obligation_contracts.py`
  - `artifacts/FPMS-V8-FO-CONTRACTS-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_contracts.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_contracts.py tests/test_v8_fee_obligation_contracts.py && .venv/bin/ruff format app/modules/fees/obligation_contracts.py tests/test_v8_fee_obligation_contracts.py && .venv/bin/ruff check app/modules/fees/obligation_contracts.py tests/test_v8_fee_obligation_contracts.py`
  - `git diff --check -- backend/app/modules/fees/obligation_contracts.py backend/tests/test_v8_fee_obligation_contracts.py tasks/postdemo/v8/FPMS-V8-FO-CONTRACTS-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-CONTRACTS-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-CONTRACTS-20260712-01` all PASS; exact closure complete and non-closure respected.

## 103. FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Create/reuse/supersede one effective line by the frozen current identity key and append/reuse exactly one `FEE_OBLIGATION_RECOGNIZED` activity with `center_changes={}` in the same transaction; on SQLite uniqueness conflict reread the same source-event/fee-code/year identity; real notice wins over estimate.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01.md`
  - `backend/app/modules/fees/obligation_service.py`
  - `backend/tests/test_v8_fee_obligation_recognize.py`
  - `artifacts/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_recognize.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_recognize.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_recognize.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_recognize.py`
  - `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_recognize.py tasks/postdemo/v8/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 104. FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Read-only estimate returns candidates and creates no obligation/draft/activity.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01.md`
  - `backend/app/modules/fees/obligation_service.py`
  - `backend/tests/test_v8_fee_estimate_read_only.py`
  - `artifacts/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_estimate_read_only.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_estimate_read_only.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_estimate_read_only.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_estimate_read_only.py`
  - `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_estimate_read_only.py tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 105. FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: Existing official-fee preview endpoint accepts an explicit estimate context, labels the result ESTIMATE and never recognizes an obligation.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md`
  - `backend/app/modules/fees/schemas.py`
  - `backend/app/modules/fees/api.py`
  - `backend/tests/test_v8_fee_estimate_preview_api.py`
  - `artifacts/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_estimate_preview_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_fee_estimate_preview_api.py && .venv/bin/ruff format app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_fee_estimate_preview_api.py && .venv/bin/ruff check app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_fee_estimate_preview_api.py`
  - `git diff --check -- backend/app/modules/fees/schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_estimate_preview_api.py tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 106. FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-FE-ADAPTER`
- Exact closure: Type the explicit estimate context/result and preserve the server's ESTIMATE label, decimal strings and source metadata without creating a frontend obligation.
- Non-closure: No page behavior, server-state inference or backend change.
- Canonical dependencies:
  - `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01.md`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/api/contracts/v8_fee_estimate_preview.contract.ts`
  - `artifacts/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/api/fees.ts src/api/fees.types.ts src/api/contracts/v8_fee_estimate_preview.contract.ts --max-warnings 0`
  - `git diff --check -- frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/api/contracts/v8_fee_estimate_preview.contract.ts tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 107. FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Record `PAY/HOLD/ABANDON` as a distinct fact/activity; no draft is implied.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md`
  - `backend/app/modules/fees/obligation_service.py`
  - `backend/tests/test_v8_fee_obligation_instruction.py`
  - `artifacts/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_instruction.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_instruction.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_instruction.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_instruction.py`
  - `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_instruction.py tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 108. FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: One POST obligation-instruction endpoint using `Fee.Edit`; 200 idempotent, 409 non-actionable/conflicting instruction and no draft side effect.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01.md`
  - `backend/app/modules/fees/obligation_schemas.py`
  - `backend/app/modules/fees/api.py`
  - `backend/tests/test_v8_fee_obligation_instruction_api.py`
  - `artifacts/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_instruction_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_instruction_api.py && .venv/bin/ruff format app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_instruction_api.py && .venv/bin/ruff check app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_instruction_api.py`
  - `git diff --check -- backend/app/modules/fees/obligation_schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_obligation_instruction_api.py tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01` all PASS; exact closure complete and non-closure respected.

## 109. FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-FE-ADAPTER`
- Exact closure: Type the PAY/HOLD/ABANDON action/result and preserve server obligation/status identity.
- Non-closure: No page behavior, server-state inference or backend change.
- Canonical dependencies:
  - `FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01.md`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/api/contracts/v8_fee_obligation_instruction.contract.ts`
  - `artifacts/FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/api/fees.ts src/api/fees.types.ts src/api/contracts/v8_fee_obligation_instruction.contract.ts --max-warnings 0`
  - `git diff --check -- frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/api/contracts/v8_fee_obligation_instruction.contract.ts tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 110. FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Read one obligation with source, item lines and seven separated states; no status/amount inference or write.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md`
  - `backend/app/modules/fees/obligation_service.py`
  - `backend/tests/test_v8_fee_obligation_detail_read.py`
  - `artifacts/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_detail_read.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_detail_read.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_detail_read.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_detail_read.py`
  - `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_detail_read.py tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01` all PASS; exact closure complete and non-closure respected.

## 111. FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: One bodyless GET obligation-detail endpoint using `Fee.Read`; 200/401/403/404/409/422 semantics and no request body.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01.md`
  - `backend/app/modules/fees/obligation_schemas.py`
  - `backend/app/modules/fees/api.py`
  - `backend/tests/test_v8_fee_obligation_detail_api.py`
  - `artifacts/FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_detail_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_detail_api.py && .venv/bin/ruff format app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_detail_api.py && .venv/bin/ruff check app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_detail_api.py`
  - `git diff --check -- backend/app/modules/fees/obligation_schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_obligation_detail_api.py tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01` all PASS; exact closure complete and non-closure respected.

## 112. FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-FE-ADAPTER`
- Exact closure: Type/fetch one obligation detail, preserving decimal strings and separated states.
- Non-closure: No page behavior, server-state inference or backend change.
- Canonical dependencies:
  - `FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01.md`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/api/contracts/v8_fee_obligation_detail.contract.ts`
  - `artifacts/FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/api/fees.ts src/api/fees.types.ts src/api/contracts/v8_fee_obligation_detail.contract.ts --max-warnings 0`
  - `git diff --check -- frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/api/contracts/v8_fee_obligation_detail.contract.ts tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 113. FPMS-V8-FO-PREPARE-DRAFT-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-PREPARE-DRAFT-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Create/reuse downstream FeeDraft/FeeItem links only from an actionable obligation and policy, and append/reuse exactly one `FEE_DRAFT_CREATED` FEE activity with `center_changes={}` in the same transaction.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-PREPARE-DRAFT-20260712-01.md`
  - `backend/app/modules/fees/obligation_service.py`
  - `backend/tests/test_v8_fee_obligation_prepare_draft.py`
  - `artifacts/FPMS-V8-FO-PREPARE-DRAFT-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_prepare_draft.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_prepare_draft.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_prepare_draft.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_prepare_draft.py`
  - `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_prepare_draft.py tasks/postdemo/v8/FPMS-V8-FO-PREPARE-DRAFT-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-PREPARE-DRAFT-20260712-01` all PASS; exact closure complete and non-closure respected.

## 114. FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Link valid same-case payment evidence; payment and official evidence remain separate states.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01.md`
  - `backend/app/modules/fees/obligation_service.py`
  - `backend/tests/test_v8_fee_obligation_payment_evidence.py`
  - `artifacts/FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_payment_evidence.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_payment_evidence.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_payment_evidence.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_payment_evidence.py`
  - `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_payment_evidence.py tasks/postdemo/v8/FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 115. FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Generic FeeDraft service accepts an explicit obligation ID and calls `prepare_draft` only for actionable PAY instruction; it reuses the returned link/activity identity and never appends a second draft activity. Legacy unlinked draft stays historical.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01.md`
  - `backend/app/modules/fees/service.py`
  - `backend/tests/test_v8_generic_fee_draft_activity_adapter.py`
  - `artifacts/FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_generic_fee_draft_activity_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/service.py tests/test_v8_generic_fee_draft_activity_adapter.py && .venv/bin/ruff format app/modules/fees/service.py tests/test_v8_generic_fee_draft_activity_adapter.py && .venv/bin/ruff check app/modules/fees/service.py tests/test_v8_generic_fee_draft_activity_adapter.py`
  - `git diff --check -- backend/app/modules/fees/service.py backend/tests/test_v8_generic_fee_draft_activity_adapter.py tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 116. FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: Existing FeeDraft POST accepts/passes one optional `obligation_id`; 409 on missing/non-actionable/mismatched linkage and no partial draft.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01.md`
  - `backend/app/modules/fees/schemas.py`
  - `backend/app/modules/fees/api.py`
  - `backend/tests/test_v8_generic_fee_draft_obligation_api.py`
  - `artifacts/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_generic_fee_draft_obligation_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_generic_fee_draft_obligation_api.py && .venv/bin/ruff format app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_generic_fee_draft_obligation_api.py && .venv/bin/ruff check app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_generic_fee_draft_obligation_api.py`
  - `git diff --check -- backend/app/modules/fees/schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_generic_fee_draft_obligation_api.py tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 117. FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-FE-ADAPTER`
- Exact closure: Type the optional obligation linkage on generic draft creation without deriving source or amount.
- Non-closure: No page behavior, server-state inference or backend change.
- Canonical dependencies:
  - `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01.md`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/api/contracts/v8_fee_draft_obligation.contract.ts`
  - `artifacts/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/api/fees.ts src/api/fees.types.ts src/api/contracts/v8_fee_draft_obligation.contract.ts --max-warnings 0`
  - `git diff --check -- frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/api/contracts/v8_fee_draft_obligation.contract.ts tasks/postdemo/v8/FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 118. FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: FeeDraft create page reads explicit `obligation_id` from `/fees/drafts/new?obligation_id=...`, fetches source/instruction detail, and blocks manual draft unless status is PAY; it never guesses an obligation.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01`
  - `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01.md`
  - `frontend/src/modules/fees/pages/FeeDraftCreate.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-draft-obligation.spec.ts`
  - `artifacts/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-fee-draft-obligation.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/fees/pages/FeeDraftCreate.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/fees/pages/FeeDraftCreate.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-draft-obligation.spec.ts tasks/postdemo/v8/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 119. FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing grant instruction action records instruction on the exact sourced grant-year obligation.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
  - `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_v8_grant_instruction_obligation_adapter.py`
  - `artifacts/FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_instruction_obligation_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_v8_grant_instruction_obligation_adapter.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_v8_grant_instruction_obligation_adapter.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_v8_grant_instruction_obligation_adapter.py`
  - `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_instruction_obligation_adapter.py tasks/postdemo/v8/FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 120. FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing manual grant draft action calls `prepare_draft`, reuses its returned link/activity identity and never appends a second draft activity.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01.md`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_v8_grant_draft_obligation_adapter.py`
  - `artifacts/FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_draft_obligation_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_v8_grant_draft_obligation_adapter.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_v8_grant_draft_obligation_adapter.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_v8_grant_draft_obligation_adapter.py`
  - `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_draft_obligation_adapter.py tasks/postdemo/v8/FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 121. FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing annuity instruction action records instruction on the exact yearly obligation.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_annuity_instruction_obligation_adapter.py`
  - `artifacts/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_instruction_obligation_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_annuity_instruction_obligation_adapter.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_annuity_instruction_obligation_adapter.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_annuity_instruction_obligation_adapter.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_annuity_instruction_obligation_adapter.py tasks/postdemo/v8/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 122. FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing annuity draft generation calls `prepare_draft` per selected obligation, reuses each returned link/activity identity and never appends a second draft activity.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_annuity_draft_obligation_adapter.py`
  - `artifacts/FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_draft_obligation_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_annuity_draft_obligation_adapter.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_annuity_draft_obligation_adapter.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_annuity_draft_obligation_adapter.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_annuity_draft_obligation_adapter.py tasks/postdemo/v8/FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 123. FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Existing PayList creation appends one list activity linked to included obligation lines.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
  - `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_pay_list_create_activity_adapter.py`
  - `artifacts/FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_create_activity_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_pay_list_create_activity_adapter.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_pay_list_create_activity_adapter.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_pay_list_create_activity_adapter.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_pay_list_create_activity_adapter.py tasks/postdemo/v8/FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 124. FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: GovPayment registration links payment evidence and appends one payment activity.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_gov_payment_activity_adapter.py`
  - `artifacts/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_gov_payment_activity_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_gov_payment_activity_adapter.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_gov_payment_activity_adapter.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_gov_payment_activity_adapter.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_gov_payment_activity_adapter.py tasks/postdemo/v8/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 125. FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Official receipt/ticket verification changes only official-evidence state and appends its own activity.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_official_payment_evidence_activity_adapter.py`
  - `artifacts/FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_official_payment_evidence_activity_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_official_payment_evidence_activity_adapter.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_official_payment_evidence_activity_adapter.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_official_payment_evidence_activity_adapter.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_official_payment_evidence_activity_adapter.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 126. FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Freeze resolver semantic `APPLICATION_FEE_NOTICE`; a reviewed confirmed notice with exact due/source/item lines creates/reuses the application-fee obligation, while preview difference enters review. For a PCT case it applies exemptions only from confirmed RO/search/report evidence through the pure PCT policy, never from `case_type` alone. It does not activate the catalog row or create a draft.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-PCT-FEE-POLICY-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/semantics.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_application_fee_notice_obligation.py`
  - `artifacts/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_application_fee_notice_obligation.py tests/test_addgap_document_deadline_carrier.py tests/test_addgap_document_deadline_read_projection.py tests/test_addgap_document_deadline_create_api.py tests/test_addgap_document_deadline_update_api.py tests/test_addgap_legacy_deadline_task_sync.py tests/test_addgap_oa_deadline_fail_closed.py tests/test_addgap_document_deadline_impact_preview.py tests/test_addgap_document_wizard_deadline_backend.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_application_fee_notice_obligation.py && .venv/bin/ruff format app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_application_fee_notice_obligation.py && .venv/bin/ruff check app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_application_fee_notice_obligation.py`
  - `git diff --check -- backend/app/modules/documents/semantics.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_application_fee_notice_obligation.py tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 127. FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Freeze resolver semantic `FEE_REDUCTION_APPROVAL_NOTICE`; a reviewed confirmed notice records/reuses scoped approval evidence, while reference-only/unknown notices do nothing. It does not activate the catalog row, create an obligation/draft or change lifecycle state.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
  - `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/semantics.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_fee_reduction_approval_notice_adapter.py`
  - `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_notice_adapter.py tests/test_addgap_oa_subsequent_task_identity.py tests/test_addgap_notice_catalog_classification.py tests/test_addgap_notice_catalog_reference_gate.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_notice_grant_activation.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-notice-catalog-ui-clarity.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_fee_reduction_approval_notice_adapter.py && .venv/bin/ruff format app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_fee_reduction_approval_notice_adapter.py && .venv/bin/ruff check app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_fee_reduction_approval_notice_adapter.py`
  - `git diff --check -- backend/app/modules/documents/semantics.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_fee_reduction_approval_notice_adapter.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 128. FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Activate only `OFFICIAL_NOTICE_034 / 缴纳申请费通知书 / 200103` as executable `APPLICATION_FEE_NOTICE` with explicit-official-due policy; preserve the existing seven executable rows, leave every other IN row reference-only, seed idempotently, and prove the reviewed real create path reaches exactly one obligation. No status, task, reply or draft side effect.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01.md`
  - `backend/app/modules/documents/official_notice_catalog.py`
  - `backend/scripts/seed_dev.py`
  - `backend/tests/test_v8_application_fee_notice_activation.py`
  - `artifacts/FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_application_fee_notice_activation.py tests/test_addgap_oa_subsequent_task_identity.py tests/test_addgap_notice_catalog_classification.py tests/test_addgap_notice_catalog_reference_gate.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_notice_grant_activation.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-notice-catalog-ui-clarity.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_v8_application_fee_notice_activation.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_v8_application_fee_notice_activation.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_v8_application_fee_notice_activation.py`
  - `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/scripts/seed_dev.py backend/tests/test_v8_application_fee_notice_activation.py tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 129. FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Activate only `OFFICIAL_NOTICE_031 / 费用减缓审批通知书 / 200021` as executable `FEE_REDUCTION_APPROVAL_NOTICE`; preserve all earlier executable rows, leave every other IN row reference-only, seed idempotently, and prove reviewed source/scope/ratio evidence reaches exactly one approval. No deadline task, reply, obligation, draft or lifecycle side effect.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01.md`
  - `backend/app/modules/documents/official_notice_catalog.py`
  - `backend/scripts/seed_dev.py`
  - `backend/tests/test_v8_fee_reduction_approval_notice_activation.py`
  - `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_notice_activation.py tests/test_addgap_oa_subsequent_task_identity.py tests/test_addgap_notice_catalog_classification.py tests/test_addgap_notice_catalog_reference_gate.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_notice_grant_activation.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-notice-catalog-ui-clarity.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_v8_fee_reduction_approval_notice_activation.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_v8_fee_reduction_approval_notice_activation.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_v8_fee_reduction_approval_notice_activation.py`
  - `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/scripts/seed_dev.py backend/tests/test_v8_fee_reduction_approval_notice_activation.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 130. FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Registration notice creates only listed grant-year annuity lines, year, amount and due; no fixed combined fee code.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_v8_grant_year_annuity_obligation.py`
  - `artifacts/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_grant_year_annuity_obligation.py tests/test_addgap_grant_lineage_schema.py tests/test_addgap_grant_source_deadline.py tests/test_addgap_grant_auto_draft_gate.py tests/test_addgap_notice_grant_activation.py tests/test_addgap_grant_replacement_service.py tests/test_addgap_grant_replacement_api.py tests/test_addgap_grant_list_lineage_projection.py tests/test_addgap_grant_state_lineage_gate.py tests/test_b3_fee_linking.py tests/test_grant_fee_notice_task_creation.py tests/test_addgap_grant_preview_no_auto_draft.py tests/test_spec_alignment_e2e.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_grant_fee_worklist_api.py tests/test_grant_fee_state_machine_api.py tests/test_addgap_grant_mutation_lineage_gate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_document_api.py tests/test_addgap_document_create_atomicity.py tests/test_grant_fee_prereq_schema.py`
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
  - `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py`
  - `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_year_annuity_obligation.py tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 131. FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: A confirmed approval applies only from grant year through the tenth annual-fee year and only within its effective scope.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01.md`
  - `backend/app/modules/fees/fee_reduction.py`
  - `backend/tests/test_v8_annuity_first_ten_year_reduction_scope.py`
  - `artifacts/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_first_ten_year_reduction_scope.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction.py tests/test_v8_annuity_first_ten_year_reduction_scope.py && .venv/bin/ruff format app/modules/fees/fee_reduction.py tests/test_v8_annuity_first_ten_year_reduction_scope.py && .venv/bin/ruff check app/modules/fees/fee_reduction.py tests/test_v8_annuity_first_ten_year_reduction_scope.py`
  - `git diff --check -- backend/app/modules/fees/fee_reduction.py backend/tests/test_v8_annuity_first_ten_year_reduction_scope.py tasks/postdemo/v8/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 132. FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Calculate each yearly payable amount from full annual fee and eligible ratio; do not reduce late-fee base.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01.md`
  - `backend/app/modules/fees/obligation_service.py`
  - `backend/tests/test_v8_annuity_payable_amount.py`
  - `artifacts/FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_payable_amount.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_annuity_payable_amount.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_annuity_payable_amount.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_annuity_payable_amount.py`
  - `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_annuity_payable_amount.py tasks/postdemo/v8/FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 133. FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Annuity task becomes a sourced yearly obligation with type/year/due, scoped reduction/payable amount and instruction state.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_future_annuity_obligation.py`
  - `artifacts/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_future_annuity_obligation.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_future_annuity_obligation.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_future_annuity_obligation.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_future_annuity_obligation.py tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 134. FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Calculate 0 then 5/10/15/20/25 percent from full annual fee, max six months, notification bands strongest.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/late_fee.py`
  - `backend/tests/test_v8_annuity_late_fee.py`
  - `artifacts/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_late_fee.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/late_fee.py tests/test_v8_annuity_late_fee.py && .venv/bin/ruff format app/modules/fees/late_fee.py tests/test_v8_annuity_late_fee.py && .venv/bin/ruff check app/modules/fees/late_fee.py tests/test_v8_annuity_late_fee.py`
  - `git diff --check -- backend/app/modules/fees/late_fee.py backend/tests/test_v8_annuity_late_fee.py tasks/postdemo/v8/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 135. FPMS-V8-PCT-FEE-POLICY-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PCT-FEE-POLICY-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Implement the frozen CNIPA RO/search/report national-stage exemptions and per-fee domestic reduction; no whole-PCT flag.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PCT-FEE-POLICY-20260712-01.md`
  - `backend/app/modules/fees/pct_policy.py`
  - `backend/tests/test_v8_pct_fee_policy.py`
  - `artifacts/FPMS-V8-PCT-FEE-POLICY-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_pct_fee_policy.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/pct_policy.py tests/test_v8_pct_fee_policy.py && .venv/bin/ruff format app/modules/fees/pct_policy.py tests/test_v8_pct_fee_policy.py && .venv/bin/ruff check app/modules/fees/pct_policy.py tests/test_v8_pct_fee_policy.py`
  - `git diff --check -- backend/app/modules/fees/pct_policy.py backend/tests/test_v8_pct_fee_policy.py tasks/postdemo/v8/FPMS-V8-PCT-FEE-POLICY-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PCT-FEE-POLICY-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PCT-FEE-POLICY-20260712-01` all PASS; exact closure complete and non-closure respected.

## 136. FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Layout-design registration fee is 1000 yuan.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_layout_registration_fee_rule.py`
  - `artifacts/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_layout_registration_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_registration_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_registration_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_registration_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_registration_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 137. FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Layout-design registration reexamination request fee is 1000 yuan.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_layout_reexamination_fee_rule.py`
  - `artifacts/FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_layout_reexamination_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_reexamination_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_reexamination_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_reexamination_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_reexamination_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 138. FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Layout-design right-restoration request fee is 500 yuan.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_layout_restoration_fee_rule.py`
  - `artifacts/FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_layout_restoration_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_restoration_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_restoration_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_restoration_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_restoration_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 139. FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Layout-design bibliographic-change fee is 50 yuan.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_layout_bibliographic_change_fee_rule.py`
  - `artifacts/FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_layout_bibliographic_change_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_bibliographic_change_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_bibliographic_change_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_bibliographic_change_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_bibliographic_change_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 140. FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Layout-design extension request fee is 150 yuan.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_layout_extension_fee_rule.py`
  - `artifacts/FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_layout_extension_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_extension_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_extension_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_extension_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_extension_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 141. FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Nonvoluntary layout-design license request fee is 150 yuan.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_layout_nonvoluntary_license_fee_rule.py`
  - `artifacts/FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_layout_nonvoluntary_license_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_nonvoluntary_license_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_nonvoluntary_license_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_nonvoluntary_license_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_nonvoluntary_license_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 142. FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Layout-design remuneration adjudication fee is 150 yuan.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_layout_remuneration_adjudication_fee_rule.py`
  - `artifacts/FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_layout_remuneration_adjudication_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_remuneration_adjudication_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_remuneration_adjudication_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_remuneration_adjudication_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_remuneration_adjudication_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 143. FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Patent-term compensation request fee is 200 yuan per case.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_term_compensation_request_fee_rule.py`
  - `artifacts/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_term_compensation_request_fee_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_term_compensation_request_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_term_compensation_request_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_term_compensation_request_fee_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_term_compensation_request_fee_rule.py tasks/postdemo/v8/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 144. FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Compensation-period annuity is 8000 yuan per full year and no charge for a partial year.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_compensation_period_annuity_rule.py`
  - `artifacts/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_compensation_period_annuity_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_compensation_period_annuity_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_compensation_period_annuity_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_compensation_period_annuity_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_compensation_period_annuity_rule.py tasks/postdemo/v8/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 145. FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-RULE`
- Exact closure: Open-license implementation-period annuity reduction is 15%; choose the best benefit and never stack reductions.
- Non-closure: No second event/rate/policy, persistence adapter, endpoint, seed or UI.
- Canonical dependencies:
  - `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/tests/test_v8_open_license_annuity_reduction_rule.py`
  - `artifacts/FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_open_license_annuity_reduction_rule.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_open_license_annuity_reduction_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_open_license_annuity_reduction_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_open_license_annuity_reduction_rule.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_open_license_annuity_reduction_rule.py tasks/postdemo/v8/FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 146. FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `IC_LAYOUT_REGISTRATION_FILED`: reviewed final layout-registration submission evidence forms/reuses only `IC_LAYOUT_REGISTRATION_FEE` with `fee_year_key=0`.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
  - `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_ic_layout_registration_filed_obligation.py`
  - `artifacts/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_registration_filed_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_registration_filed_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_registration_filed_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_registration_filed_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_registration_filed_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 147. FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `IC_LAYOUT_REEXAM_REQUESTED`: reviewed final request submission forms/reuses only `IC_LAYOUT_REEXAM_REQUEST_FEE`; rejection or possible reexamination does not trigger it.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_ic_layout_reexamination_request_obligation.py`
  - `artifacts/FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_reexamination_request_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_reexamination_request_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_reexamination_request_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_reexamination_request_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_reexamination_request_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 148. FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `IC_LAYOUT_RESTORE_RIGHT_REQUESTED`: reviewed final restoration request forms/reuses only `IC_LAYOUT_RESTORE_RIGHT_FEE`; a loss-of-right notice alone does not trigger it.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_ic_layout_right_restoration_request_obligation.py`
  - `artifacts/FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_right_restoration_request_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_right_restoration_request_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_right_restoration_request_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_right_restoration_request_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_right_restoration_request_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 149. FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `IC_LAYOUT_BIBLIO_CHANGE_SUBMITTED`: each reviewed final submission source forms/reuses only its own `IC_LAYOUT_BIBLIO_CHANGE_FEE`.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_ic_layout_bibliographic_change_submission_obligation.py`
  - `artifacts/FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_bibliographic_change_submission_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_bibliographic_change_submission_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_bibliographic_change_submission_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_bibliographic_change_submission_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_bibliographic_change_submission_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 150. FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `IC_LAYOUT_EXTENSION_REQUESTED`: reviewed final extension request forms/reuses only `IC_LAYOUT_EXTENSION_REQUEST_FEE`; an approaching deadline does not trigger it.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_ic_layout_extension_request_obligation.py`
  - `artifacts/FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_extension_request_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_extension_request_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_extension_request_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_extension_request_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_extension_request_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 151. FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUESTED`: reviewed final request forms/reuses only `IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_FEE`.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_ic_layout_nonvoluntary_license_request_obligation.py`
  - `artifacts/FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_nonvoluntary_license_request_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_nonvoluntary_license_request_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_nonvoluntary_license_request_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_nonvoluntary_license_request_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_nonvoluntary_license_request_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 152. FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUESTED`: reviewed final request forms/reuses only `IC_LAYOUT_NONVOLUNTARY_LICENSE_REMUNERATION_ADJUDICATION_FEE`.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_ic_layout_remuneration_adjudication_request_obligation.py`
  - `artifacts/FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_remuneration_adjudication_request_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_remuneration_adjudication_request_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_remuneration_adjudication_request_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_remuneration_adjudication_request_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_remuneration_adjudication_request_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 153. FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `TERM_COMPENSATION_REQUESTED`: reviewed final compensation request forms/reuses only `CN_PATENT_TERM_COMPENSATION_REQUEST_FEE`; request date is the source date and an absent official due remains review-blocked rather than guessed.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_workflow_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_patent_term_compensation_request_obligation.py`
  - `artifacts/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_patent_term_compensation_request_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_patent_term_compensation_request_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_patent_term_compensation_request_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_patent_term_compensation_request_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_patent_term_compensation_request_obligation.py tasks/postdemo/v8/FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 154. FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `TERM_COMPENSATION_GRANTED`: reviewed official decision with explicit compensation period forms/reuses one obligation with one `CN_COMPENSATION_PERIOD_ANNUITY_FEE` line per complete year; no line for a partial year and 409 when the period/full-year facts are missing.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01`
  - `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01.md`
  - `backend/app/modules/documents/evidence_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_compensation_period_annuity_obligation.py`
  - `artifacts/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_compensation_period_annuity_obligation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py app/modules/documents/fee_linking_service.py tests/test_v8_compensation_period_annuity_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_service.py app/modules/documents/fee_linking_service.py tests/test_v8_compensation_period_annuity_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_service.py app/modules/documents/fee_linking_service.py tests/test_v8_compensation_period_annuity_obligation.py`
  - `git diff --check -- backend/app/modules/documents/evidence_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_compensation_period_annuity_obligation.py tasks/postdemo/v8/FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 155. FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: `OPEN_LICENSE_IMPLEMENTATION_PERIOD_CONFIRMED`: reviewed official evidence applies best-benefit non-stacked 15% treatment only to an existing ordinary annuity obligation inside the confirmed period, using recognize/supersede to replace effective lines; it never creates an annuity obligation.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`
  - `FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01`
  - `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01.md`
  - `backend/app/modules/documents/evidence_service.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_v8_open_license_annuity_obligation_adapter.py`
  - `artifacts/FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_open_license_annuity_obligation_adapter.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_service.py app/modules/documents/fee_linking_service.py tests/test_v8_open_license_annuity_obligation_adapter.py && .venv/bin/ruff format app/modules/documents/evidence_service.py app/modules/documents/fee_linking_service.py tests/test_v8_open_license_annuity_obligation_adapter.py && .venv/bin/ruff check app/modules/documents/evidence_service.py app/modules/documents/fee_linking_service.py tests/test_v8_open_license_annuity_obligation_adapter.py`
  - `git diff --check -- backend/app/modules/documents/evidence_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_open_license_annuity_obligation_adapter.py tasks/postdemo/v8/FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 156. FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only versioned official rate-book carrier and FeeRate compatibility link.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w4_official_rate_book.py`
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_v8_official_rate_book_schema.py`
  - `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_official_rate_book_schema.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w4_official_rate_book.py app/modules/fees/models.py tests/test_v8_official_rate_book_schema.py && .venv/bin/ruff format alembic/versions/v8_w4_official_rate_book.py app/modules/fees/models.py tests/test_v8_official_rate_book_schema.py && .venv/bin/ruff check alembic/versions/v8_w4_official_rate_book.py app/modules/fees/models.py tests/test_v8_official_rate_book_schema.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w4_official_rate_book.py backend/app/modules/fees/models.py backend/tests/test_v8_official_rate_book_schema.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 157. FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Activate a version only with CNIPA source snapshot, approval, effective interval and non-overlap; customer sheets never activate it.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md`
  - `backend/app/modules/fees/official_rate_book.py`
  - `backend/scripts/seed_dev.py`
  - `backend/tests/test_v8_official_rate_book_activation.py`
  - `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_official_rate_book_activation.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py scripts/seed_dev.py tests/test_v8_official_rate_book_activation.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py scripts/seed_dev.py tests/test_v8_official_rate_book_activation.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py scripts/seed_dev.py tests/test_v8_official_rate_book_activation.py`
  - `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/scripts/seed_dev.py backend/tests/test_v8_official_rate_book_activation.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 158. FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Correct only misclassified publication-print fee while preserving fee code/history.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01.md`
  - `backend/scripts/seed_dev.py`
  - `backend/tests/test_v8_official_fee_category_correction.py`
  - `artifacts/FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_official_fee_category_correction.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/seed_dev.py tests/test_v8_official_fee_category_correction.py && .venv/bin/ruff format scripts/seed_dev.py tests/test_v8_official_fee_category_correction.py && .venv/bin/ruff check scripts/seed_dev.py tests/test_v8_official_fee_category_correction.py`
  - `git diff --check -- backend/scripts/seed_dev.py backend/tests/test_v8_official_fee_category_correction.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 159. FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only `t_pay_list_export_artifact` with kind/status/hash/template version/path, generated identity and nullable official-site acceptance evidence/time; no payment or ticket state.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_w5_pay_list_export_artifact.py`
  - `backend/app/modules/annuity/models.py`
  - `backend/tests/test_v8_pay_list_export_artifact_schema.py`
  - `artifacts/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_schema.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py && .venv/bin/ruff format alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py && .venv/bin/ruff check alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_w5_pay_list_export_artifact.py backend/app/modules/annuity/models.py backend/tests/test_v8_pay_list_export_artifact_schema.py tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 160. FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Internal `.xlsx` creates INTERNAL_XLSX artifact/activity and returns blob without proving official upload.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/app/modules/annuity/export_excel.py`
  - `backend/tests/test_v8_internal_pay_list_export.py`
  - `artifacts/FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_internal_pay_list_export.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py app/modules/annuity/export_excel.py tests/test_v8_internal_pay_list_export.py && .venv/bin/ruff format app/modules/annuity/service.py app/modules/annuity/export_excel.py tests/test_v8_internal_pay_list_export.py && .venv/bin/ruff check app/modules/annuity/service.py app/modules/annuity/export_excel.py tests/test_v8_internal_pay_list_export.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/app/modules/annuity/export_excel.py backend/tests/test_v8_internal_pay_list_export.py tasks/postdemo/v8/FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 161. FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-ADAPTER`
- Exact closure: Mark-paid relies on payment evidence, not internal/official export; old EXPORTED rows remain readable only.
- Non-closure: No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor.
- Canonical dependencies:
  - `FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_pay_list_payment_export_decouple.py`
  - `artifacts/FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_payment_export_decouple.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_pay_list_payment_export_decouple.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_pay_list_payment_export_decouple.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_pay_list_payment_export_decouple.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_pay_list_payment_export_decouple.py tasks/postdemo/v8/FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 162. FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: PayList detail returns internal artifacts, official workbook gate/status and payment facts separately.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01.md`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_v8_pay_list_export_artifact_read.py`
  - `artifacts/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_read.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_pay_list_export_artifact_read.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_pay_list_export_artifact_read.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_pay_list_export_artifact_read.py`
  - `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_pay_list_export_artifact_read.py tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01` all PASS; exact closure complete and non-closure respected.

## 163. FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-FE-ADAPTER`
- Exact closure: Map the separated PayList facts without deriving official status from header status.
- Non-closure: No page behavior, server-state inference or backend change.
- Canonical dependencies:
  - `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01.md`
  - `frontend/src/api/govPayments.ts`
  - `frontend/src/api/govPayments.types.ts`
  - `frontend/src/api/contracts/v8_pay_list_boundary.contract.ts`
  - `artifacts/FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/api/govPayments.ts src/api/govPayments.types.ts src/api/contracts/v8_pay_list_boundary.contract.ts --max-warnings 0`
  - `git diff --check -- frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts frontend/src/api/contracts/v8_pay_list_boundary.contract.ts tasks/postdemo/v8/FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 164. FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: PayList detail has separate internal export, gated official workbook, payment and evidence sections in Chinese.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01.md`
  - `frontend/src/modules/annuity/pages/PayListDetail.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-pay-list-boundary-ui.spec.ts`
  - `artifacts/FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-pay-list-boundary-ui.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/annuity/pages/PayListDetail.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/annuity/pages/PayListDetail.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-pay-list-boundary-ui.spec.ts tasks/postdemo/v8/FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 165. FPMS-V8-DECISION-GATE-CARRIER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CARRIER-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SCHEMA`
- Exact closure: Add only append-only `t_customer_decision_gate`, nullable unique current identity, supersedes/idempotency identities and source/scope/status audit fields.
- Non-closure: No backfill, service, endpoint, seed, UI or second table/carrier.
- Canonical dependencies:
  - `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CARRIER-20260712-01.md`
  - `backend/alembic/versions/v8_post_w1_customer_decision_gate.py`
  - `backend/app/modules/system/models.py`
  - `backend/tests/test_v8_customer_decision_gate_schema.py`
  - `artifacts/FPMS-V8-DECISION-GATE-CARRIER-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_customer_decision_gate_schema.py`
  - `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_post_w1_customer_decision_gate.py app/modules/system/models.py tests/test_v8_customer_decision_gate_schema.py && .venv/bin/ruff format alembic/versions/v8_post_w1_customer_decision_gate.py app/modules/system/models.py tests/test_v8_customer_decision_gate_schema.py && .venv/bin/ruff check alembic/versions/v8_post_w1_customer_decision_gate.py app/modules/system/models.py tests/test_v8_customer_decision_gate_schema.py`
  - `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
  - `git diff --check -- backend/alembic/versions/v8_post_w1_customer_decision_gate.py backend/app/modules/system/models.py backend/tests/test_v8_customer_decision_gate_schema.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CARRIER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-CARRIER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-CARRIER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 166. FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Atomically confirm/revoke/reuse one frozen gate decision, supersede the former current row and reject idempotency/payload/current-identity conflicts; no commit.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01.md`
  - `backend/app/modules/system/decision_gate_service.py`
  - `backend/tests/test_v8_decision_gate_record_service.py`
  - `artifacts/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_record_service.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_record_service.py && .venv/bin/ruff format app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_record_service.py && .venv/bin/ruff check app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_record_service.py`
  - `git diff --check -- backend/app/modules/system/decision_gate_service.py backend/tests/test_v8_decision_gate_record_service.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 167. FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Resolve exactly one current effective global/case/form decision and fail closed on absence, revocation, future date, scope mismatch or corrupt multiplicity.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md`
  - `backend/app/modules/system/decision_gate_service.py`
  - `backend/tests/test_v8_decision_gate_read_service.py`
  - `artifacts/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_read_service.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_read_service.py && .venv/bin/ruff format app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_read_service.py && .venv/bin/ruff check app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_read_service.py`
  - `git diff --check -- backend/app/modules/system/decision_gate_service.py backend/tests/test_v8_decision_gate_read_service.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 168. FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: One POST confirmation endpoint using `SystemParam.Edit`; 201 new/200 idempotent and 400/401/403/409/422 semantics; no second endpoint.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01.md`
  - `backend/app/modules/system/decision_gate_schemas.py`
  - `backend/app/modules/system/api.py`
  - `backend/tests/test_v8_decision_gate_confirm_api.py`
  - `artifacts/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_confirm_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_confirm_api.py && .venv/bin/ruff format app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_confirm_api.py && .venv/bin/ruff check app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_confirm_api.py`
  - `git diff --check -- backend/app/modules/system/decision_gate_schemas.py backend/app/modules/system/api.py backend/tests/test_v8_decision_gate_confirm_api.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01` all PASS; exact closure complete and non-closure respected.

## 169. FPMS-V8-DECISION-GATE-LIST-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: One bodyless GET audit endpoint using `SystemParam.Read`, returning persisted source/version/scope/status without interpreting business behavior.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md`
  - `backend/app/modules/system/decision_gate_schemas.py`
  - `backend/app/modules/system/api.py`
  - `backend/tests/test_v8_decision_gate_list_api.py`
  - `artifacts/FPMS-V8-DECISION-GATE-LIST-API-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_list_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_list_api.py && .venv/bin/ruff format app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_list_api.py && .venv/bin/ruff check app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_list_api.py`
  - `git diff --check -- backend/app/modules/system/decision_gate_schemas.py backend/app/modules/system/api.py backend/tests/test_v8_decision_gate_list_api.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-LIST-API-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-LIST-API-20260712-01` all PASS; exact closure complete and non-closure respected.

## 252. FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Read-only report classifies legacy state/evidence conflicts without changing data.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-LC-CASE-OPENED-20260712-01`
  - `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
  - `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
  - `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
  - `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
  - `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
  - `FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01`
  - `FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01.md`
  - `backend/scripts/audit_v8_legacy_state.py`
  - `backend/tests/test_v8_legacy_state_preflight.py`
  - `artifacts/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_state_preflight.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/audit_v8_legacy_state.py tests/test_v8_legacy_state_preflight.py && .venv/bin/ruff format scripts/audit_v8_legacy_state.py tests/test_v8_legacy_state_preflight.py && .venv/bin/ruff check scripts/audit_v8_legacy_state.py tests/test_v8_legacy_state_preflight.py`
  - `git diff --check -- backend/scripts/audit_v8_legacy_state.py backend/tests/test_v8_legacy_state_preflight.py tasks/postdemo/v8/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01` all PASS; exact closure complete and non-closure respected.

## 253. FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Backfill only deterministic legacy states as `LEGACY_IMPORT/LEGACY_UNVERIFIED`; old GRANTED never becomes patent in force.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01.md`
  - `backend/scripts/backfill_v8_lifecycle.py`
  - `backend/tests/test_v8_legacy_lifecycle_import.py`
  - `artifacts/FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_lifecycle_import.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/backfill_v8_lifecycle.py tests/test_v8_legacy_lifecycle_import.py && .venv/bin/ruff format scripts/backfill_v8_lifecycle.py tests/test_v8_legacy_lifecycle_import.py && .venv/bin/ruff check scripts/backfill_v8_lifecycle.py tests/test_v8_legacy_lifecycle_import.py`
  - `git diff --check -- backend/scripts/backfill_v8_lifecycle.py backend/tests/test_v8_legacy_lifecycle_import.py tasks/postdemo/v8/FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01` all PASS; exact closure complete and non-closure respected.

## 254. FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Create unverified versions for unambiguous attachments; role/current conflicts remain unresolved.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-CONTRACTS-20260712-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
  - `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01.md`
  - `backend/scripts/backfill_v8_document_evidence.py`
  - `backend/tests/test_v8_legacy_document_evidence_import.py`
  - `artifacts/FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_document_evidence_import.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/backfill_v8_document_evidence.py tests/test_v8_legacy_document_evidence_import.py && .venv/bin/ruff format scripts/backfill_v8_document_evidence.py tests/test_v8_legacy_document_evidence_import.py && .venv/bin/ruff check scripts/backfill_v8_document_evidence.py tests/test_v8_legacy_document_evidence_import.py`
  - `git diff --check -- backend/scripts/backfill_v8_document_evidence.py backend/tests/test_v8_legacy_document_evidence_import.py tasks/postdemo/v8/FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01` all PASS; exact closure complete and non-closure respected.

## 255. FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Map explicit no-reduction `0`; map `0.7/0.85` only with source/scope; never coerce missing/invalid to zero.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01.md`
  - `backend/scripts/backfill_v8_fee_reduction.py`
  - `backend/tests/test_v8_legacy_fee_reduction_import.py`
  - `artifacts/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_fee_reduction_import.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/backfill_v8_fee_reduction.py tests/test_v8_legacy_fee_reduction_import.py && .venv/bin/ruff format scripts/backfill_v8_fee_reduction.py tests/test_v8_legacy_fee_reduction_import.py && .venv/bin/ruff check scripts/backfill_v8_fee_reduction.py tests/test_v8_legacy_fee_reduction_import.py`
  - `git diff --check -- backend/scripts/backfill_v8_fee_reduction.py backend/tests/test_v8_legacy_fee_reduction_import.py tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01` all PASS; exact closure complete and non-closure respected.

## 256. FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Link old draft/payment history only when same case/source/fee/year is unambiguous; do not manufacture obligation.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01`
  - `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
  - `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01.md`
  - `backend/scripts/backfill_v8_fee_truth.py`
  - `backend/tests/test_v8_legacy_fee_truth_link.py`
  - `artifacts/FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_fee_truth_link.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/backfill_v8_fee_truth.py tests/test_v8_legacy_fee_truth_link.py && .venv/bin/ruff format scripts/backfill_v8_fee_truth.py tests/test_v8_legacy_fee_truth_link.py && .venv/bin/ruff check scripts/backfill_v8_fee_truth.py tests/test_v8_legacy_fee_truth_link.py`
  - `git diff --check -- backend/scripts/backfill_v8_fee_truth.py backend/tests/test_v8_legacy_fee_truth_link.py tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01` all PASS; exact closure complete and non-closure respected.

## 257. FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Read-only comparison reports projection/version/fee differences and accepts only classified conflicts.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01.md`
  - `backend/scripts/audit_v8_dual_read.py`
  - `backend/tests/test_v8_dual_read_reconciliation.py`
  - `artifacts/FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_dual_read_reconciliation.py`
  - `cd backend && .venv/bin/ruff check --fix scripts/audit_v8_dual_read.py tests/test_v8_dual_read_reconciliation.py && .venv/bin/ruff format scripts/audit_v8_dual_read.py tests/test_v8_dual_read_reconciliation.py && .venv/bin/ruff check scripts/audit_v8_dual_read.py tests/test_v8_dual_read_reconciliation.py`
  - `git diff --check -- backend/scripts/audit_v8_dual_read.py backend/tests/test_v8_dual_read_reconciliation.py tasks/postdemo/v8/FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 258. FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01.md`
- Owner role: Tester / monitor
- Profile: `TC-QA`
- Exact closure: After imports and dual-read reconciliation, static test permits legacy status write only in lifecycle projection and explicit legacy import.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
  - `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
  - `FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01`
  - `FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01.md`
  - `backend/tests/test_v8_direct_case_status_write_gate.py`
  - `artifacts/FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_direct_case_status_write_gate.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_direct_case_status_write_gate.py && .venv/bin/ruff format tests/test_v8_direct_case_status_write_gate.py && .venv/bin/ruff check tests/test_v8_direct_case_status_write_gate.py`
  - `git diff --check -- backend/tests/test_v8_direct_case_status_write_gate.py tasks/postdemo/v8/FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 259. FPMS-V8-OVERLAY-CONTRACTS-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-CONTRACTS-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-INTERFACE`
- Exact closure: Freeze center snapshot, milestone, document, task, fee, warnings, gates, conflicts and cursor schemas.
- Non-closure: No persistence, business adapter, endpoint or UI.
- Canonical dependencies:
  - `FPMS-V8-LC-CONTRACTS-20260712-01`
  - `FPMS-V8-DE-CONTRACTS-20260712-01`
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-CONTRACTS-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_overlay_schemas.py`
  - `backend/tests/test_v8_lifecycle_overlay_contracts.py`
  - `artifacts/FPMS-V8-OVERLAY-CONTRACTS-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_contracts.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_schemas.py tests/test_v8_lifecycle_overlay_contracts.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_schemas.py tests/test_v8_lifecycle_overlay_contracts.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_schemas.py tests/test_v8_lifecycle_overlay_contracts.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_overlay_schemas.py backend/tests/test_v8_lifecycle_overlay_contracts.py tasks/postdemo/v8/FPMS-V8-OVERLAY-CONTRACTS-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-CONTRACTS-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-CONTRACTS-20260712-01` all PASS; exact closure complete and non-closure respected.

## 260. FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Read one case/revision and central changes from activity ledger with no write.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01`
  - `FPMS-V8-OVERLAY-CONTRACTS-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_overlay_service.py`
  - `backend/tests/test_v8_lifecycle_overlay_center.py`
  - `artifacts/FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_center.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_center.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_center.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_center.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_lifecycle_overlay_center.py tasks/postdemo/v8/FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01` all PASS; exact closure complete and non-closure respected.

## 261. FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Bulk attach exact document evidence/work package/task facts by activity IDs.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DE-CONTRACTS-20260712-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
  - `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
  - `FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01`
  - `FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_overlay_service.py`
  - `backend/tests/test_v8_lifecycle_overlay_documents.py`
  - `artifacts/FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_documents.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_documents.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_documents.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_documents.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_lifecycle_overlay_documents.py tasks/postdemo/v8/FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01` all PASS; exact closure complete and non-closure respected.

## 262. FPMS-V8-OVERLAY-FEE-JOIN-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-FEE-JOIN-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Bulk attach obligation/instruction/draft/list/payment/evidence facts by activity IDs.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
  - `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
  - `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`
  - `FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-FEE-JOIN-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_overlay_service.py`
  - `backend/tests/test_v8_lifecycle_overlay_fees.py`
  - `artifacts/FPMS-V8-OVERLAY-FEE-JOIN-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_fees.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_fees.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_fees.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_fees.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_lifecycle_overlay_fees.py tasks/postdemo/v8/FPMS-V8-OVERLAY-FEE-JOIN-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-FEE-JOIN-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-FEE-JOIN-20260712-01` all PASS; exact closure complete and non-closure respected.

## 263. FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: Attach the eight applicable persisted gate states/sources/scopes, including unresolved reasons, without altering any business state.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-OVERLAY-FEE-JOIN-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_overlay_service.py`
  - `backend/tests/test_v8_lifecycle_overlay_decision_gates.py`
  - `artifacts/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_decision_gates.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_decision_gates.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_decision_gates.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_decision_gates.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_lifecycle_overlay_decision_gates.py tasks/postdemo/v8/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01` all PASS; exact closure complete and non-closure respected.

## 264. FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-SERVICE`
- Exact closure: `sequence > after` and `<= as_of_revision`, ascending `limit+1`, stable next cursor; 121 rows across three pages without loss/duplication.
- Non-closure: No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01.md`
  - `backend/app/modules/cases/lifecycle_overlay_service.py`
  - `backend/tests/test_v8_lifecycle_overlay_pagination.py`
  - `artifacts/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_pagination.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_pagination.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_pagination.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_pagination.py`
  - `git diff --check -- backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_lifecycle_overlay_pagination.py tasks/postdemo/v8/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01` all PASS; exact closure complete and non-closure respected.

## 265. FPMS-V8-OVERLAY-HTTP-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-HTTP-20260712-01.md`
- Owner role: Backend Developer / worker
- Profile: `TC-API`
- Exact closure: Bodyless GET `/cases/{case_id}/lifecycle-overlay`; permissions as four function parameters; no router edit.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-HTTP-20260712-01.md`
  - `backend/app/modules/cases/api.py`
  - `backend/tests/test_v8_lifecycle_overlay_api.py`
  - `artifacts/FPMS-V8-OVERLAY-HTTP-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_api.py`
  - `cd backend && .venv/bin/ruff check --fix app/modules/cases/api.py tests/test_v8_lifecycle_overlay_api.py && .venv/bin/ruff format app/modules/cases/api.py tests/test_v8_lifecycle_overlay_api.py && .venv/bin/ruff check app/modules/cases/api.py tests/test_v8_lifecycle_overlay_api.py`
  - `git diff --check -- backend/app/modules/cases/api.py backend/tests/test_v8_lifecycle_overlay_api.py tasks/postdemo/v8/FPMS-V8-OVERLAY-HTTP-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-HTTP-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-HTTP-20260712-01` all PASS; exact closure complete and non-closure respected.

## 266. FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-FE-ADAPTER`
- Exact closure: Dedicated typed adapter; preserve decimal strings and server associations.
- Non-closure: No page behavior, server-state inference or backend change.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-HTTP-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01.md`
  - `frontend/src/api/lifecycleOverlay.ts`
  - `frontend/src/api/lifecycleOverlay.types.ts`
  - `frontend/src/api/contracts/v8_lifecycle_overlay.contract.ts`
  - `artifacts/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01/**`
- Required verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/api/lifecycleOverlay.ts src/api/lifecycleOverlay.types.ts src/api/contracts/v8_lifecycle_overlay.contract.ts --max-warnings 0`
  - `git diff --check -- frontend/src/api/lifecycleOverlay.ts frontend/src/api/lifecycleOverlay.types.ts frontend/src/api/contracts/v8_lifecycle_overlay.contract.ts tasks/postdemo/v8/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 267. FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Replace `CaseFeesTab`'s fixed `FILING_ACCEPTED` request with an explicit user-selected estimate context; display ESTIMATE separately from real overlay obligations and never infer a draft/payment.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`
  - `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01.md`
  - `frontend/src/modules/cases/components/CaseFeesTab.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-estimate-obligation.spec.ts`
  - `artifacts/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-fees-estimate-obligation.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/cases/components/CaseFeesTab.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/CaseFeesTab.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-estimate-obligation.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01` all PASS; exact closure complete and non-closure respected.

## 268. FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Case fees tab records PAY/HOLD/ABANDON on a real obligation, shows the fact separately, and after PAY exposes exact navigation `/fees/drafts/new?obligation_id=<server-id>`; it never creates a draft automatically.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01.md`
  - `frontend/src/modules/cases/components/CaseFeesTab.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts`
  - `artifacts/FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-fees-instruction.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/cases/components/CaseFeesTab.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/CaseFeesTab.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 269. FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Render business/official/legal state and confirmed center changes only.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01.md`
  - `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
  - `artifacts/FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-overlay-center-lane.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/cases/components/LifecycleCenterLane.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/LifecycleCenterLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts tasks/postdemo/v8/FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 270. FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Render document role/version/derivation/package/submission/receipt facts only.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01.md`
  - `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
  - `artifacts/FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-overlay-document-lane.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/cases/components/DocumentEvidenceLane.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/DocumentEvidenceLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts tasks/postdemo/v8/FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 271. FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Render GOV/SERVICE obligation and seven separated fee states only.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01.md`
  - `frontend/src/modules/cases/components/FeeObligationLane.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`
  - `artifacts/FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-overlay-fee-lane.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/cases/components/FeeObligationLane.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/FeeObligationLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts tasks/postdemo/v8/FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 272. FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Compose left document, centered lifecycle and right fee lanes; replace CaseStepper display on this page without deleting the legacy component.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01.md`
  - `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts`
  - `artifacts/FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-three-lane.spec.ts --workers=1`
  - `cd frontend && npm run typecheck`
  - `cd frontend && npx eslint src/modules/cases/components/CaseLifecycleOverlay.vue src/modules/cases/pages/CaseDetail.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/pages/CaseDetail.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts tasks/postdemo/v8/FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01` all PASS; exact closure complete and non-closure respected.

## 273. FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Show unverified, customer gate, conflict and reference-only reasons in Simplified Chinese.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01.md`
  - `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`
  - `artifacts/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-gates-warnings.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/cases/components/CaseLifecycleOverlay.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/CaseLifecycleOverlay.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts tasks/postdemo/v8/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 274. FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01.md`
- Owner role: Frontend Developer / worker
- Profile: `TC-UI`
- Exact closure: Load more using the first revision, next cursor and deduplication; never claim complete history while `has_more`.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Canonical dependencies:
  - `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01.md`
  - `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
  - `artifacts/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-overlay-cursor.spec.ts --workers=1`
  - `cd frontend && npx eslint src/modules/cases/components/CaseLifecycleOverlay.vue --max-warnings 0`
  - `git diff --check -- frontend/src/modules/cases/components/CaseLifecycleOverlay.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts tasks/postdemo/v8/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01` all PASS; exact closure complete and non-closure respected.

## 275. FPMS-V8-LIVE-FIXTURE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md`
- Owner role: Tester / monitor
- Profile: `TC-QA`
- Exact closure: Create dedicated live fixture with >100 activities, all lanes, gates/conflicts/unverified facts; do not modify shared P1 live seed.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
  - `FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
  - `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
  - `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
  - `FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py`
  - `backend/tests/test_v8_overlay_live_seed.py`
  - `artifacts/FPMS-V8-LIVE-FIXTURE-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_overlay_live_seed.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_overlay_live_seed.py && .venv/bin/ruff format tests/test_v8_overlay_live_seed.py && .venv/bin/ruff check tests/test_v8_overlay_live_seed.py`
  - `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py backend/tests/test_v8_overlay_live_seed.py tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LIVE-FIXTURE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LIVE-FIXTURE-20260712-01` all PASS; exact closure complete and non-closure respected.

## 276. FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01.md`
- Owner role: Tester / monitor
- Profile: `TC-QA`
- Exact closure: Real login/API/Vite case path, no route fulfillment, verifies three lanes and stable three-page cursor.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - `FPMS-V8-LIVE-FIXTURE-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01.md`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
  - `artifacts/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-lifecycle-overlay-live.spec.ts --workers=1`
  - `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts tasks/postdemo/v8/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01` all PASS; exact closure complete and non-closure respected.

## 277. FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01.md`
- Owner role: Tester / monitor
- Profile: `TC-QA`
- Exact closure: Real path proves internal export does not imply official upload and payment remains distinct.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - `FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`
  - `FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01.md`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-pay-list-boundary-live.spec.ts`
  - `artifacts/FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01/**`
- Required verification:
  - `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-pay-list-boundary-live.spec.ts --workers=1`
  - `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-pay-list-boundary-live.spec.ts tasks/postdemo/v8/FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01` all PASS; exact closure complete and non-closure respected.

## 279. FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01.md`
- Owner role: Tester / monitor
- Profile: `TC-QA`
- Exact closure: Run only the frozen non-gated V8-to-Tasks01–70 targeted regression matrix and report failures; no product fixes.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
  - `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
  - `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
  - `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
  - `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
  - `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
  - `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
  - `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
  - `FPMS-V8-LC-CONTRACTS-20260712-01`
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-CASE-OPENED-20260712-01`
  - `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
  - `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
  - `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
  - `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-DE-CONTRACTS-20260712-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
  - `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
  - `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
  - `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
  - `FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
  - `FPMS-V8-DE-REVIEW-UI-20260712-01`
  - `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01`
  - `FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01`
  - `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01`
  - `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`
  - `FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`
  - `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
  - `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
  - `FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01`
  - `FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01`
  - `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01`
  - `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
  - `FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01`
  - `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
  - `FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01`
  - `FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01`
  - `FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-RENDER-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01`
  - `FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01`
  - `FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01`
  - `FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01`
  - `FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01`
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`
  - `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
  - `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
  - `FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`
  - `FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
  - `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`
  - `FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01`
  - `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01`
  - `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`
  - `FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`
  - `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`
  - `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`
  - `FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01`
  - `FPMS-V8-PCT-FEE-POLICY-20260712-01`
  - `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01`
  - `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01`
  - `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01`
  - `FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01`
  - `FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
  - `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
  - `FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01`
  - `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
  - `FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01`
  - `FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01`
  - `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01`
  - `FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`
  - `FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01`
  - `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`
  - `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`
  - `FPMS-V8-DECISION-GATE-LIST-API-20260712-01`
  - `FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01`
  - `FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01`
  - `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01`
  - `FPMS-V8-OVERLAY-CONTRACTS-20260712-01`
  - `FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01`
  - `FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01`
  - `FPMS-V8-OVERLAY-FEE-JOIN-20260712-01`
  - `FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`
  - `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`
  - `FPMS-V8-OVERLAY-HTTP-20260712-01`
  - `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01`
  - `FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
  - `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
  - `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
  - `FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01.md`
  - `backend/tests/test_v8_foundation_inherited_regression_matrix_contract.py`
  - `artifacts/FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01/**`
- Required verification:
  - `cd backend && .venv/bin/pytest -q tests/test_v8_foundation_inherited_regression_matrix_contract.py`
  - `cd backend && .venv/bin/ruff check --fix tests/test_v8_foundation_inherited_regression_matrix_contract.py && .venv/bin/ruff format tests/test_v8_foundation_inherited_regression_matrix_contract.py && .venv/bin/ruff check tests/test_v8_foundation_inherited_regression_matrix_contract.py`
  - `git diff --check -- backend/tests/test_v8_foundation_inherited_regression_matrix_contract.py artifacts/FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01/** tasks/postdemo/v8/FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01` all PASS; exact closure complete and non-closure respected.

## 280. FPMS-V8-FOUNDATION-CLOSE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md`
- Owner role: Independent Reviewer / explorer
- Profile: `TC-QA`
- Exact closure: Foundation-only QA close: verify every other foundation task/evidence and inherited regression mapping, classify every omitted customer lane as unresolved/confirmed-pending/activated/prior-PASS, and publish residuals without product fixes or any repo-wide/release check. It must not claim full V8 completion.
- Non-closure: No product fix, schema change or test-assertion weakening.
- Canonical dependencies:
  - `FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
  - `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
  - `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
  - `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
  - `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
  - `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
  - `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
  - `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
  - `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
  - `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
  - `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
  - `FPMS-V8-LC-CONTRACTS-20260712-01`
  - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
  - `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
  - `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
  - `FPMS-V8-LC-CASE-OPENED-20260712-01`
  - `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
  - `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
  - `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
  - `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
  - `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
  - `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
  - `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`
  - `FPMS-V8-DE-CONTRACTS-20260712-01`
  - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
  - `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
  - `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
  - `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
  - `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
  - `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
  - `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
  - `FPMS-V8-DE-REVIEW-API-20260712-01`
  - `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
  - `FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
  - `FPMS-V8-DE-REVIEW-UI-20260712-01`
  - `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
  - `FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01`
  - `FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01`
  - `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
  - `FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01`
  - `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`
  - `FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`
  - `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
  - `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
  - `FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01`
  - `FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01`
  - `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01`
  - `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
  - `FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01`
  - `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
  - `FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01`
  - `FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01`
  - `FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-RENDER-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01`
  - `FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01`
  - `FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01`
  - `FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01`
  - `FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01`
  - `FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01`
  - `FPMS-V8-FO-CONTRACTS-20260712-01`
  - `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
  - `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`
  - `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
  - `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
  - `FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`
  - `FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01`
  - `FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
  - `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`
  - `FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01`
  - `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01`
  - `FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01`
  - `FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01`
  - `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01`
  - `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`
  - `FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`
  - `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`
  - `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`
  - `FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01`
  - `FPMS-V8-PCT-FEE-POLICY-20260712-01`
  - `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01`
  - `FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01`
  - `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01`
  - `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01`
  - `FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01`
  - `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01`
  - `FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01`
  - `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
  - `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
  - `FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01`
  - `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
  - `FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01`
  - `FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01`
  - `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01`
  - `FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`
  - `FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01`
  - `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`
  - `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
  - `FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`
  - `FPMS-V8-DECISION-GATE-LIST-API-20260712-01`
  - `FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01`
  - `FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`
  - `FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01`
  - `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01`
  - `FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01`
  - `FPMS-V8-OVERLAY-CONTRACTS-20260712-01`
  - `FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01`
  - `FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01`
  - `FPMS-V8-OVERLAY-FEE-JOIN-20260712-01`
  - `FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`
  - `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`
  - `FPMS-V8-OVERLAY-HTTP-20260712-01`
  - `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01`
  - `FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01`
  - `FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
  - `FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
  - `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
  - `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
  - `FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`
  - `FPMS-V8-LIVE-FIXTURE-20260712-01`
  - `FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01`
  - `FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01`
  - `FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01`
- Allowed files:
  - `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md`
  - `docs/reviews/fpms_postdemo_v8_foundation_close_audit_20260712.md`
  - `backend/tests/test_v8_foundation_close_contract.py`
  - `artifacts/FPMS-V8-FOUNDATION-CLOSE-20260712-01/**`
- Required verification:
  - `for task in $(python3 -c "import json; print(*json.load(open('artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/materialization/foundation_manifest_index.json'))['task_ids'])"); do [ "$task" = "FPMS-V8-FOUNDATION-CLOSE-20260712-01" ] || ./scripts/task_validate.sh "$task"; done`
  - `./scripts/task_validate.sh FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01`
  - `python3 scripts/v8_catalog_manifest_gate.py --phase foundation --manifest tasks/batches/FPMS-POSTDEMO-V8-FOUNDATION-20260712-01.md --self-pending FPMS-V8-FOUNDATION-CLOSE-20260712-01`
  - `cd backend && .venv/bin/pytest -q tests/test_v8_foundation_close_contract.py`
  - `git diff --check -- docs/reviews/fpms_postdemo_v8_foundation_close_audit_20260712.md backend/tests/test_v8_foundation_close_contract.py tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md`
  - `./scripts/task_validate.sh FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- Remaining Follow-Up Task IDs: `None`
- Done definition: exact RED/GREEN, scoped lint/test/scope, dirty-baseline evidence, independent review, atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FOUNDATION-CLOSE-20260712-01` all PASS; exact closure complete and non-closure respected.
