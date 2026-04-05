# GF-BATCH-INSTR-BE-01 — grant-fee batch PAY / ABANDON endpoint

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-batch-instruction.md`
- Type: `backend api + service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为授权费管理补上批量客户指示的最小后端闭环，新增批量 `PAY / ABANDON` API，并沿用现有 state machine 语义对所选任务执行批量校验和状态推进。
- Exact closure slice:
  - 新增 batch instruction request/response schema
  - 新增 batch instruction endpoint
  - 新增 batch instruction service rule
  - 新增 targeted backend tests
- Explicit non-closure:
  - 不做通知函生成
  - 不做 batch draft generation
  - 不做 bill/document linkage
  - 不做 detail/edit
- Remaining follow-up task ids:
  - `GF-BATCH-INSTR-FE-01`
  - `GF-BATCH-INSTR-QA-01`
- Allowlist:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/tests/test_grant_fee_state_machine_api.py`
- Verification:
  - `python3 -m ruff format backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_grant_fee_state_machine_api.py`
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_grant_fee_state_machine_api.py`
  - `cd backend && pytest -q tests/test_grant_fee_state_machine_api.py`

## Execution Checklist

- [ ] Add batch input/output schemas for selected task ids and action
- [ ] Add backend endpoint with `Depends(require_perm("GrantFeeTask.Write"))`
- [ ] Reuse frozen state machine semantics for batch PAY / ABANDON
- [ ] Add success, invalid-state, missing-task, and permission tests
