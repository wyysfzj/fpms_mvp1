# DOCSEARCH-ATTACH-BE-01

## Closure Slice

Add backend `has_attachment` filter support to `GET /documents`.

This task closes exactly:
- request contract accepts `has_attachment`
- service-layer document list query filters by attachment existence
- targeted backend tests cover true / false / omitted behavior

## Non-Closure

- no frontend selector
- no export
- no result column expansion
- no detail changes
- no attachment generation changes
- no other Module 2 residuals

## Allowlist

- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_document_specific_search_api.py`

## Follow-up Task IDs

- `DOCSEARCH-ATTACH-FE-01`
- `DOCSEARCH-ATTACH-QA-01`
