# PE-FE-WD-03

Status: PASS

Scope:
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/pages/DocumentEdit.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`

Changes:
- surfaced template-rule cues on create/edit/detail
- made `need_reply`, deadline-template, fee-draft, status-effect, and reply-template hints visible to users
- aligned edit-page template visibility with create/detail behavior

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

Notes:
- no new route
- no document generation scope added
