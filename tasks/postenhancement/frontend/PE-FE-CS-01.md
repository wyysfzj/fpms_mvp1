# PE-FE-CS-01 — 顾问/检索项目立案页。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：顾问/检索项目立案页。
- Allowlist:
  - `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue` (new)
  - `frontend/src/api/consulting.ts` (new)
  - `frontend/src/api/consulting.types.ts` (new)
- 依赖：PE-BE-CS-01
- 验收：支持创建 CONSULTING/SEARCH 项目并校验专属字段。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
