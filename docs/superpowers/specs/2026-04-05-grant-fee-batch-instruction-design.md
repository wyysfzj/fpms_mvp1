# P2 #15 授权费管理 Batch Instruction Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE batch instruction path`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`FPMS SPEC 2.0` §5.7.2 明确要求在“授权费管理”界面支持勾选多条记录，将 `ClientInstruction` 批量设置为 `PAY` 或 `ABANDON`。当前 repo 虽然已有单行 state machine 与 draft generation，但授权费看板仍没有多选与批量用户路径，顶部 `状态操作（预留）` 还是 disabled。这个 GAP 不能再用单行动作或状态机存在来解释性关闭，必须补上真实批量用户路径。

## Assumptions

- 权威对象固定为：
  - `grant-fee batch PAY / ABANDON user path`
- 最小闭环固定为：
  - FE 支持勾选多条任务
  - FE 提供批量设置为 `PAY` / `ABANDON`
  - BE 接收一批 `task_ids + action`
  - BE 对每条任务按既有状态机做批量校验与应用
- 第一轮只支持：
  - `record_pay_instruction`
  - `record_abandon_instruction`
- batch slice 不自动吸收：
  - `mark_waiting_client`
  - `mark_draft_generated`
  - `mark_done`

## Scope

- 新增授权费批量客户指示 API
- 接入 grant-fee 页面多选与批量动作 UI
- 对非法状态批量更新返回一致的业务错误
- 保持现有单行草单生成与标记完成不变

## Explicit Non-scope

- 真实通知函生成
- 真实文书 / reminder task 生成
- batch draft generation
- detail/edit page
- bill generation / settlement semantics

## API / Contract

- New endpoint:
  - `POST /api/v1/grant-fee-tasks/batch-instruction`
- Permission:
  - `GrantFeeTask.Write`
- Payload:
  - `task_ids: list[str]`
  - `action: "record_pay_instruction" | "record_abandon_instruction"`
- Success semantics:
  - returns success count + updated task ids
- Error semantics:
  - `400` when selection empty or action not allowed for one/more rows
  - `404` when one/more task ids do not exist
  - `403` for permission denied

## Service Semantics

- Batch handler must:
  - deduplicate `task_ids`
  - ensure every task exists
  - derive current state using existing `derive_grant_fee_task_state(...)`
  - allow action only when current state is `WAITING_CLIENT`
- `record_pay_instruction` result:
  - `client_instruction = PAY`
  - `notify_count = 2`
- `record_abandon_instruction` result:
  - `client_instruction = ABANDON`
  - `notify_count = 4`
- Batch mutation should reuse the same business semantics as single-row action path

## UI Semantics

- Add selection column to grant-fee worklist
- Replace disabled `状态操作（预留）` with real batch action button
- Batch dialog or confirm flow must:
  - show current selected count
  - allow choosing:
    - `批量标记为支付`
    - `批量标记为放弃`
- On success:
  - show simplified-Chinese success toast
  - refresh current worklist
  - clear selection

## Shared-file / Ownership Analysis

- Backend shared ownership:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/tests/test_grant_fee_state_machine_api.py`
- Frontend shared ownership:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Verification

- Backend:
  - `python3 -m ruff format backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_grant_fee_state_machine_api.py`
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_grant_fee_state_machine_api.py`
  - `cd backend && pytest -q tests/test_grant_fee_state_machine_api.py`
- Frontend:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- real batch PAY / ABANDON user path on existing grant-fee page

## Explicit Non-closure Boundary

- no real notice generation
- no document/task creation
- no batch draft generation
- no detail/edit
- no bill generation
