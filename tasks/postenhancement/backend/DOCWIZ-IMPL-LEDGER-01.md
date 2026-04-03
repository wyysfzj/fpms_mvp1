# DOCWIZ-IMPL-LEDGER-01 — `#8` strict implementation gap ledger

- Source: `docs/superpowers/plans/2026-04-03-docwiz-implementation-gap-ledger.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 严格对照 `FPMS SPEC 2.0.md`，为 `#8 中间文件 5 步向导` 产出一份 implementation gap ledger，明确哪些能力已实现、哪些仅完成 contract freeze、哪些仍缺实现，并据此给出 implementation slices。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-03-docwiz-implementation-gap-ledger-design.md`
  - 更新 `docs/superpowers/plans/2026-04-03-docwiz-implementation-gap-ledger.md`
- Explicit non-closure:
  - 不做任何产品实现补丁
  - 不更新 close decision
  - 不扩展到 dispatch / search / reporting
- Remaining follow-up task ids:
  - `DOCWIZ-QA-IMPL-LEDGER-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-docwiz-implementation-gap-ledger-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-implementation-gap-ledger.md`
  - `tasks/postenhancement/backend/DOCWIZ-IMPL-LEDGER-01.md`
  - `tasks/postenhancement/backend/DOCWIZ-QA-IMPL-LEDGER-01.md`
- Verification:
  - `./scripts/task_validate.sh DOCWIZ-IMPL-LEDGER-01`

## Execution Checklist

- [ ] Extract step-level capabilities from spec
- [ ] Mark each capability as `Implemented / Contract Frozen Only / Missing`
- [ ] Group residual implementation buckets
- [ ] Keep implementation work explicitly deferred
