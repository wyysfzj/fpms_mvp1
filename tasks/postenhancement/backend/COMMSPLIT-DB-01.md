# COMMSPLIT-DB-01 — existing carrier reclassification checkpoint。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-existing-carrier-reclassification.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 评估现有 `CaseAgentSplit` 是否已经构成 durable carrier，并冻结 reclassification 结果，只决定旧的 `COMMSPLIT-DB-01 = mandatory DB prerequisite` 结论应被保留、缩窄、改名还是移除。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-DB-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-existing-carrier-reclassification-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-existing-carrier-reclassification.md`
  - `tasks/postenhancement/backend/COMMSPLIT-DB-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md` is referenced for downstream audit wording alignment only; this wave does not claim QA ownership.
- Out of scope:
  - `backend/**`
  - `frontend/**`
  - any schema/model/API/service/UI implementation
- Shared ownership:
  - `No`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md` remains QA-owned; any reference-only wording alignment does not transfer shared ownership into this wave
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-DB-01`

## Exact Closure Slice

- This task closes exactly:
  - assess the existing `CaseAgentSplit` carrier status and freeze the reclassification result only

## Frozen Assessment Result

- Carrier classification:
  - `partial carrier`
- Code facts used for the freeze:
  - `backend/app/modules/cases/models.py` persists `T_CaseAgentSplit` as a real table with `case_id`, `agent_id`, `role`, and `share_ratio`
  - `backend/app/modules/cases/service.py` validates split membership, role, and ratio rules, deletes and recreates the current effective split rows, and enforces `share_ratio` total = `100`
  - `backend/app/modules/cases/api.py` reads and serializes the split rows on case detail
  - `backend/app/modules/commission/service.py` consumes the split rows for commission allocation and falls back to `primary_agent_id` only when no split rows exist
- Reclassification result:
  - `COMMSPLIT-DB-01` is narrowed and renamed from a mandatory DB prerequisite into an existing-carrier reclassification checkpoint
  - the old mandatory DB-prerequisite meaning is removed
- Why this is not `auxiliary-only`:
  - the structure is persisted, validated, serialized, and consumed by commission logic
- Why this is not a fully closed durable source-of-truth:
  - the current code only proves current-effective split rows and fallback allocation semantics; broader settlement / report / full domain source-of-truth semantics remain deferred
- Follow-up mapping:
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-03`

## Decision Record

- Existing carrier status to evaluate:
  - `真实 durable carrier`
  - `部分 carrier，但语义不足`
  - `仅是 UI/case 辅助结构`
- Reclassification outputs allowed:
  - keep
  - narrow
  - rename
  - remove

## Explicit Non-Closure Statement

- This task does NOT close:
  - schema/migration changes
  - ORM model changes
  - commission calculation changes
  - settlement linkage changes
  - API contract changes
  - FE viewing/editing
  - report/payout/export

## Remaining Follow-up Task IDs

- `COMMSPLIT-BE-01`
- `COMMSPLIT-BE-02`
- `COMMSPLIT-BE-03`
- `COMMSPLIT-FE-01`
- `COMMSPLIT-QA-03`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] existing carrier status explicit
- [ ] reclassification result explicit
- [ ] follow-up task mapping explicit
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Review existing case/commission evidence before changing docs
- [ ] Update the reclassification spec and plan only
- [ ] Keep follow-up stories explicit
- [ ] If updating `COMMSPLIT-QA-03.md`, limit the change to audit wording alignment only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
