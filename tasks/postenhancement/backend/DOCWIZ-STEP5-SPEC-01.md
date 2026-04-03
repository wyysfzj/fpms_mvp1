# DOCWIZ-STEP5-SPEC-01 — 向导 Step 5 附件/模板生成 residual contract

- Source: `docs/superpowers/plans/2026-04-03-docwiz-step5-attachment-generation.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结中间文件 5 步向导 `Step 5 – 附件 / 模板生成` 的 residual contract，只明确适用条件、candidate 生成语义、UI 字段边界与最终写入时机。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-03-docwiz-step5-attachment-generation-design.md`
  - 更新 `docs/superpowers/plans/2026-04-03-docwiz-step5-attachment-generation.md`
- Explicit non-closure:
  - 不做 dispatch / envelope
  - 不做 search / reporting
  - 不做 status transitions
  - 不做 frontend/backend 实现
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP5-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-docwiz-step5-attachment-generation-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-step5-attachment-generation.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP5-SPEC-01.md`
  - `tasks/postenhancement/backend/DOCWIZ-QA-STEP5-01.md`
- Verification:
  - `./scripts/task_validate.sh DOCWIZ-STEP5-SPEC-01`

## Execution Checklist

- [ ] Freeze Step 5 applicability
- [ ] Freeze attachment/template candidate semantics
- [ ] Freeze UI preview/edit boundary
- [ ] Freeze final-write timing
- [ ] Keep non-Step-5 capabilities explicitly deferred
