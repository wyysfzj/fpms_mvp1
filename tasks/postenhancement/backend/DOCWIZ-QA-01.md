# DOCWIZ-QA-01 — 中间文件向导 Step1-2 任务级审计与 ledger。

- Source: `docs/superpowers/plans/2026-03-29-documents-step12-wizard.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 审计 `P1 #8` 的实现切片、证据与 gate 状态，生成 item-to-slice ledger，并给出故事级 `PASS / FAIL / BLOCKED` 结论。
- Covered items:
  - `Priority P1 #8`
- Allowlist:
  - `artifacts/DOCWIZ-QA-01/**`
  - `docs/superpowers/specs/2026-03-29-documents-step12-wizard-design.md`
  - `docs/superpowers/plans/2026-03-29-documents-step12-wizard.md`
  - `tasks/postenhancement/backend/DOCWIZ-BE-01.md`
  - `tasks/postenhancement/frontend/DOCWIZ-FE-SHELL-01.md`
  - `tasks/postenhancement/frontend/DOCWIZ-FE-STEP1-01.md`
  - `tasks/postenhancement/frontend/DOCWIZ-FE-STEP2-01.md`
- Out of scope:
  - 任何产品代码修改
  - 重新定义向导设计
  - 绕过 task gate 改判状态
- Shared ownership:
  - `No`
- Verification:
  - `./scripts/task_validate.sh DOCWIZ-BE-01`
  - `./scripts/task_validate.sh DOCWIZ-FE-SHELL-01`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP1-01`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP2-01`
  - `./scripts/task_validate.sh DOCWIZ-QA-01`

## Exact Closure Slice

- This task closes exactly:
  - 对中间文件向导 Step1-2 的已批准实现切片执行证据审计，生成 item-to-slice ledger，并给出故事级收口结论。

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
