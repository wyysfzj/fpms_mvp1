# GF-NOTICE-DOC-SPEC-01 — grant-fee real notice generation authority freeze

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-notice-generation.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 严格对照 `FPMS SPEC 2.0` 与当前 grant-fee/documents/templates 实现，为 `#15` 产出一份 real grant-fee notice generation authority freeze，明确模板权威、用户路径、生成对象、write-back 语义以及第一条真正 implementation slice。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-05-grant-fee-notice-generation-design.md`
  - 更新 `docs/superpowers/plans/2026-04-05-grant-fee-notice-generation.md`
- Explicit non-closure:
  - 不做任何 grant-fee / documents 产品实现补丁
  - 不做 reminder task generation
  - 不更新 `#15` close decision
- Remaining follow-up task ids:
  - `GF-QA-NOTICE-DOC-SPEC-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-05-grant-fee-notice-generation-design.md`
  - `docs/superpowers/plans/2026-04-05-grant-fee-notice-generation.md`
  - `tasks/postenhancement/backend/GF-NOTICE-DOC-SPEC-01.md`
  - `tasks/postenhancement/backend/GF-QA-NOTICE-DOC-SPEC-01.md`
- Verification:
  - `./scripts/task_validate.sh GF-NOTICE-DOC-SPEC-01`

## Execution Checklist

- [ ] Freeze template authority and minimal lineage rule
- [ ] Freeze eligible row semantics and write-back semantics
- [ ] Freeze first implementation-ready closure slice
- [ ] Explicitly defer reminder generation and dispatch semantics
