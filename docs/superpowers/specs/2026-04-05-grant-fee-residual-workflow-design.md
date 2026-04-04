# P2 #15 授权费管理 Residual Workflow Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `residual decomposition after implemented first-round workflow`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#15 授权费管理` 当前已经不能诚实地描述为“缺模型 + 缺完整 workflow”。`GF-PRE / GF-SM / GF-WL / GF-DRAFT` 已形成第一轮真实产品闭环：有 `T_GrantFeeTask` 承载、有主干状态机、有 worklist 页面，也有最小 `GrantFeeTask -> FeeDraft` 生成链路。但对照 `FPMS SPEC 2.0` 中“授权费管理”的完整业务宽度，当前 family 仍缺 post-draft 之后的多条 workflow 语义，因此下一步不应重做已完成 slice，而应先冻结 strict residual workflow map。

## Assumptions

- first-round close authority 固定为：
  - `GFPRE-*`
  - `GFSM-*`
  - `GFWL-*`
  - `GFDRAFT-*`
- 当前 grant-fee 第一轮权威产品证据固定为：
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
- 关闭标准继续固定为：
  - 只有真实产品行为存在，才允许新增 residual capability 计入 closure

## Scope

- 对 `#15` 做 strict residual workflow map
- 明确 first-round already closed slices
- 明确 post-draft 之后仍缺的 workflow breadth
- 推荐一个最小 residual follow-up story

## Explicit Non-scope

- 不重做 `GFPRE-*`
- 不重做 `GFSM-*`
- 不重做 `GFWL-*`
- 不重做 `GFDRAFT-*`
- 不做任何 grant-fee 产品实现补丁
- 不触发 `#15` close update

## Current Implemented Slice

### Existing product evidence

- prerequisite / carrier:
  - `T_GrantFeeTask`
  - `GrantFeeTask.Read / GrantFeeTask.Write`
- state machine:
  - `mark_waiting_client`
  - `record_pay_instruction`
  - `record_abandon_instruction`
  - `mark_draft_generated`
  - `mark_done`
- worklist:
  - `GET /api/v1/grant-fee-tasks/list`
  - `GrantFeeTaskList.vue`
- draft linkage:
  - `POST /api/v1/grant-fee-tasks/{task_id}/generate-draft`
  - idempotent `FeeDraft / FeeItem` minimal generation

### Already closed under first-round interpretation

- grant-fee task carrier exists
- minimal worklist/query exists
- minimal state transitions exist
- minimal draft-generation trigger exists
- workbench page allows:
  - 查看
  - 筛选
  - 单行生成草单

## Residual Workflow Gap

### Residual breadth still open

- post-draft downstream lifecycle breadth
- bill linkage / receivable follow-through
- document / reminder linkage
- detail/edit capability
- richer frontend action execution beyond single draft-generation trigger

### Residual buckets

#### Residual bucket A — post-draft task transition semantics

- after `DRAFT_GENERATED`, what exact product action closes the operational task
- whether `mark_done` remains manual-only or requires downstream proof
- what user-visible state/action path should exist on the worklist page

#### Residual bucket B — bill linkage

- whether grant-fee workflow needs explicit `FeeDraft -> Bill` carrier feedback
- whether a bill-generated or billed state is required
- whether first follow-up should stay entirely backend-side

#### Residual bucket C — document / reminder linkage

- grant-fee-specific reminder or notice outputs
- document generation or dispatch integration

#### Residual bucket D — detail/edit / batch actions

- row detail page or drawer
- edit corrections
- bulk selection / bulk execution
- failure retry affordances

## Recommended First Residual Slice

- `GF-POSTDRAFT-01`
- exact closure candidate:
  - freeze and implement one post-draft workflow rule after `DRAFT_GENERATED`
  - keep it inside current `grant_fees` backend ownership

### Why this is recommended first

- current first-round chain already ends at `generate-draft`
- the next honest workflow question is what “done” means after draft generation
- it is narrower than bill linkage, document linkage, or detail/edit expansion
- it preserves current worklist page authority instead of opening a new UI surface

## Residuals Explicitly Deferred

- bill linkage
- document/reminder linkage
- detail/edit page
- batch actions
- reporting / analytics
- export / print

## SQLite / Phase Compatibility Assessment

- This residual mapping story is doc-only and compatible
- The recommended first residual slice appears achievable without schema change
- If later bill or document linkage requires a new carrier/state, that must be assessed as a separate follow-up story

## Risks / Blockers

- treating `generate-draft` as proof that the whole grant-fee lifecycle is closed
- reopening already-implemented prerequisite/state/worklist/draft slices
- folding post-draft state, bill linkage, document linkage, and detail UI into one next story

## Exact Closure Slice Candidates

### Preferred

- `GF-RESIDUAL-SPEC-01`
  - freeze grant-fee residual workflow map and recommend one first post-draft story

### Explicit non-closure

- no product implementation
- no close update for `#15`
- no bill/document/detail workflow implementation

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
