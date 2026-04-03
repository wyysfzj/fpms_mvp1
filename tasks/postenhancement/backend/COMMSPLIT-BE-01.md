# COMMSPLIT-BE-01 — contract semantics freeze checkpoint。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-contract-semantics.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 冻结 `CaseAgentSplit -> commission generation` 的 contract semantics，只决定 split source-of-truth、`second_agent_id` 是否在 generation 中被 split rows 覆盖、fallback 语义、`share_ratio = 100` 上游不变量和 follow-up remapping。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-BE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-contract-semantics-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-contract-semantics.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md` is referenced for downstream audit wording alignment only; this wave does not claim QA ownership.
- Out of scope:
  - `backend/**`
  - `frontend/**`
  - any service/API/settlement/FE/schema/model implementation
- Shared ownership:
  - `No`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md` remains QA-owned; any reference-only wording alignment does not transfer shared ownership into this wave
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-01`

## Exact Closure Slice

- This task closes exactly:
  - freeze the `CaseAgentSplit -> commission generation` contract semantics only

## Frozen Contract Result

- Split rows present:
  - `CaseAgentSplit` is the active generation source-of-truth
  - split rows override `second_agent_id` for generation semantics
  - `second_agent_id` remains context-only for commission generation
- Split rows absent:
  - fallback to `primary_agent_id` only
- Generation precondition:
  - `share_ratio` total = `100` is an upstream generation invariant
- Historical semantics:
  - not included in the generation contract for this slice
- Invalid-state hardening:
  - deferred to later backend follow-up work
- Follow-up mapping:
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-04`

## Explicit Non-Closure Statement

- This task does NOT close:
  - commission calculation/recompute changes
  - settlement linkage changes
  - API contract changes
  - FE viewing/editing
  - report/payout/export
  - any schema/model changes

## Remaining Follow-up Task IDs

- `COMMSPLIT-BE-02`
- `COMMSPLIT-BE-03`
- `COMMSPLIT-FE-01`
- `COMMSPLIT-QA-04`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] source-of-truth semantics explicit
- [ ] fallback semantics explicit
- [ ] generation preconditions explicit
- [ ] follow-up mapping explicit
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Review existing case/commission contract evidence before changing docs
- [ ] Update the contract semantics spec and plan only
- [ ] Keep follow-up stories explicit
- [ ] If updating `COMMSPLIT-QA-04.md`, limit the change to audit wording alignment only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
