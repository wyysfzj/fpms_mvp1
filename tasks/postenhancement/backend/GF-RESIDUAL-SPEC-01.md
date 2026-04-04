# GF-RESIDUAL-SPEC-01 — `#15` 授权费管理 residual workflow spec

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-residual-workflow.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 对 `#15 授权费管理` 形成一份 strict residual workflow map，明确当前 first-round workflow 已闭合了什么、相对 spec 还剩哪些 post-draft lifecycle / bill / document / detail residual，并推荐一个最小 follow-up story。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-05-grant-fee-residual-workflow-design.md`
  - 更新 `docs/superpowers/plans/2026-04-05-grant-fee-residual-workflow.md`
- Explicit non-closure:
  - 不做任何 grant-fee 产品实现补丁
  - 不重做 `GFPRE-* / GFSM-* / GFWL-* / GFDRAFT-*`
  - 不更新 `#15` 的 close decision
- Remaining follow-up task ids:
  - `GF-QA-RESIDUAL-SPEC-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-05-grant-fee-residual-workflow-design.md`
  - `docs/superpowers/plans/2026-04-05-grant-fee-residual-workflow.md`
  - `tasks/postenhancement/backend/GF-RESIDUAL-SPEC-01.md`
  - `tasks/postenhancement/backend/GF-QA-RESIDUAL-SPEC-01.md`
- Verification:
  - `./scripts/task_validate.sh GF-RESIDUAL-SPEC-01`

## Execution Checklist

- [ ] Freeze first-round implemented workflow authority
- [ ] Enumerate named residual buckets after `generate-draft`
- [ ] Recommend one first post-draft story
- [ ] Keep bill/document/detail/reporting explicitly deferred
