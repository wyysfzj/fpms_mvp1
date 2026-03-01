# Post-Enhancement Package (for Agent Team / Multi-Agent)

## Files
- `tasks/postenhancement/POSTENH_SPEC2_ENHANCEMENT_PLAN.md`
  - 总体增强计划（目标、架构、波次、门禁、回归策略）
- `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
  - 后端原子任务清单（分批、依赖、allowlist、验收与验证）
- `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
  - 前端原子任务清单（分批、依赖、allowlist、验收与验证）
- `tasks/postenhancement/backend/INDEX.md`
  - 后端“按 Task ID 拆分”的独立任务索引（每个 Task 一个 md 文件）
- `tasks/postenhancement/frontend/INDEX.md`
  - 前端“按 Task ID 拆分”的独立任务索引（每个 Task 一个 md 文件）

## Suggested Execution
1. 先执行 backend B0/B1（契约与数据基线）
2. 再执行 backend B2~B5（业务功能）
3. 前端按 B1~B4 跟进
4. 最后执行 B6 / FE-B5 做统一回归与发布门禁

## Split Task Files
- Backend split files directory: `tasks/postenhancement/backend/`
- Frontend split files directory: `tasks/postenhancement/frontend/`
- File naming convention: `<TASK-ID>.md`
  - 示例：`PE-BE-COM-05.md`, `PE-FE-AN-03.md`

## Global Gates
- Backend: `ruff check --fix . && ruff format . && ruff check . && pytest -q`
- Frontend: `npm run lint && npm run typecheck && npm run build`
- Evidence: `scripts/evidence_run.sh` / `scripts/task_validate.sh` / `scripts/release_gate.sh`
