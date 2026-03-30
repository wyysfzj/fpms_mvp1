# DOCDSP-BE-ENV-01 Evidence Summary

- Task: `DOCDSP-BE-ENV-01`
- Role: backend worker takeover by main thread for evidence closure
- Closure slice: envelope preview query with address priority `CASE_DOC_ADDRESS -> CLIENT_DEFAULT_ADDRESS -> FIRST_APPLICANT_ADDRESS -> MANUAL_REQUIRED`
- Non-closure respected: no mailing field updates, no dispatch generation, no frontend changes, no print log persistence

## Verification

- `python3 -m ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_envelope.py` -> PASS
- `cd backend && PYTHONPATH=. pytest -q tests/test_doc_dispatch_envelope.py` -> PASS
- `./scripts/task_validate.sh DOCDSP-BE-ENV-01` -> PASS

## Evidence

- Code diff: `artifacts/DOCDSP-BE-ENV-01/git/diff.patch`
- Results log: `artifacts/DOCDSP-BE-ENV-01/results.jsonl`
- Dirty baseline list: `artifacts/DOCDSP-BE-ENV-01/baseline_external_files.txt`
- Dirty allowlist baseline: `artifacts/DOCDSP-BE-ENV-01/baseline_allowlist.diff`

## Scope Notes

- Added `GET /documents/{document_id}/envelope-preview`
- Added envelope preview response schema
- Resolved recipient and address from case doc address, then client default address, then first applicant address
