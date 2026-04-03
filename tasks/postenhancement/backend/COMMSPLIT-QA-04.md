# COMMSPLIT-QA-04 — contract semantics close audit。

- Source: `docs/superpowers/plans/2026-04-03-commission-split-contract-semantics.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 审计 `COMMSPLIT-BE-01` 的证据、contract freeze 结论与 follow-up remapping，确认 split source-of-truth、`second_agent_id` 生成覆盖语义、fallback 和 `share_ratio = 100` 上游不变量已被冻结，并给出 contract-wave 级 `PASS / FAIL / BLOCKED` 结论。
- Covered items:
  - `P1 #5`
  - `COMMSPLIT-BE-01`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-04/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-contract-semantics-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-contract-semantics.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md`
- Out of scope:
  - any product code change
  - any service/API/settlement implementation
- Shared ownership:
  - `No`
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-04`

## Exact Closure Slice

- This task closes exactly:
  - 对 contract-freeze wave 执行证据审计，确认 split source-of-truth、`second_agent_id` 覆盖语义、fallback 和 `share_ratio = 100` 上游不变量的冻结结论与 follow-up remapping 已被冻结，并明确 implementation stories 仍未执行。

## Explicit Non-Closure Statement

- This task does NOT close:
  - calculation/recompute changes
  - settlement linkage changes
  - API contract changes
  - frontend viewing/editing
  - schema/model changes

## Remaining Follow-up Task IDs

- `None` for the QA audit task itself.
- This does not mean the broader commission-split program has no deferred work; the implementation follow-ups remain in `COMMSPLIT-BE-01` and its referenced deferred task IDs.

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] contract-freeze evidence mapped
- [ ] residual implementation stories listed
- [ ] final contract-wave status emitted
- [ ] verification passed
- [ ] artifacts generated

## Execution Checklist

- [ ] Confirm audit-only allowlist
- [ ] Re-run referenced task gates
- [ ] Check required evidence files exist
- [ ] Write close summary
- [ ] If needed, align QA-task wording with the frozen contract result and audit-only boundary
- [ ] Capture scoped audit diff
- [ ] Stop without editing product code
