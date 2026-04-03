# DOCWIZ-STEP3-SPEC-01 — 向导 Step 3 时限联动 residual contract

- Source: `docs/superpowers/plans/2026-04-03-docwiz-step3-deadline-linkage.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结中间文件 5 步向导 `Step 3 – 生成相关时限任务` 的 residual contract，只明确适用条件、candidate 生成语义、UI 字段边界与最终写入时机。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-03-docwiz-step3-deadline-linkage-design.md`
  - 更新 `docs/superpowers/plans/2026-04-03-docwiz-step3-deadline-linkage.md`
- Explicit non-closure:
  - 不做 Step 4 fee linkage
  - 不做 Step 5 / later steps
  - 不做 dispatch / envelope
  - 不做 search / reporting
  - 不做 frontend/backend 实现
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP3-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-docwiz-step3-deadline-linkage-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-step3-deadline-linkage.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP3-SPEC-01.md`
  - `tasks/postenhancement/backend/DOCWIZ-QA-STEP3-01.md`
- Verification:
  - `./scripts/task_validate.sh DOCWIZ-STEP3-SPEC-01`

## Execution Checklist

- [ ] Freeze Step 3 applicability
- [ ] Freeze candidate-generation semantics
- [ ] Freeze UI preview/edit boundary
- [ ] Freeze final-write timing
- [ ] Keep Step 4 and all non-wizard-adjacent capabilities explicitly deferred
