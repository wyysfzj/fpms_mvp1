# REPORTS-LEDGER-01 — `#13` strict report-family implementation ledger

- Source: `docs/superpowers/plans/2026-04-04-reports-implementation-ledger.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 严格对照 `FPMS SPEC 2.0.md` 与当前真实产品实现，为 `#13 所有统计报表` 产出一份 report-family implementation ledger，明确哪些 family 已实现、哪些仅为 representative slice、哪些仍需 residual implementation，并据此给出第一条真正的 implementation family 建议。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-04-reports-implementation-ledger-design.md`
  - 更新 `docs/superpowers/plans/2026-04-04-reports-implementation-ledger.md`
- Explicit non-closure:
  - 不做任何报表产品实现补丁
  - 不更新 `#13` 的 close decision
  - 不扩展到 export / print / chart / analytics
- Remaining follow-up task ids:
  - `REPORTS-QA-LEDGER-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-04-reports-implementation-ledger-design.md`
  - `docs/superpowers/plans/2026-04-04-reports-implementation-ledger.md`
  - `tasks/postenhancement/backend/REPORTS-LEDGER-01.md`
  - `tasks/postenhancement/backend/REPORTS-QA-LEDGER-01.md`
- Verification:
  - `./scripts/task_validate.sh REPORTS-LEDGER-01`

## Execution Checklist

- [ ] Extract report-family inventory from spec and current product evidence
- [ ] Mark each family as `Implemented / Partially Implemented / Contract-Plan Only / Missing`
- [ ] Freeze family boundaries and non-closure
- [ ] Recommend one first implementation family without starting code work
