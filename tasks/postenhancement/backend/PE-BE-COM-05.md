# PE-BE-COM-05 — 在 billing 链路中接入提成服务 hook（不改变旧返回契约）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：在 billing 链路中接入提成服务 hook（不改变旧返回契约）。
- Allowlist:
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-COM-04
- 验收：账单生成后可写提成；失败不影响账单主事务需有明确策略。
- 验证：`cd backend && pytest -q tests/test_spec_alignment_e2e.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
