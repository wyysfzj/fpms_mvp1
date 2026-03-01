# PE-BE-TEST-01 — 新增 annuity/collections/commission/consulting 关键 E2E 测试。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `doc+test`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 annuity/collections/commission/consulting 关键 E2E 测试。
- Allowlist:
  - `backend/tests/test_annuity_e2e.py`
  - `backend/tests/test_collections_e2e.py`
  - `backend/tests/test_commission_e2e.py`
  - `backend/tests/test_consulting_e2e.py`
- 依赖：B2-B5 完成
- 验收：关键路径全绿。
- 验证：`cd backend && pytest -q`

---

## 2. Router Wiring 原子任务（串行，避免冲突）

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
