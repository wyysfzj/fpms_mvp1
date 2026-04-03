# COMMSPLIT-QA-03 — existing carrier reclassification close audit。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-existing-carrier-reclassification.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 审计 `COMMSPLIT-DB-01` 的证据、carrier assessment 结论与 follow-up remapping，确认 `CaseAgentSplit` 已被冻结为 `partial carrier`，并给出 reclassification-wave 级 `PASS / FAIL / BLOCKED` 结论。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-DB-01`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-03/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-existing-carrier-reclassification-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-existing-carrier-reclassification.md`
  - `tasks/postenhancement/backend/COMMSPLIT-DB-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md`
- Out of scope:
  - any product code change
  - any schema or service implementation
- Shared ownership:
  - `No`
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-DB-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-03`

## Exact Closure Slice

- This task closes exactly:
  - 对 existing-carrier reclassification wave 执行证据审计，确认 `CaseAgentSplit` 的 `partial carrier` 冻结判断与 follow-up remapping 已被冻结，并明确 implementation stories 仍未执行。

## Explicit Non-Closure Statement

- This task does NOT close:
  - schema/migration changes
  - ORM model changes
  - commission calculation changes
  - settlement linkage changes
  - API contract changes
  - frontend viewing/editing

## Remaining Follow-up Task IDs

- `None` for the QA audit task itself.
- This does not mean the broader commission-split program has no deferred work; the implementation follow-ups remain in `COMMSPLIT-DB-01` and its referenced deferred task IDs.

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] reclassification evidence mapped
- [ ] residual implementation stories listed
- [ ] final reclassification-wave status emitted
- [ ] verification passed
- [ ] artifacts generated

## Execution Checklist

- [ ] Confirm audit-only allowlist
- [ ] Re-run referenced task gates
- [ ] Check required evidence files exist
- [ ] Write close summary
- [ ] If needed, align QA-task wording with the frozen reclassification result and audit-only boundary
- [ ] Capture scoped audit diff
- [ ] Stop without editing product code
