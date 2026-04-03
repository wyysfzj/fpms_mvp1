# COMMSPLIT-QA-08 — FE edit consistency close audit

- Source: `docs/superpowers/plans/2026-04-03-commission-split-fe-edit-consistency.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `COMMSPLIT-FE-EDIT-01` 的证据与 create/edit 一致性结果，确认 `CaseCreate.vue` 已补齐 split 录入入口、校验与提交能力，并明确 residual FE work 仍未执行。
- Exact closure slice:
  - 对 `COMMSPLIT-FE-EDIT-01` 执行证据审计并给出 `PASS / FAIL / BLOCKED` 结论
- Explicit non-closure:
  - 不改任何产品代码
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-08/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-fe-edit-consistency-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-fe-edit-consistency.md`
  - `tasks/postenhancement/frontend/COMMSPLIT-FE-EDIT-01.md`
  - `tasks/postenhancement/frontend/COMMSPLIT-QA-08.md`
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-FE-EDIT-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-08`

## Execution Checklist

- [ ] Confirm audit-only allowlist
- [ ] Re-run referenced task gates
- [ ] Check required evidence files exist
- [ ] Write close summary
- [ ] Stop without editing product code
