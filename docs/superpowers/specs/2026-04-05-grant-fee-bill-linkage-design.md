# Grant Fee Bill Linkage Semantics Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `semantics freeze before linkage implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`GF-RESIDUAL-SPEC-01` 已明确 `GF-BILL` 是 `#15 授权费管理` 的下一类 residual，但当前 repo 只有通用 billing 链路：

- `POST /bills/from-drafts`
- `BillItem.draft_id`
- `BillDetail.source_draft_ids / primary_draft_id`

还没有 grant-fee 专属的 bill linkage authority。现在不能直接实现“授权费已开账单/已回款”之类行为，否则会把 bill carrier、grant-fee 状态回投、前端展示和更宽的 receivable semantics 混成一条故事。当前必须先冻结：

- `GF-BILL` 的 source-of-truth
- draft-to-bill 回投边界
- grant-fee task 在 bill linkage 第一轮里到底关闭哪一个最小行为

## Assumptions

- 当前可复用的通用 billing authority 已存在：
  - `POST /api/v1/bills/from-drafts`
  - `BillItem.draft_id`
  - `BillDetail.source_draft_ids`
- 当前 grant-fee draft authority 已存在：
  - `FeeDraft.draft_type == "GRANT_FEE"`
  - `FeeItem.remark = "GRANT_FEE_TASK:<task_id>"`
- 第一轮 bill linkage 不自动包含：
  - payment / receipt semantics
  - bad debt semantics
  - document / reminder linkage

## Scope

- 冻结 grant-fee bill linkage 的 source-of-truth
- 冻结 `GrantFeeTask -> FeeDraft -> Bill` 的最小回投语义
- 冻结第一轮 in-scope 状态回投和 FE 展示边界
- 推荐一个最小 bill-linkage follow-up story

## Explicit Non-scope

- 不做任何 billing / grant-fee 产品实现补丁
- 不做 receipt / payment semantics
- 不做 document/reminder linkage
- 不更新 `#15` close decision

## Current Carrier Assessment

### Available

- billing generation:
  - `POST /api/v1/bills/from-drafts`
- bill lineage:
  - `BillItem.draft_id`
  - `BillDetail.source_draft_ids`
  - `BillDetail.primary_draft_id`
- grant-fee lineage:
  - `FeeDraft.draft_type == "GRANT_FEE"`
  - `FeeItem.remark = "GRANT_FEE_TASK:<task_id>"`
  - grant-fee worklist already stores `draft_generated`

### Missing as explicit contract

- whether bill-created proof should change grant-fee task state
- whether a new task state is needed in first-round bill linkage
- whether first-round FE only needs visibility or an actual bill-generation trigger

## Authority Freeze

### Bill linkage source-of-truth

- 第一轮 `GF-BILL` authority 采用：
  - `BillItem.draft_id -> FeeDraft.id`
  - with `FeeDraft.draft_type == "GRANT_FEE"`
- `Bill` existence without grant-fee draft lineage does not count
- direct `CaseReceipt` / `Payment` rows do not count as bill-linkage proof for this slice

### Grant-fee lineage back to task

- `GrantFeeTask -> FeeDraft` authority continues to use:
  - `FeeItem.remark = "GRANT_FEE_TASK:<task_id>"`
- therefore first-round bill linkage can deterministically answer:
  - whether a grant-fee task’s generated draft has entered at least one bill

### First-round bill-linkage product rule

- first-round `GF-BILL` should **not** create a new grant-fee state
- first-round closure should remain narrower:
  - expose one deterministic “已开账单” visibility/entry slice for tasks whose grant-fee draft has bill lineage
- rationale:
  - current state machine only covers:
    - `OPEN`
    - `WAITING_CLIENT`
    - `READY_TO_DRAFT`
    - `DRAFT_GENERATED`
    - `DONE`
  - adding a new billed state would be a separate state-machine story, not linkage-first

## Recommended First Bill-linkage Slice

- `GF-BILL-VIS-01`
- exact closure candidate:
  - add one backend-visible derived flag or projection for “grant-fee draft already billed”
  - expose one FE visibility block / entry on the existing worklist

### Why this is recommended first

- it keeps the first bill-linkage slice observational, not state-machine-expanding
- it stays narrower than “generate bill from grant-fee page”
- it avoids mixing receivable and receipt semantics
- it preserves current `grant_fees` worklist authority

## Residuals Explicitly Deferred

- bill-generation trigger from the grant-fee page
- new `BILLED` or equivalent task state
- payment / receipt follow-through
- document / reminder linkage
- detail/edit UI

## SQLite / Phase Compatibility Assessment

- This semantics-freeze story is doc-only and compatible
- The recommended first bill-linkage slice appears achievable without schema change
- If a later story wants a new billed state, that must be split as a state-machine follow-up, not absorbed into linkage visibility

## Risks / Blockers

- treating generic bill existence as grant-fee-specific bill linkage proof
- letting bill linkage silently redefine the grant-fee state machine
- folding bill visibility, bill generation trigger, and receipt semantics into one story

## Exact Closure Slice Candidates

### Preferred

- `GF-BILL-SPEC-01`
  - freeze grant-fee bill linkage semantics and first follow-up recommendation

### Explicit non-closure

- no product implementation
- no state-machine expansion
- no receipt/payment semantics

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
