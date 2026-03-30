# DOCDSP-BE-DISP-01 Evidence Summary

- Task: `DOCDSP-BE-DISP-01`
- Role: backend worker takeover by main thread for evidence closure
- Closure slice: create document dispatch sheets and fetch dispatch detail for generated `DocDispatch` / `DocDispatchLine`
- Non-closure respected: no mailing field updates, no envelope preview query, no frontend changes

## Verification

- `python3 -m ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_handoff.py` -> PASS
- `cd backend && PYTHONPATH=. pytest -q tests/test_doc_dispatch_handoff.py` -> PASS
- `./scripts/task_validate.sh DOCDSP-BE-DISP-01` -> pending until results and summary landed, then PASS

## Evidence

- Code diff: `artifacts/DOCDSP-BE-DISP-01/git/diff.patch`
- Results log: `artifacts/DOCDSP-BE-DISP-01/results.jsonl`
- Dirty baseline list: `artifacts/DOCDSP-BE-DISP-01/baseline_external_files.txt`
- Dirty allowlist baseline: `artifacts/DOCDSP-BE-DISP-01/baseline_allowlist.diff`

## Scope Notes

- Added `POST /documents/dispatches` for dispatch generation
- Added `GET /documents/dispatches/{id}` for dispatch detail
- Enforced same-client and OUT-direction constraints for selected documents
