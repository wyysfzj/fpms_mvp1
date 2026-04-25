# BE-B-DOCUMENT-TEST-MAINT-01

Task ID: `BE-B-DOCUMENT-TEST-MAINT-01`

Story Shape Classification:
- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: low
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Update stale B/document backend tests so helper-created cases include valid applicants after the applicant-list backend rule became mandatory.

This task closes only:
- Add valid applicant prerequisites to B2 reply-chain, B3 fee-linking, and document wizard backend test helpers.
- Preserve document wizard, reply-chain, fee-linking, task-generation, and attachment business assertions.
- Revalidate the B/document backend tests that were previously blocked by `CASE_APPLICANT_REQUIRED`.

## Explicit Non-Closure

Do not:
- modify backend service/API/schema behavior
- weaken applicant rules
- change document, task, fee, billing, or commission assertions
- implement pytest automation handlers
- modify `wave_b.py`
- modify frontend
- modify skeleton data

## Remaining Follow-Up Task IDs

- `PRODUCT-B-OA-WIZARD-CONTRACT-01`
- `BE-B-OA-WIZARD-READINESS-01`
- `BE-B-OA-REPLY-READINESS-01`
- `BE-B-OA-FINANCE-READINESS-01`

## Allowed Files

- `tasks/backend/test_maintenance/BE-B-DOCUMENT-TEST-MAINT-01.md`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_b3_fee_linking.py`
- `backend/tests/test_document_wizard_batch_create.py`
- `backend/tests/test_document_wizard_task_preview.py`
- `backend/tests/test_document_wizard_fee_preview.py`
- `backend/tests/test_document_wizard_attachment_preview.py`
- `artifacts/BE-B-DOCUMENT-TEST-MAINT-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py
python3 -m ruff format tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py
python3 -m ruff check tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py
pytest tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py -q
./scripts/task_validate.sh BE-B-DOCUMENT-TEST-MAINT-01
```

## Evidence Path

- `artifacts/BE-B-DOCUMENT-TEST-MAINT-01/results.jsonl`
- `artifacts/BE-B-DOCUMENT-TEST-MAINT-01/summary.md`
- `artifacts/BE-B-DOCUMENT-TEST-MAINT-01/git/diff.patch`
