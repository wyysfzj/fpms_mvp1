# GF-LEDGER-01 — `#15` strict grant-fee workflow implementation ledger

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-implementation-ledger.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 严格对照 `FPMS SPEC 2.0.md` 与当前真实产品实现，为 `#15 授权费管理` 产出一份 grant-fee workflow implementation ledger，明确哪些 slices 已实现、哪些仅为 representative / visibility slice、哪些仍需 residual implementation，并据此给出第一条真正的 implementation slice 建议。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-05-grant-fee-implementation-ledger-design.md`
  - 更新 `docs/superpowers/plans/2026-04-05-grant-fee-implementation-ledger.md`
- Explicit non-closure:
  - 不做任何 grant-fee 产品实现补丁
  - 不更新 `#15` 的 close decision
  - 不扩展到 bill/document generation、detail/edit、batch actions、settlement semantics
- Remaining follow-up task ids:
  - `GF-QA-LEDGER-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-05-grant-fee-implementation-ledger-design.md`
  - `docs/superpowers/plans/2026-04-05-grant-fee-implementation-ledger.md`
  - `tasks/postenhancement/backend/GF-LEDGER-01.md`
  - `tasks/postenhancement/backend/GF-QA-LEDGER-01.md`
- Verification:
  - `./scripts/task_validate.sh GF-LEDGER-01`

## Execution Checklist

- [ ] Extract grant-fee workflow inventory from spec and current product evidence
- [ ] Mark each slice as `Implemented / Partially Implemented / Contract-Plan Only / Missing`
- [ ] Freeze workflow boundaries and non-closure
- [ ] Recommend one first implementation slice without starting code work
