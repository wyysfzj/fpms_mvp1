# P1 #5 多代理人提成分成 Settlement Linkage Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend settlement semantics before frontend follow-up`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`COMMSPLIT-BE-03` 不是 settlement API 或 frontend story，而是 multi-agent split 下 `Commission -> is_settleable -> CommissionSettleLine` 的 settlement linkage semantics story。当前 repo 已经存在 `Commission`、`CommissionSettlement`、`CommissionSettleLine`、`recompute_commission_settleable(...)` 与 `generate_commission_settlement_lines(...)`，但这些行为尚未被正式冻结为 row-level settlement contract。

## Assumptions

- 权威对象固定为：
  - `commission-row level settlement linkage semantics under current split`
- 第一轮判断标准固定为：
  - `is_settleable` 是否按每条 commission 独立计算
  - 同一 `bill/case` 下多个 agent commission 是否允许分别进入 settlement
  - 已进入 `CommissionSettleLine` 的记录是否必须保持不可重写
  - split 变化后，未 settlement-linked 的 commission 是否可重新进入新的 settleable 判断
  - settlement 是否只消费当前已生成的 commission rows，而不回头重新解释 split 行
- 第一轮结果形态固定为：
  - `settlement linkage decision`
  - `narrowed backend follow-up mapping`
- 第一轮最小闭环固定为：
  - `settleable` 计算语义
  - `Commission -> CommissionSettleLine` 进入条件
  - linked / non-linked rows 的边界
  - follow-up remapping
  - explicit deferred slices

## Scope

- 冻结 row-level `settleable` 语义
- 冻结 `Commission -> CommissionSettleLine` 的进入条件
- 冻结 settlement-linked rows 与 non-linked rows 的重写边界
- 明确 settlement 只消费已生成 commission rows 的语义

## Explicit Non-scope

- settlement/API implementation changes
- FE viewing/editing
- report/payout/export
- schema/model changes
- new settlement workflow UI

## Current Code Evidence

### Settleable carrier

- [commission/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/models.py)
  - `Commission.is_settleable`
  - `Commission.settleable_date`

### Settlement models

- [commission/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/models.py)
  - `CommissionSettlement`
  - `CommissionSettleLine`
- Current structural fact:
  - `(settlement_id, commission_id)` is unique
  - settlement lines are already row-level per `commission_id`

### Settleable recompute

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `recompute_commission_settleable(...)`
- Current behavior:
  - recomputes `is_settleable` and `settleable_date` from current commission row state

### Settlement line generation

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `generate_commission_settlement_lines(...)`
- Current behavior:
  - filters `Commission.is_settleable == True`
  - applies period and agent filters on existing commission rows
  - generates one `CommissionSettleLine` per eligible commission row

### Rewrite boundary already implied

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - `_commission_is_rewritable(...)`
- Current behavior:
  - any commission already referenced by `CommissionSettleLine` is not rewritable

## Settlement Linkage Assessment

### Row-level settleable semantics

- Frozen decision:
  - `is_settleable` is evaluated per commission row, not per case-level split bundle

### Independent settlement entry

- Frozen decision:
  - multiple agent commissions from the same `bill/case` may independently become settleable and independently enter settlement

### Linked-row boundary

- Frozen decision:
  - once a commission row is referenced by `CommissionSettleLine`, it stays outside rewrite scope

### Split-change boundary

- Frozen decision:
  - split changes may affect only commission rows that are not yet settlement-linked
  - settlement-linked rows are consumed outputs, not reinterpreted split definitions

### Settlement source-of-truth boundary

- Frozen decision:
  - settlement consumes already-generated commission rows only
  - it does not re-read or reinterpret `CaseAgentSplit` as a parallel source-of-truth

## Frozen Decision

- `is_settleable` remains a per-commission-row state
- same `bill/case` may produce multiple independently settleable agent-level commission rows
- `CommissionSettleLine` generation stays row-based by `commission_id`
- settlement-linked rows remain non-rewritable
- settlement consumes current commission rows, not split definitions directly

## Narrowed Follow-up Mapping

- `COMMSPLIT-BE-03`
  - settlement linkage semantics freeze
- `COMMSPLIT-FE-01`
  - viewing/editing and downstream exposure
- `COMMSPLIT-QA-06`
  - serialized audit-only close wave for the settlement-linkage slice

## Deferred Slices Ledger

- `settlement/API implementation changes`
- `FE viewing/editing`
- `report/payout/export`
- `schema/model changes`
- `new settlement workflow UI`

## Phase Compatibility Assessment

- This design wave is compatible with current constraints because it only freezes backend settlement semantics.
- It does not require schema changes.
- It narrows the implementation slice instead of expanding it into API, frontend, or payout work.

## Risks / Blockers

- If settlement semantics are not frozen first, later implementation may silently mix row-level commission semantics with case-level split semantics.
- If linked-row immutability remains implicit, later patches may accidentally rewrite settlement-consumed rows.
- If settlement is not explicitly treated as a consumer of commission rows only, later work may incorrectly make it reinterpret `CaseAgentSplit`.

## Exact Closure Slice Candidates

### Preferred first slice

- `COMMSPLIT-BE-03`
  - freeze row-level settlement linkage semantics only

### Explicit non-closure

- no settlement/API patch
- no frontend patch
- no report/payout/export patch
- no schema/model patch
- no new settlement workflow UI

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a backend settlement-linkage semantics slice, not a settlement API, frontend, or payout story.
