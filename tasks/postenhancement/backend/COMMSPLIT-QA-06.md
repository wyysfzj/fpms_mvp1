# COMMSPLIT-QA-06 — settlement linkage close audit。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-settlement-linkage.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 审计 `COMMSPLIT-BE-03` 的证据、settlement-linkage 结论与 follow-up remapping，确认 row-level `is_settleable`、`Commission -> CommissionSettleLine` 进入条件、linked-row immutability 和 settlement-as-consumer 边界已被冻结，并给出 settlement-wave 级 `PASS / FAIL / BLOCKED` 结论。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-BE-03`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-06/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-settlement-linkage-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-settlement-linkage.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-03.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md`
- Out of scope:
  - any product code change
  - any settlement/API/FE implementation
- Shared ownership:
  - `No`
  - this task remains QA-owned and audit-only
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-03`
  - `./scripts/task_validate.sh COMMSPLIT-QA-06`

## Exact Closure Slice

- This task closes exactly:
  - 对 settlement-linkage wave 执行证据审计，确认 row-level `is_settleable`、`Commission -> CommissionSettleLine` 进入条件、linked-row immutability 和 settlement-as-consumer 边界的冻结结论与 follow-up remapping 已被冻结，并明确 implementation stories 仍未执行。
  - this is a QA audit slice only; it does not transfer or absorb implementation ownership.

## Explicit Non-Closure Statement

- This task does NOT close:
  - settlement/API implementation changes
  - frontend viewing/editing
  - schema/model changes
  - report/payout/export

## Remaining Follow-up Task IDs

- `None` for the QA audit task itself.
- This does not mean the broader commission-split program has no deferred work; the remaining implementation follow-ups continue in the downstream task IDs referenced by `COMMSPLIT-BE-03`, including `COMMSPLIT-FE-01`.

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] settlement-linkage evidence mapped
- [ ] residual implementation stories listed
- [ ] final settlement-wave status emitted
- [ ] verification passed
- [ ] artifacts generated

## Execution Checklist

- [ ] Confirm audit-only allowlist
- [ ] Re-run referenced task gates
- [ ] Check required evidence files exist
- [ ] Write close summary
- [ ] If needed, align QA-task wording with the frozen settlement result and audit-only boundary
- [ ] Capture scoped audit diff
- [ ] Stop without editing product code
