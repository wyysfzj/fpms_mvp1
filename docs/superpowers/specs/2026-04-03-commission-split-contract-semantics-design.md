# P1 #5 多代理人提成分成 Contract Semantics Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend semantic-hardening before calculation and settlement follow-ups`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`COMMSPLIT-BE-01` 不是 calculation 或 settlement story，而是 contract semantics decision story。当前 repo 已经表现出：`CaseAgentSplit` 会被 commission generation 消费，split 行为空时会 fallback 到 `primary_agent_id`。本轮必须先冻结这些行为是否构成正式 contract，明确 `second_agent_id` 的地位、fallback 的合法性、以及 generation 的前置条件，然后再把 calculation / settlement follow-ups 缩窄。

## Assumptions

- 权威对象固定为：
  - `CaseAgentSplit -> commission generation contract`
- 第一轮判断标准固定为：
  - split 行存在时是否完全覆盖 `second_agent_id` 语义
  - split 行为空时是否只能回退到 `primary_agent_id`
  - `share_ratio = 100` 总和是否构成 generation 前置条件
  - commission service 是否只消费 current effective split，而不引入历史版本语义
  - 当前 contract 是否仍缺 error / invalid-state semantics
- 第一轮结果形态固定为：
  - `contract semantics decision`
  - `narrowed backend follow-up mapping`
- 第一轮最小闭环固定为：
  - split source-of-truth semantics
  - fallback semantics
  - generation preconditions
  - follow-up remapping
  - explicit deferred slices

## Scope

- 冻结 `CaseAgentSplit` 与 commission generation 之间的 contract semantics
- 明确 `second_agent_id` 在 generation 路径中的语义地位
- 明确 fallback 到 `primary_agent_id` 的 contract
- 明确 generation 前置条件与 invalid-state 边界

## Explicit Non-scope

- commission calculation/recompute changes
- settlement linkage changes
- API contract changes
- FE viewing/editing
- report/payout/export
- any schema/model changes

## Current Code Evidence

### Split consumption

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `_load_case_agent_splits(...)`
  - reads `T_CaseAgentSplit.agent_id`
  - reads `T_CaseAgentSplit.share_ratio`
  - does **not** read `Case.second_agent_id`

### Split-based commission generation

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `_split_money_by_ratios(...)`
  - `apply_commission_for_bill(...)`
  - with split rows: generates allocations from current effective split rows and divides `base_fee` by `share_ratio`
  - without split rows: falls back to one allocation with `primary_agent_id` and `100`

### Generation preconditions already enforced in case service

- [cases/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/service.py)
  - `validate_case_agent_splits(...)`
  - enforces:
    - unique `agent_id`
    - `role == Agent`
    - `share_ratio > 0 and <= 100`
    - `share_ratio` total = `100`
    - split members must be internal Agent-role users

### Case-side API exposure

- [cases/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/api.py)
  - reads and serializes split rows on case detail

## Contract Semantics Assessment

### Split source-of-truth semantics

- Frozen decision:
  - `CaseAgentSplit` is the active split source-of-truth for commission generation when split rows exist.
- Consequence:
  - when split rows exist, `second_agent_id` is context-only and does not act as a parallel generation source.
  - split rows override `second_agent_id` for generation semantics.

### Fallback semantics

- Frozen decision:
  - when split rows do not exist, commission generation falls back to `primary_agent_id` only.
- Consequence:
  - `second_agent_id` is not part of the no-split fallback path.

### Generation preconditions

- Frozen decision:
  - `share_ratio` total = `100` is an upstream generation invariant.
  - invalid split state must be blocked before generation rather than silently normalized during generation

### Historical semantics

- Frozen decision:
  - current generation consumes current effective split rows only
  - no historical split-version semantics are implied in this wave

### Invalid-state semantics

- Frozen decision:
  - `primary_agent_id` missing and no split rows is an invalid upstream condition that still needs explicit downstream hardening follow-up
  - split rows invalid at write time are already blocked by case-side validation

## Frozen Decision

- Split rows present:
  - override `second_agent_id` for generation purposes
- Split rows absent:
  - fallback to `primary_agent_id` only
- Generation precondition:
  - `share_ratio = 100` total is a required upstream invariant
- Historical semantics:
  - not included
- Invalid-state hardening:
  - deferred to follow-up backend work

## Narrowed Follow-up Mapping

- `COMMSPLIT-BE-01`
  - contract semantics freeze only
- `COMMSPLIT-BE-02`
  - calculation / recompute hardening
- `COMMSPLIT-BE-03`
  - settlement linkage semantics if still needed
- `COMMSPLIT-FE-01`
  - viewing/editing

## Deferred Slices Ledger

- `commission calculation/recompute changes`
- `settlement linkage changes`
- `API contract changes`
- `FE viewing/editing`
- `report/payout/export`
- `any schema/model changes`

## Phase Compatibility Assessment

- This contract-freeze wave is compatible with current Phase constraints because it is document-only.
- It does not require schema changes.
- It narrows later backend work rather than expanding the current slice.

## Risks / Blockers

- If `BE-01` is skipped, later calculation or settlement work will continue to rely on implicit assumptions.
- If `second_agent_id` is not explicitly demoted to context-only when split rows exist, future implementations may accidentally treat it as a second source.
- If invalid-state semantics remain unnamed, later backend work may silently encode policy without a frozen contract.

## Exact Closure Slice Candidates

### Preferred first slice

- `COMMSPLIT-BE-01`
  - freeze `CaseAgentSplit -> commission generation` contract semantics only

### Explicit non-closure

- no calculation/recompute patch
- no settlement patch
- no API patch
- no frontend patch
- no schema/model patch
- no report/payout/export patch

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a semantics-freeze story, not an implementation-heavy backend story.
