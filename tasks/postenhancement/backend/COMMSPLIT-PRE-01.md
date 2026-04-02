# COMMSPLIT-PRE-01 — 多代理提成分成 prerequisite 冻结任务。

- Source: `docs/superpowers/plans/2026-04-02-commission-split-prerequisite.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 冻结 `P1 #5` 的 allocation carrier、ratio semantics、settlement linkage semantics，明确当前 `Case.second_agent_id`、`Commission.s1_rate/s2_rate` 与现有 settlement 结构都只是上下文，不是真实 split carrier，并将 active decomposition 改写为 prerequisite-first 形式。
- Covered items:
  - `P1 #5`
  - `FR-COM-03` (historical context only; not an additional implementation item in this wave)
- Allowlist:
  - `docs/superpowers/specs/2026-04-02-commission-split-prerequisite-design.md`
  - `docs/superpowers/plans/2026-04-02-commission-split-prerequisite.md`
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-01.md`
- Out of scope:
  - `backend/**`
  - `frontend/**`
  - any schema/migration file
  - any API/service/UI implementation
- Shared ownership:
  - `Yes` for the prerequisite planning docs and task definition files in this allowlist wave
  - `COMMSPLIT-QA-01` is reserved as the downstream serialized QA task, not a concurrent co-owner
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-PRE-01`

## Exact Closure Slice

- This task closes exactly:
  - 将 `P1 #5` 冻结为 prerequisite-heavy structural story，明确当前字段只能算上下文、不能视为真实 split carrier，并为后续 schema/calculation/FE follow-up stories 建立稳定边界。

## Explicit Non-Closure Statement

- This task does NOT close:
  - schema/migration implementation
  - commission allocation calculation
  - settlement linkage behavior
  - case-page split editor
  - commission reports / payout / export
  - any backend service, API, or UI implementation

## Remaining Follow-up Task IDs

- `COMMSPLIT-PRE-02`
- `COMMSPLIT-BE-01`
- `COMMSPLIT-BE-02`
- `COMMSPLIT-FE-01`
- `COMMSPLIT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] prerequisite semantics frozen
- [ ] follow-up stories named explicitly
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/COMMSPLIT-PRE-01/baseline_allowlist.diff`
- `artifacts/COMMSPLIT-PRE-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Update the design, plan, and task docs that are explicitly in the allowlist for this prerequisite wave
- [ ] Keep follow-up stories explicit
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
