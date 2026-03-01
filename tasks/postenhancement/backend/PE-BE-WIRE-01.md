# PE-BE-WIRE-01 — 将新增模块 router 接入 `backend/app/api/router.py`（一次性）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：将新增模块 router 接入 `backend/app/api/router.py`（一次性）。
- Allowlist:
  - `backend/app/api/router.py`
- 依赖：至少一个新增模块 API 文件落地
- 验收：路由可被 `app/main.py` 正常加载。
- 验证：`cd backend && python3 -m py_compile app/api/router.py && pytest -q`

---

## 3. 每个任务统一验证脚本模板
```bash
./scripts/evidence_run.sh <TASK-ID> lint bash -lc "cd backend && ruff check ."
./scripts/evidence_run.sh <TASK-ID> fmt  bash -lc "cd backend && ruff format ."
./scripts/evidence_run.sh <TASK-ID> test bash -lc "cd backend && pytest -q"
./scripts/evidence_finalize.sh <TASK-ID>
./scripts/task_validate.sh <TASK-ID>
```

## 4. 多 Agent 分配建议
- 可并行：
  - DB 任务按“不同 migration 文件 + 不同模型文件”并行
  - API 任务按“不同模块 api.py”并行
- 必须串行：
  - `router.py` wiring
  - 同一 `api.py` 内多个 endpoint
  - Commission 与 Billing hook 任务（PE-BE-COM-05/06）

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
