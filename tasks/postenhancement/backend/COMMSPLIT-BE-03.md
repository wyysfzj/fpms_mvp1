# COMMSPLIT-BE-03 — settlement linkage checkpoint。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-settlement-linkage.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 冻结 `backend/app/modules/commission/models.py` 与 `backend/app/modules/commission/service.py` 中当前多代理 split 下的 row-level settlement linkage 语义，只决定 `is_settleable`、`Commission -> CommissionSettleLine` 进入条件、linked-row immutability 和 settlement-as-consumer 边界。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-BE-03`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-settlement-linkage-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-settlement-linkage.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-03.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md` is referenced for downstream audit wording alignment only; this wave does not claim or absorb QA ownership.
- Out of scope:
  - `backend/**`
  - `frontend/**`
  - any settlement/API/FE/report/schema/model implementation
- Shared ownership:
  - `No`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md` remains QA-owned; any reference-only wording alignment does not transfer shared ownership into this wave
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-03`

## Current Code Facts

- `Commission`
  - persists `is_settleable` and `settleable_date` per commission row
- `CommissionSettleLine`
  - is unique by `settlement_id / commission_id`
- `recompute_commission_settleable(...)`
  - recalculates settleable state per commission row
- `generate_commission_settlement_lines(...)`
  - consumes existing commission rows where `is_settleable == True`
  - creates one settlement line per eligible commission row
- `_commission_is_rewritable(...)`
  - treats any commission already referenced by `CommissionSettleLine` as non-rewritable

## Exact Closure Slice

- This task closes exactly:
  - freeze row-level settlement linkage semantics only

## Frozen Behavior Result

- `is_settleable` scope:
  - settleable state is row-level per commission
- Independent settlement entry:
  - the same `bill/case` may yield multiple independently settleable agent-level commission rows
- Settlement line generation:
  - remains one line per eligible `commission_id`
- Linked boundary:
  - any commission already linked to `CommissionSettleLine` remains outside rewrite scope
- Source-of-truth boundary:
  - settlement consumes current commission rows only and does not reinterpret split rows directly
- Follow-up mapping:
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-06` for downstream audit-only validation of this frozen behavior

## Explicit Non-Closure Statement

- This task does NOT close:
  - settlement/API implementation changes
  - FE viewing/editing
  - report/payout/export
  - schema/model changes
  - new settlement workflow UI
  - QA execution or ownership transfer

## Remaining Follow-up Task IDs

- `COMMSPLIT-FE-01`
- `COMMSPLIT-QA-06` (audit-only, downstream)

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] row-level settleable semantics explicit from current code facts
- [ ] settlement-line entry semantics explicit from current code facts
- [ ] linked/non-linked boundary explicit from current code facts
- [ ] follow-up mapping explicit
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Review current settlement evidence before changing docs
- [ ] Update the settlement linkage spec and plan only
- [ ] Keep follow-up stories explicit
- [ ] If updating `COMMSPLIT-QA-06.md`, limit the change to audit wording alignment only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
