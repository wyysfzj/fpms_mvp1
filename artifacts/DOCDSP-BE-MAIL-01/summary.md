# DOCDSP-BE-MAIL-01 Evidence Summary

- Task: `DOCDSP-BE-MAIL-01`
- Role: backend worker
- Closure slice: batch register outgoing mailing info for selected `Document` rows, updating `outgoing_reg_no` and optional `forward_date`
- Non-closure respected: no dispatch table generation, no envelope query, no frontend changes

## Verification

- `python3 -m ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_mailing_action.py` -> PASS
- `cd backend && PYTHONPATH=. pytest -q tests/test_doc_dispatch_mailing_action.py` -> PASS
- `./scripts/task_validate.sh DOCDSP-BE-MAIL-01` -> PASS

## Evidence

- Code diff: `artifacts/DOCDSP-BE-MAIL-01/git/diff.patch`
- Results log: `artifacts/DOCDSP-BE-MAIL-01/results.jsonl`
- Dirty baseline list: `artifacts/DOCDSP-BE-MAIL-01/baseline_external_files.txt`
- Dirty allowlist baseline: `artifacts/DOCDSP-BE-MAIL-01/baseline_allowlist.diff`

## Scope Notes

- Added a new mailing batch endpoint under `documents`
- Batch updates apply only to `OUT` documents
- Invalid selection direction is rejected with a business error
