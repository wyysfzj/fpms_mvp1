# DOCSEARCH-ATTACH-FE-01

## Closure Slice

Add the real frontend attachment-state selector to the document-specific search page and wire it to the existing `/documents` request.

This task closes exactly:
- selector exists in Simplified Chinese
- selector maps to `has_attachment`
- user can search with all / has attachments / no attachments

## Non-Closure

- no backend query semantics
- no export
- no result column expansion
- no detail changes
- no attachment preview / generation changes
- no other Module 2 residuals

## Allowlist

- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentList.vue`

## Follow-up Task IDs

- `DOCSEARCH-ATTACH-QA-01`
