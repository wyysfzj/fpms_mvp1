# PREPAYRPT-QA-01 — 预收款管理报表任务级审计与 ledger。

- Source: `docs/superpowers/plans/2026-03-29-billing-prepayment-reporting.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 审计 `P1 #7` 的实现切片、证据与 gate 状态，生成 item-to-slice ledger，并给出故事级 `PASS / FAIL / BLOCKED` 结论。
- Covered items:
  - `Priority P1 #7`
- Allowlist:
  - `artifacts/PREPAYRPT-QA-01/**`
  - `docs/superpowers/specs/2026-03-29-billing-prepayment-reporting-design.md`
  - `docs/superpowers/plans/2026-03-29-billing-prepayment-reporting.md`
  - `tasks/postenhancement/backend/PREPAYRPT-BE-01.md`
  - `tasks/postenhancement/frontend/PREPAYRPT-FE-01.md`
- Out of scope:
  - 任何产品代码修改
  - 重新定义预收款报表设计
  - 绕过已有 task gate 强行改判状态
- Shared ownership:
  - `No`
- Verification:
  - `./scripts/task_validate.sh PREPAYRPT-BE-01`
  - `./scripts/task_validate.sh PREPAYRPT-FE-01`
  - `test -f artifacts/PREPAYRPT-BE-01/results.jsonl`
  - `test -f artifacts/PREPAYRPT-FE-01/results.jsonl`
  - `./scripts/task_validate.sh PREPAYRPT-QA-01`

## Exact Closure Slice

- This task closes exactly:
  - 对预收款管理报表的已批准实现切片执行证据审计，生成 item-to-slice ledger，并给出故事级收口结论。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 新的 backend/frontend 功能实现
  - release gate 或全仓发布结论

## Remaining Follow-up Task IDs

- `None`

## Done Definition

- [ ] item-to-slice ledger written
- [ ] implementation tasks mapped to evidence
- [ ] story-level residual gap explicitly stated
- [ ] final story status emitted
- [ ] verification passed
- [ ] artifacts generated
