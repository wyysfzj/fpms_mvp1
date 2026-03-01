# PE-FE-QA-03 — 补充新增业务链路手工冒烟文档。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `doc`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：补充新增业务链路手工冒烟文档。
- Allowlist:
  - `docs/frontend_smoke_flows.md`
  - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
- 依赖：PE-FE-QA-01
- 验收：覆盖 annuity/collections/commission/consulting/expense。
- 验证：文档自检。

---

## 2. 每个任务统一验证模板
```bash
cd frontend
npm run lint
npm run typecheck
# 页面/路由改动任务建议额外执行
npm run build
```

## 3. 多 Agent 并行建议
- 可并行：
  - 不同模块下新建页面任务（`annuity` vs `commission` vs `consulting`）
  - API client 新文件任务
- 必须串行：
  - `router/index.ts`、`constants/menu.ts`、`stores/auth.ts`
  - 同一页面文件的多次改动任务

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
