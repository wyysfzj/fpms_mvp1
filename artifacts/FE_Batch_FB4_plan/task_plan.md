# FB4 Batch — Task Plan

## Goal
Create TaskTemplate management page. Add menu item. Verify SystemParam page works with new A4 seeded params.

## Backend Dependency
**Backend A1 (Task Template CRUD APIs) — CONFIRMED COMPLETE**
- `GET /task-templates` (enabled_only filter)
- `POST /task-templates` → TaskTemplateOut (201)
- `PUT /task-templates/{template_id}` → TaskTemplateOut

**TaskTemplateOut schema**: id, code, name, add_days, add_months, inner_offset_days, default_worker_role, enabled, description, created_at, updated_at

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/tasks.ts` | modify |
| `frontend/src/api/tasks.types.ts` | modify |
| `frontend/src/modules/system/pages/TaskTemplateList.vue` | new |
| `frontend/src/router/index.ts` | modify |
| `frontend/src/constants/menu.ts` | modify |

## Status
- [ ] Architect Plan approved
- [ ] Implementation complete
- [ ] Quality Gate passed
- [ ] Review Report generated
