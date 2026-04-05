# GF-BATCH-INSTR-QA-01 — grant-fee batch instruction audit

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-batch-instruction.md`
- Type: `qa close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `GF-BATCH-INSTR-BE-01` 与 `GF-BATCH-INSTR-FE-01` 的证据、gate 和 exact closure，确认这轮只关闭批量 `PAY / ABANDON` slice。
- Exact closure slice:
  - 审计 BE/FE evidence
  - 生成 `artifacts/GF-BATCH-INSTR-QA-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不扩展到通知函生成、detail/edit、bill generation
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/GF-BATCH-INSTR-BE-01/**`
  - `artifacts/GF-BATCH-INSTR-FE-01/**`
  - `artifacts/GF-BATCH-INSTR-QA-01/**`
  - `tasks/postenhancement/backend/GF-BATCH-INSTR-QA-01.md`
- Verification:
  - `./scripts/task_validate.sh GF-BATCH-INSTR-BE-01`
  - `./scripts/task_validate.sh GF-BATCH-INSTR-FE-01`
  - `./scripts/task_validate.sh GF-BATCH-INSTR-QA-01`

## Execution Checklist

- [ ] Confirm backend and frontend closures match the approved batch slice
- [ ] Confirm non-closure boundaries were respected
- [ ] Record exact closure and gate results in summary
