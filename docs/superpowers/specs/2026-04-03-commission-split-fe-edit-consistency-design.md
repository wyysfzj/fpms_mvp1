# P1 #5 多代理人提成分成 FE Edit Consistency Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend implementation on top of frozen backend semantics`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`COMMSPLIT-FE-EDIT-01` 不是 detail viewing、settlement exposure 或 router/menu story，而是 case-side create/edit split exposure consistency story。当前 [CaseEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseEdit.vue) 已有 `CaseAgentSplitEditor` 与 split 校验/提交链路，但 [CaseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseCreate.vue) 仍主要依赖 `primary_agent_id / second_agent_id`。本轮必须把 create/edit 的 split 录入能力对齐。

## Assumptions

- 权威对象固定为：
  - `CaseCreate / CaseEdit split exposure consistency`
- 第一轮判断标准固定为：
  - `CaseCreate.vue` 是否引入与 `CaseEdit.vue` 等价的 `代理人分摊` 入口
  - `CaseAgentSplitEditor.vue` 是否直接复用
  - `second_agent_id` 是否在 create/edit 页面降级为 context 字段
  - create/edit 两页是否共享同一组 split 校验语义
  - 当前是否只补 page-local exposure，而不扩展到 list/detail 页面
- 第一轮结果形态固定为：
  - `implementation-ready FE slice`
- 第一轮最小闭环固定为：
  - create-side split entry
  - split validation parity
  - create payload wiring
  - explicit non-closure

## Scope

- 在 `CaseCreate.vue` 中引入 `CaseAgentSplitEditor`
- 对齐 create/edit 的 split 校验语义
- 确保 create payload 提交 `agent_splits`
- 保持 `second_agent_id` 为 context 字段，而不是主 split 录入入口

## Explicit Non-scope

- `CaseDetail.vue`
- settlement read-only exposure
- router/menu changes
- report/payout/export UI
- backend semantics changes

## Current Code Evidence

### Existing split editor component

- [CaseAgentSplitEditor.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/components/CaseAgentSplitEditor.vue)
- Current capability:
  - row add/remove
  - `agent_id / role / share_ratio` editing
  - row-level error rendering

### Edit page is already complete enough

- [CaseEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseEdit.vue)
- Current capability:
  - `代理人分摊` section
  - `form.agent_splits`
  - split validation summary
  - row error extraction
  - payload submit of `agent_splits`

### Create page still lacks split section

- [CaseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseCreate.vue)
- Current capability:
  - `primary_agent_id`
  - `second_agent_id`
  - `draftor_id`
- Current gap:
  - no `代理人分摊` section
  - no `CaseAgentSplitEditor`
  - no `form.agent_splits`
  - no split validation summary

### Cases API/types already support split payloads

- [cases.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.ts)
- [cases.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.types.ts)
- Current fact:
  - `agent_splits` payload support already exists

## Implementation Assessment

### Editing parity

- Frozen implementation target:
  - `CaseCreate.vue` should gain the same split entry capability already present in `CaseEdit.vue`

### Component reuse

- Frozen implementation target:
  - reuse `CaseAgentSplitEditor.vue`
  - do not fork a second split editor component

### Validation parity

- Frozen implementation target:
  - create page uses the same split validation semantics as edit page

### Context field boundary

- Frozen implementation target:
  - `second_agent_id` remains available but is no longer the primary multi-agent entry mechanism

## Frozen Decision

- `CaseCreate.vue` must expose `代理人分摊`
- `CaseAgentSplitEditor.vue` must be reused
- create/edit split validation must stay semantically aligned
- `second_agent_id` remains context-only for multi-agent split entry

## Narrowed Follow-up Mapping

- `COMMSPLIT-FE-EDIT-01`
  - create/edit split exposure consistency implementation
- `COMMSPLIT-FE-VIEW-01`
  - case detail viewing exposure if still needed
- `COMMSPLIT-QA-08`
  - serialized audit-only close wave for the edit-consistency slice

## Deferred Slices Ledger

- `CaseDetail.vue`
- settlement read-only exposure
- router/menu changes
- report/payout/export UI

## Phase Compatibility Assessment

- This slice is compatible with the current constraints because it is a frontend-only implementation on top of already-frozen backend semantics.
- It does not require schema or backend API changes.

## Risks / Blockers

- If create page only mounts the component without validation parity, create/edit behavior will still diverge.
- If `second_agent_id` keeps being treated as the main split input, the UI will contradict the frozen FE ownership semantics.
- If detail viewing is absorbed here, the task will lose atomicity.

## Exact Closure Slice Candidates

### Preferred implementation slice

- `COMMSPLIT-FE-EDIT-01`
  - implement create/edit split exposure consistency only

### Explicit non-closure

- no detail viewing
- no settlement exposure
- no router/menu changes
- no report/payout/export UI
- no backend change

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a frontend implementation slice for create/edit split consistency only.
