# FC1 Batch — Task Plan

## Goal
Create DocTemplate management page for the configuration-driven document automation system from backend B1.

## Backend Dependency
**Backend B1 (DocTemplate Enhancement) — needs verification**
APIs: GET/POST/PUT /doc-templates, GET /doc-templates/{id}
Fields: id, code, name, direction, enabled, status_effect, status_restore, deadline_template_code, fee_draft_type, fee_item_list, need_reply, reply_to_template_code, input_fields

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/documents.ts` | modify |
| `frontend/src/api/documents.types.ts` | modify |
| `frontend/src/modules/system/pages/DocTemplateList.vue` | new |
| `frontend/src/router/index.ts` | modify |
| `frontend/src/constants/menu.ts` | modify |

## Status
- [ ] Architect Plan approved
- [ ] Implementation complete
- [ ] Quality Gate passed
- [ ] Review Report generated
