# COMMSPLIT-PRE-02 — 多代理提成 durable carrier decision。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-durable-carrier-decision.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 比较 durable carrier 候选，冻结推荐选择为 `CaseAgentSplit` 明细表，并明确必须拆出 `COMMSPLIT-DB-01` 作为真正的 schema prerequisite task。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-PRE-02`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-durable-carrier-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-durable-carrier-decision.md`
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md` is referenced for downstream audit wording alignment only; this wave does not claim QA ownership.
- Out of scope:
  - `backend/**`
  - `frontend/**`
  - any migration/model/API/service/UI implementation
- Shared ownership:
  - `No`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md` remains QA-owned; any reference-only wording alignment does not transfer shared ownership into this wave
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-PRE-02`

## Exact Closure Slice

- This task closes exactly:
  - 比较并冻结 durable split carrier 的三种候选方案，明确推荐 carrier 选择为 `CaseAgentSplit` 明细表，并正式判断必须拆出 `COMMSPLIT-DB-01` 作为 schema prerequisite。

## Decision Record

- Recommended carrier:
  - `CaseAgentSplit`
- Rejected for this MVP1 slice:
  - `CommissionAllocation`
  - `Settlement-linked allocation`
- Schema prerequisite recommendation:
  - `COMMSPLIT-DB-01` is mandatory before any DB, BE, or FE implementation

## Explicit Non-Closure Statement

- This task does NOT close:
  - migration
  - ORM model
  - case API contract
  - commission calculation
  - settlement behavior changes
  - FE editing/viewing
  - reports / payout / export
  - any product implementation of the durable carrier itself

## Remaining Follow-up Task IDs

- `COMMSPLIT-DB-01`
- `COMMSPLIT-BE-01`
- `COMMSPLIT-BE-02`
- `COMMSPLIT-FE-01`
- `COMMSPLIT-QA-02`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] carrier recommendation explicit
- [ ] DB prerequisite recommendation explicit
- [ ] deferred implementation stories explicit
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/COMMSPLIT-PRE-02/baseline_allowlist.diff`
- `artifacts/COMMSPLIT-PRE-02/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Update the decision spec and plan only
- [ ] Keep follow-up stories explicit
- [ ] If updating `COMMSPLIT-QA-02.md`, limit the change to audit wording alignment only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
