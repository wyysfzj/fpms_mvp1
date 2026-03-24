# FC1 Findings — Architect Agent

**Date**: 2026-02-27

## Backend B1 Verification

### CONFIRMED
1. All 4 DocTemplate CRUD endpoints exist in `backend/app/modules/documents/api.py` lines 51–113
2. Endpoints are registered under the Documents router (no separate prefix), at path `/doc-templates`
3. DocTemplate model has all 14 fields as specified (code, name, direction, enabled, + 8 spec fields, + created_at, updated_at)
4. Backend schemas match model 1:1 with proper validation (code: min_length=1, max_length=64; name: min_length=1, max_length=256)
5. `DocTemplateUpdateIn` does NOT include `code` — code is immutable after creation
6. List endpoint supports pagination via `PageResult[DocTemplateOut]` → `{ items, page, page_size, total }`
7. List endpoint supports filtering: `q` (text search), `direction` (IN/OUT), `enabled` (bool)

### DISCOVERIES
1. **Doc-template routes are in documents module, NOT templates module**: The templates module (`backend/app/modules/templates/`) handles `Template` (docx rendering templates) and `LetterHead` — completely separate from `DocTemplate`.
2. **DocTemplate is in documents module**: Model in `documents/models.py`, service in `documents/service.py`, API in `documents/api.py`. This is correct per B1 design.
3. **TaskTemplate list is unpaginated**: `GET /task-templates` returns a flat `TaskTemplate[]` array (not paginated), while DocTemplate list IS paginated. This means the DocTemplateList.vue needs `el-pagination` which TaskTemplateList.vue does not have.
4. **`deadline_template_code` references TaskTemplate.code**: Not enforced by FK at DB level (just a string column), but semantically points to task template codes.
5. **`fee_item_list` and `input_fields` are plain TEXT columns**: Stored as JSON strings, no JSONB. Backend does no JSON validation — just stores the string as-is.
6. **Backend duplicate code check**: `create_doc_template()` raises 409 if code already exists (line 363-368 of service.py).
7. **ApiErrorBanner component exists**: Located at `frontend/src/components/errors/ApiErrorBanner.vue` — available for reuse.
8. **Frontend uses relative imports**: No `@/` alias — all imports use `../../../` relative paths (confirmed in TaskTemplateList.vue).

### NO ISSUES FOUND
- All backend dependencies are in place
- No missing endpoints or schemas
- Frontend patterns are clear and consistent
- Pagination interface `Pagination<T>` matches backend `PageResult[T]` shape exactly

## Bugs Found
(none)

## Deviations
(none — all backend APIs match spec)
