# DOCWIZ-STEP5-PREREQ-01 — Step 5 模板来源 prerequisite freeze

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step5-template-source-prereq.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 Step 5 final submit 当前不可直接实现的模板来源 blocker，并给出下一条 prerequisite task 建议。
- Exact closure slice:
  - 明确 `DocTemplate` 与真实模板文件来源之间缺失的映射契约
  - 明确 Step 5 final submit 为什么不能直接开始实现
- Explicit non-closure:
  - 不做 schema change
  - 不做 API/service implementation
  - 不做 Step 5 final submit integration
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP5-PREREQ-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-04-docwiz-step5-template-source-prereq-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step5-template-source-prereq.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP5-PREREQ-01.md`
  - `artifacts/DOCWIZ-STEP5-PREREQ-01/**`
- Verification:
  - `./scripts/task_validate.sh DOCWIZ-STEP5-PREREQ-01`

## Execution Checklist

- [ ] Freeze blocker statement
- [ ] Freeze source-mapping options
- [ ] Produce explicit next-task recommendation
