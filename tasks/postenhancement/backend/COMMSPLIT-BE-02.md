# COMMSPLIT-BE-02 — generation hardening checkpoint。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-generation-hardening.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 冻结 `backend/app/modules/commission/service.py` 中当前 split 驱动下的 commission generation / rewrite 行为，只决定 split 生成、无 split fallback、rewritable-only update/delete 和 locked/settled row 边界。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-BE-02`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-generation-hardening-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-generation-hardening.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-05.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-05.md` is referenced for downstream audit wording alignment only; this wave does not claim or absorb QA ownership.
- Out of scope:
  - `backend/**`
  - `frontend/**`
  - any settlement/API/FE/schema/model implementation
- Shared ownership:
  - `No`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-05.md` remains QA-owned; any reference-only wording alignment does not transfer shared ownership into this wave
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-02`

## Current Code Facts

- `apply_commission_for_bill(...)`
  - when `T_CaseAgentSplit` rows exist for a case, it builds one target allocation per current split row and uses `_split_money_by_ratios(...)` to derive each allocation amount
  - when no split rows exist, it falls back to one allocation for `case.primary_agent_id` with `share_ratio = 100`
  - for each target allocation, it upserts by `case_id / agent_id / fee_type / rule_id`
  - existing rows are updated only when `_commission_is_rewritable(...)` returns `True`
  - extra rows for the same `case_id / rule_id / fee_type` are deleted only if they are not in the current target allocation set and remain rewritable
- `_commission_is_rewritable(...)`
  - terminal commission statuses are untouched
  - any commission already referenced by `CommissionSettleLine` is untouched

## Exact Closure Slice

- This task closes exactly:
  - freeze current split driven generation / rewrite behavior only

## Frozen Behavior Result

- Split rows present:
  - generate or update one commission row per current allocation
- Split rows absent:
  - fallback to one `primary_agent_id` row
- Rewrite scope:
  - only rewritable rows participate in update / delete
- Locked boundary:
  - terminal or settlement-linked rows remain untouched
- Recompute scope:
  - no extra settlement semantics are introduced in this slice
- Follow-up mapping:
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-05` for downstream audit-only validation of this frozen behavior

## Explicit Non-Closure Statement

- This task does NOT close:
  - settlement linkage changes
  - API contract changes
  - FE viewing/editing
  - report/payout/export
  - schema/model changes
  - QA execution or ownership transfer

## Remaining Follow-up Task IDs

- `COMMSPLIT-BE-03`
- `COMMSPLIT-FE-01`
- `COMMSPLIT-QA-05` (audit-only, downstream)

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] generation behavior explicit from current code facts
- [ ] fallback behavior explicit from current code facts
- [ ] locked/rewrite boundary explicit from current code facts
- [ ] follow-up mapping explicit
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Review current commission generation evidence before changing docs
- [ ] Update the generation hardening spec and plan only
- [ ] Keep follow-up stories explicit
- [ ] If updating `COMMSPLIT-QA-05.md`, limit the change to audit wording alignment only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
