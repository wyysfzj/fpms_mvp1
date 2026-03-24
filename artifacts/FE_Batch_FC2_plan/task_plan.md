# FC2 Batch — Task Plan

## Goal
Add template selection to DocumentCreate, display reply chain info in DocumentDetail, show need_reply indicator in DocumentList.

## Backend Dependency
**Backend B2 (Document Reply Chain) — needs verification**
Reply chain fields: reply_to_id, need_reply, reply_date
DocTemplate from B1: need_reply, status_effect, deadline_template_code

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/documents.types.ts` | modify |
| `frontend/src/modules/documents/pages/DocumentCreate.vue` | modify |
| `frontend/src/modules/documents/pages/DocumentDetail.vue` | modify |
| `frontend/src/modules/documents/pages/DocumentList.vue` | modify |

## Status
- [ ] Architect Plan approved
- [ ] Implementation complete
- [ ] Quality Gate passed
- [ ] Review Report generated
