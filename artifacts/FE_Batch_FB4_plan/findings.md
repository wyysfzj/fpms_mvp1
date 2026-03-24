# FB4 Batch — Findings

## Backend Dependency Check
- Backend A1 Task Template CRUD APIs: **CONFIRMED** in `backend/app/modules/tasks/api.py` (lines 53-89)
- TaskTemplateOut schema: id, code, name, add_days, add_months, inner_offset_days, default_worker_role, enabled, description, created_at, updated_at
- TaskTemplateCreateIn: code (required), name (required), add_days, add_months, inner_offset_days, default_worker_role, description
- TaskTemplateUpdateIn: name, add_days, add_months, inner_offset_days, default_worker_role, enabled, description (NO code — read-only after creation)

## Existing Patterns
- SystemParams.vue, TemplateList.vue, LetterheadList.vue in system module — use as reference
- Router has system/* routes under main layout
- menu.ts has 系统设置 group with 系统配置 item — need to add 任务模板

## Bugs Found
(none yet)

## Deviations
(none yet)
