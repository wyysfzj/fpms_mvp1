# P1 #5 多代理人提成分成 Frontend Exposure Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend exposure decision after backend semantics freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`COMMSPLIT-FE-01` 不是 settlement 页面增强或报表/导出 story，而是 multi-agent split 在前端中的 viewing/editing exposure 归属 story。当前 backend 已经冻结：`CaseAgentSplit` 是 split source-of-truth，`second_agent_id` 在 generation 中仅为 context，commission / settlement 只是下游消费层。因此本轮必须先冻结用户应在哪里查看和编辑 split，以及哪些页面只允许只读 exposure。

## Assumptions

- 权威对象固定为：
  - `frontend viewing/editing exposure of CaseAgentSplit`
- 第一轮判断标准固定为：
  - split 信息是否应暴露在案件创建/编辑页
  - split 信息是否应暴露在案件详情或列表的某个 viewing 入口
  - 用户是否只能编辑 `CaseAgentSplit`，而不能直接编辑 commission rows
  - `second_agent_id` 在 FE 是否只保留为 context，而不是 split 编辑主入口
  - 当前是否需要最小只读 commission/settlement exposure，还是先仅做 case-side exposure
- 第一轮结果形态固定为：
  - `frontend exposure decision`
  - `narrowed page/component follow-up mapping`
- 第一轮最小闭环固定为：
  - viewing 入口所在页面
  - editing 入口所在页面
  - `CaseAgentSplit` 与 `second_agent_id` 的前端边界
  - 是否需要最小只读 commission/settlement exposure
  - follow-up remapping
  - explicit deferred slices

## Scope

- 冻结 split viewing/editing 的前端归属
- 冻结 `CaseAgentSplit` 与 `second_agent_id` 的 FE 语义边界
- 冻结 settlement 页面不承担 split 编辑职责
- 为后续 FE 实现 slice 画边界

## Explicit Non-scope

- Vue/page/component implementation
- shared API/types wiring
- router/menu changes
- report/payout/export UI
- settlement workflow UI enhancement

## Current Code Evidence

### Case-side types and payloads already support split rows

- [cases.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.ts)
- [cases.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.types.ts)
- Current facts:
  - `CaseAgentSplit` type already exists
  - case payload mapping already supports `agent_splits`
  - `primary_agent_id` and `second_agent_id` are still present as separate fields

### Case edit already exposes split editing

- [CaseEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseEdit.vue)
- [CaseAgentSplitEditor.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/components/CaseAgentSplitEditor.vue)
- Current facts:
  - `代理人分摊` section already exists
  - `CaseAgentSplitEditor` is already embedded
  - FE validation already enforces duplicate-agent, role, and ratio-sum rules

### Case create still emphasizes primary/second agent fields

- [CaseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseCreate.vue)
- Current fact:
  - visible evidence confirms `primary_agent_id` / `second_agent_id` inputs
  - current split exposure is not yet proven equivalent to `CaseEdit.vue`

### Case detail still shows legacy context fields

- [CaseDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseDetail.vue)
- Current facts:
  - detail page visibly shows `primary_agent_id`
  - detail page visibly shows `second_agent_id`
  - explicit `agent_splits` viewing block is not yet present

### Settlement page is not the split editing owner

- `frontend/src/modules/commission/**`
- Current assessment:
  - no current split editing owner is present there
  - this matches the frozen backend boundary: settlement is a downstream consumer, not a split source editor

## Frontend Exposure Assessment

### Editing ownership

- Frozen decision:
  - split editing belongs on the case side, not the settlement side

### Viewing ownership

- Frozen decision:
  - split viewing should also prioritize case-side exposure, especially detail-level viewing

### `CaseAgentSplit` vs `second_agent_id`

- Frozen decision:
  - `CaseAgentSplit` is the primary FE object for multi-agent split
  - `second_agent_id` remains visible only as context / legacy auxiliary field

### Settlement exposure boundary

- Frozen decision:
  - settlement pages may at most consume the already-frozen downstream semantics
  - they do not own split editing

### First-round exposure scope

- Frozen decision:
  - first-round FE ownership should focus on case-side exposure
  - any downstream read-only commission/settlement exposure stays follow-up unless separately requested

## Frozen Decision

- editing ownership stays on case-side pages
- viewing ownership also prioritizes case-side pages
- `CaseAgentSplit` is the FE split source object
- `second_agent_id` remains context-only for FE split semantics
- settlement pages do not own split editing

## Narrowed Follow-up Mapping

- `COMMSPLIT-FE-01`
  - frontend exposure decision freeze
- `COMMSPLIT-QA-07`
  - serialized audit-only close wave for the frontend-exposure slice
- possible later implementation follow-ups:
  - case edit/create exposure consistency
  - case detail viewing exposure
  - downstream read-only commission/settlement exposure if still needed

## Deferred Slices Ledger

- `Vue/page/component implementation`
- `shared API/types wiring`
- `router/menu changes`
- `report/payout/export UI`
- `settlement workflow UI enhancement`

## Phase Compatibility Assessment

- This design wave is compatible with current constraints because it only freezes frontend ownership and exposure semantics.
- It does not require backend schema or router changes.
- It narrows later implementation slices instead of expanding into settlement or reporting work.

## Risks / Blockers

- If frontend ownership is not frozen first, later work may split editing responsibility across case and settlement pages.
- If `second_agent_id` remains visually equal to `CaseAgentSplit` semantics, users may continue treating a context field as the split source-of-truth.
- If case-side viewing is not frozen now, later work may overcorrect by pushing split visibility into reporting or settlement pages.

## Exact Closure Slice Candidates

### Preferred first slice

- `COMMSPLIT-FE-01`
  - freeze frontend viewing/editing exposure ownership only

### Explicit non-closure

- no Vue/page/component patch
- no shared API/types patch
- no router/menu patch
- no report/payout/export UI patch
- no settlement workflow UI enhancement

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a frontend exposure decision slice, not a component implementation or settlement UI story.
