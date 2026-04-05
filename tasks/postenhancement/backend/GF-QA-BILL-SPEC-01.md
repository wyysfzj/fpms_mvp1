# GF-QA-BILL-SPEC-01 — 授权费 bill linkage 语义审核

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-bill-linkage.md`
- Type: `qa close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `GF-BILL-SPEC-01` 的 evidence 与文档输出，确认 grant-fee bill linkage semantics 已冻结，并生成 close summary。
- Exact closure slice:
  - 审计 `GF-BILL-SPEC-01` 的 evidence 与 doc diff
  - 生成 `artifacts/GF-QA-BILL-SPEC-01/**`
- Explicit non-closure:
  - 不做任何产品代码实现
  - 不扩展到 bill linkage 真正实现
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `tasks/postenhancement/backend/GF-QA-BILL-SPEC-01.md`
  - `artifacts/GF-BILL-SPEC-01/**`
  - `artifacts/GF-QA-BILL-SPEC-01/**`
- Verification:
  - `./scripts/task_validate.sh GF-BILL-SPEC-01`
  - `./scripts/task_validate.sh GF-QA-BILL-SPEC-01`

## Execution Checklist

- [ ] Confirm bill-linkage source-of-truth is explicit
- [ ] Confirm no state-machine expansion was absorbed
- [ ] Confirm first follow-up story is explicit
- [ ] Record exact closure / non-closure in summary
