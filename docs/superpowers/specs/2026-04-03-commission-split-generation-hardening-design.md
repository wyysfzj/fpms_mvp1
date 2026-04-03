# P1 #5 多代理人提成分成 Generation Hardening Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend behavior hardening before settlement follow-up`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`COMMSPLIT-BE-02` 不是 settlement 或 frontend story，而是 commission generation / rewrite behavior hardening story。当前 repo 中 `apply_commission_for_bill()` 已经在当前 split 下创建、更新、删除 agent 级 commission 记录，并用 `_commission_is_rewritable()` 约束可重写边界。本轮必须先冻结这些行为应构成什么正式语义，尤其是 current split 驱动生成、无 split 单代理 fallback、locked/settled 记录不可重写、以及 stale allocation 记录何时允许被删除。

## Assumptions

- 权威对象固定为：
  - `commission generation / rewrite behavior under current split`
- 第一轮判断标准固定为：
  - split 行存在时是否按 current split 生成每 agent 一条 commission
  - 无 split 时是否保持单代理 fallback
  - 已进入 settlement line 的 commission 是否必须保持不可重写
  - 未冻结 commission 是否允许按 current split 重新生成 / 更新 / 删除
  - recompute 路径是否与 generation 路径共享相同 split 语义边界
- 第一轮结果形态固定为：
  - `behavior hardening decision`
  - `narrowed implementation slice`
- 第一轮最小闭环固定为：
  - generation behavior
  - recompute boundary
  - locked/frozen boundary
  - create / update / delete semantics
  - explicit deferred slices

## Scope

- 冻结 split 驱动 generation 的目标行为
- 冻结 rewritable-only update / delete 边界
- 明确 stale allocation records 的处理语义
- 明确 recompute 与 generation 的边界关系

## Explicit Non-scope

- settlement linkage changes
- API contract changes
- FE viewing/editing
- report/payout/export
- schema/model changes

## Current Code Evidence

### Generation and rewrite entrypoint

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `apply_commission_for_bill(...)`

### Split-based generation behavior

- With split rows:
  - loads `T_CaseAgentSplit.agent_id, share_ratio`
  - computes `split_amounts`
  - creates or updates one `Commission` row per allocation

### No-split fallback

- With no split rows:
  - generates one allocation with `agent_id = case.primary_agent_id`
  - uses `share_ratio = 100`

### Rewrite boundary

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `_commission_is_rewritable(...)`
- Current behavior:
  - terminal statuses are not rewritable
  - any commission already referenced by `CommissionSettleLine` is not rewritable

### Stale allocation cleanup

- `apply_commission_for_bill(...)`
  - deletes existing commission rows for the same `case_id / rule_id / fee_type` when their `agent_id` is no longer in the current target allocation set and the row is still rewritable

### Recompute presence

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `recompute_commission_settleable(...)`
- Current assessment:
  - settleable-state recompute exists
  - broader split-driven record rewrite semantics still need explicit freezing

## Behavior Hardening Assessment

### Generation behavior

- Frozen decision:
  - current split drives one commission row per agent allocation
  - no split keeps single-agent fallback

### Rewrite behavior

- Frozen decision:
  - only rewritable commission rows may be updated or deleted when current split changes

### Locked / settled boundary

- Frozen decision:
  - commissions in terminal states or already referenced by `CommissionSettleLine` remain untouched

### Stale-target delete semantics

- Frozen decision:
  - stale commission rows may be deleted only when they no longer belong to the current target allocation set and remain rewritable

### Recompute boundary

- Frozen decision:
  - this wave freezes generation / rewrite semantics only
  - any additional settleable-state or settlement-driven recompute semantics remain follow-up work unless they are already implied by the existing rewrite boundary

## Frozen Decision

- Split rows present:
  - generate or update one commission row per current allocation
- Split rows absent:
  - keep one-row `primary_agent_id` fallback
- Rewrite scope:
  - only rewritable rows participate in update / delete
- Locked boundary:
  - terminal or settlement-linked rows are untouched
- Recompute scope:
  - no extra settlement semantics are introduced in this slice

## Narrowed Follow-up Mapping

- `COMMSPLIT-BE-02`
  - generation / rewrite behavior hardening
- `COMMSPLIT-BE-03`
  - settlement linkage semantics if still needed
- `COMMSPLIT-FE-01`
  - viewing/editing
- `COMMSPLIT-QA-05`
  - serialized audit-only close wave for the generation-hardening slice

## Deferred Slices Ledger

- `settlement linkage changes`
- `API contract changes`
- `FE viewing/editing`
- `report/payout/export`
- `schema/model changes`

## Phase Compatibility Assessment

- This design wave is compatible with current constraints because it only freezes backend behavior semantics.
- It does not require schema changes.
- It narrows the implementation slice instead of expanding it into settlement or frontend work.

## Risks / Blockers

- If this behavior is not frozen first, later implementation may accidentally rewrite locked rows or mix settlement semantics into generation.
- If stale-row delete semantics are left implicit, later patches may incorrectly preserve or remove rows under split changes.
- If recompute scope is not narrowed now, later work may stretch this story into a settlement story.

## Exact Closure Slice Candidates

### Preferred first slice

- `COMMSPLIT-BE-02`
  - freeze current split driven generation / rewrite behavior only

### Explicit non-closure

- no settlement linkage patch
- no API patch
- no frontend patch
- no report/payout/export patch
- no schema/model patch

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a backend behavior-hardening slice, not a settlement or frontend story.
