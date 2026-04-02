# COMMSPLIT-QA-02 — durable carrier decision close audit。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-durable-carrier-decision.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 审计 `COMMSPLIT-PRE-02` 的证据、推荐结论与 residual implementation story 命名，确认 `CaseAgentSplit` 与 `COMMSPLIT-DB-01` 已被冻结，并给出 decision-wave 级 `PASS / FAIL / BLOCKED` 结论。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-PRE-02`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-02/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-durable-carrier-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-durable-carrier-decision.md`
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md`
- Out of scope:
  - any product code change
  - any schema or service implementation
- Shared ownership:
  - `No`
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-PRE-02`
  - `./scripts/task_validate.sh COMMSPLIT-QA-02`

## Exact Closure Slice

- This task closes exactly:
  - 对 durable carrier decision wave 执行证据审计，确认 carrier recommendation 为 `CaseAgentSplit`、DB prerequisite recommendation 为 `COMMSPLIT-DB-01`，并明确 residual implementation stories 仍未执行。

## Explicit Non-Closure Statement

- This task does NOT close:
  - DB prerequisite implementation
  - case API contract
  - commission calculation
  - settlement behavior changes
  - frontend viewing/editing

## Remaining Follow-up Task IDs

- `None` for the QA audit task itself.
- This does not mean the broader commission-split program has no deferred work; the implementation follow-ups remain in `COMMSPLIT-PRE-02` and its referenced deferred task IDs.

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] decision evidence mapped
- [ ] residual implementation stories listed
- [ ] final decision-wave status emitted
- [ ] verification passed
- [ ] artifacts generated

## Execution Checklist

- [ ] Confirm audit-only allowlist
- [ ] Re-run referenced task gates
- [ ] Check required evidence files exist
- [ ] Write close summary
- [ ] If needed, align QA-task wording with the frozen decision and audit-only boundary
- [ ] Capture scoped audit diff
- [ ] Stop without editing product code
