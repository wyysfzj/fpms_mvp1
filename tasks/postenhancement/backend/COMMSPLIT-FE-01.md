# COMMSPLIT-FE-01 — frontend exposure checkpoint。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-frontend-exposure.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 冻结前端中多代理 split 的 viewing/editing 归属，只决定 case-side viewing/editing ownership、`CaseAgentSplit` 与 `second_agent_id` 的 FE 边界，以及 settlement 页面不承担 split 编辑职责。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-FE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-frontend-exposure-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-frontend-exposure.md`
  - `tasks/postenhancement/backend/COMMSPLIT-FE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-07.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-07.md` is referenced for downstream audit wording alignment only; this wave does not claim or absorb QA ownership.
- Out of scope:
  - `frontend/**`
  - `backend/**`
  - any Vue/API/router/report/settlement implementation
- Shared ownership:
  - `No`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-07.md` remains QA-owned; any reference-only wording alignment does not transfer shared ownership into this wave
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-FE-01`

## Current Code Facts

- `cases.ts / cases.types.ts`
  - already support `agent_splits`, `primary_agent_id`, and `second_agent_id`
- `CaseEdit.vue`
  - already exposes `代理人分摊` and embeds `CaseAgentSplitEditor`
- `CaseAgentSplitEditor.vue`
  - already provides row-level split editing UI structure
- `CaseCreate.vue`
  - clearly exposes `primary_agent_id` / `second_agent_id`
  - split exposure is not yet proven equivalent to `CaseEdit.vue`
- `CaseDetail.vue`
  - visibly shows `primary_agent_id` / `second_agent_id`
  - does not yet prove explicit `agent_splits` viewing exposure
- `frontend/src/modules/commission/**`
  - does not currently own split editing

## Exact Closure Slice

- This task closes exactly:
  - freeze frontend viewing/editing exposure ownership only

## Frozen Behavior Result

- Editing ownership:
  - stays on case-side pages
- Viewing ownership:
  - also prioritizes case-side pages
- FE split source object:
  - `CaseAgentSplit` is primary
- Context-only field:
  - `second_agent_id` remains context/legacy auxiliary field
- Settlement boundary:
  - settlement pages do not own split editing
- Follow-up mapping:
  - `COMMSPLIT-QA-07` for downstream audit-only validation
  - implementation follow-ups remain separate and deferred

## Explicit Non-Closure Statement

- This task does NOT close:
  - Vue/page/component implementation
  - shared API/types wiring
  - router/menu changes
  - report/payout/export UI
  - settlement workflow UI enhancement
  - QA execution or ownership transfer

## Remaining Follow-up Task IDs

- `COMMSPLIT-QA-07` (audit-only, downstream)

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] viewing ownership explicit from current code facts
- [ ] editing ownership explicit from current code facts
- [ ] `CaseAgentSplit` vs `second_agent_id` boundary explicit
- [ ] follow-up mapping explicit
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Review current frontend exposure evidence before changing docs
- [ ] Update the frontend exposure spec and plan only
- [ ] Keep follow-up stories explicit
- [ ] If updating `COMMSPLIT-QA-07.md`, limit the change to audit wording alignment only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
