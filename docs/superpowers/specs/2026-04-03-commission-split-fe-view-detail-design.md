# P1 #5 多代理人提成分成 FE Detail View Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend implementation on top of frozen backend semantics`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`COMMSPLIT-FE-VIEW-01` 不是编辑能力、settlement read-only exposure 或 router/menu story，而是 case detail split viewing exposure story。当前 [CaseDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseDetail.vue) 仍主要展示 `主办代理人 / 辅办代理人 / 撰写人`，但没有把 `agent_splits` 提升为多代理 split 的主要只读载体。本轮必须补齐 detail 页的 `代理人分摊` 只读展示。

## Assumptions

- 权威对象固定为：
  - `CaseDetail split viewing exposure`
- 第一轮判断标准固定为：
  - `CaseDetail.vue` 是否新增清晰的 `代理人分摊` 区块
  - `agent_splits` 是否成为 detail 页上的 split 主展示对象
  - `primary_agent_id / second_agent_id` 是否继续保留但降级为 context
  - detail 页是否保持严格只读，不引入编辑控件
  - 当前是否只补 detail-local exposure，而不扩展到 list/settlement 页面
- 第一轮结果形态固定为：
  - `implementation-ready FE slice`
- 第一轮最小闭环固定为：
  - detail split block
  - read-only row presentation
  - context-field demotion
  - explicit non-closure

## Scope

- 在 `CaseDetail.vue` 中新增 `代理人分摊` 只读信息块
- 展示 `caseData.agent_splits`
- 在 detail 页语义上把 `agent_splits` 提升为 split 的主要可见载体
- 保留 `primary_agent_id / second_agent_id` 在 `代理人分配` 区块中作为 context

## Explicit Non-scope

- editing controls
- settlement read-only exposure
- list page exposure
- router/menu changes
- backend/API/types changes

## Current Code Evidence

### Detail page still shows legacy assignment only

- [CaseDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseDetail.vue)
- Current capability:
  - `代理人分配`
  - `主办代理人`
  - `辅办代理人`
  - `撰写人`
- Current gap:
  - no `代理人分摊` block
  - no `agent_splits` display

### Frontend contract already includes split rows

- [cases.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.ts)
- [cases.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.types.ts)
- Current fact:
  - `Case` detail mapping already carries `agent_splits`

## Implementation Assessment

### Read-only ownership

- Frozen implementation target:
  - detail page shows split rows
  - no editing actions are introduced

### Context demotion

- Frozen implementation target:
  - `primary_agent_id / second_agent_id` remain visible
  - `agent_splits` becomes the primary multi-agent split display

## Frozen Decision

- `CaseDetail.vue` must expose `代理人分摊`
- `agent_splits` must be shown as read-only split rows
- `primary_agent_id / second_agent_id` remain context-only for split semantics
- no editing or settlement exposure is introduced

## Narrowed Follow-up Mapping

- `COMMSPLIT-FE-VIEW-01`
  - detail split viewing implementation
- `COMMSPLIT-QA-09`
  - serialized audit-only close wave for the detail-view slice

## Deferred Slices Ledger

- editing controls
- settlement read-only exposure
- list page exposure
- router/menu changes
- report/payout/export UI

## Phase Compatibility Assessment

- This slice is compatible with the current constraints because it is a frontend-only implementation on top of already-frozen backend semantics.
- It does not require schema, API, or router changes.

## Risks / Blockers

- If detail page keeps only `primary_agent_id / second_agent_id`, FE semantics will remain behind the frozen split contract.
- If editing controls are introduced here, the task will absorb a second slice.
- If shared API/types are touched, the task will unnecessarily collide with pre-existing dirty files.

## Exact Closure Slice Candidates

### Preferred implementation slice

- `COMMSPLIT-FE-VIEW-01`
  - implement case detail split viewing only

### Explicit non-closure

- no editing
- no settlement exposure
- no list exposure
- no router/menu changes
- no backend/API/types changes

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a frontend implementation slice for case detail split viewing only.
