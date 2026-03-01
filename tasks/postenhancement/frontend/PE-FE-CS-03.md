# PE-FE-CS-03 — 顾问/检索服务费草单生成页。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：顾问/检索服务费草单生成页。
- Allowlist:
  - `frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue` (new)
- 依赖：PE-BE-CS-05
- 验收：支持固定/工时/混合模式参数输入。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
