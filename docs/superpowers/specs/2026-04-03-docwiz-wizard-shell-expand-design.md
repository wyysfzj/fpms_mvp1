# P1 #8 中间文件 5 步向导 Wizard Shell Expansion Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `frontend shell implementation before step-specific logic`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`#8` 的 strict gap ledger 已经明确：当前 wizard 只有 Step 1/2 产品实现，而 full 5-step 用户路径仍缺失。后续真正的第一条实现 slice 不应直接从 Step 3/4/5 业务逻辑开始，而应先把 `DocumentWizard.vue` 从“两步向导”扩成真正可承载 5-step flow 的前端壳层，为 Step 3/4/5 提供稳定挂点。

## Assumptions

- 权威对象固定为：
  - `wizard shell expansion`
- 结果形态固定为：
  - `frontend shell implementation slice`
- 最小闭环固定为：
  - 2-step -> 5-step shell
  - title/subtitle correction
  - Step 3/4/5 placeholder sections
  - correct navigation flow
  - Step 1/2 behavior preserved

## Scope

- 扩展 wizard 壳层到 5-step
- 调整页面标题/副标题与步骤文案
- 为 Step 3/4/5 增加独立占位承载区
- 让步骤流转与 5-step shell 一致
- 保持 Step 1/2 当前行为不回归

## Explicit Non-scope

- Step 3/4/5 product implementation
- any backend patch
- any API/types change
- dispatch / search / reporting / downstream status work

## Current-state Shell Evidence

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
  - subtitle 仍是 `两步完成批量登记`
  - `el-steps` 只有 2 步
  - 主体条件渲染仍只有 Step 1 / Step 2 两个分支
- strict ledger:
  - [2026-04-03-docwiz-implementation-gap-ledger-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-03-docwiz-implementation-gap-ledger-design.md)
  - Step 1/2 = `Implemented`
  - Step 3/4/5 = `Contract Frozen Only`
  - full 5-step path = `Missing`

## Shared-file / Ownership Analysis

Primary shared ownership file:
- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)

Serialized ownership is required for:
- step metadata
- active step index / previous / next flow
- title / subtitle / button wording
- Step 1/2 vs Step 3/4/5 conditional rendering

This story should avoid touching:
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)

## Implementation Recommendation

Recommended approach:

1. expand `el-steps` from 2 to 5
2. replace misleading two-step subtitle with 5-step wording
3. preserve current Step 1/2 UI and submit behavior
4. add Step 3/4/5 placeholder panels with Simplified Chinese empty-state wording
5. wire correct previous/next navigation through all 5 shell steps

Preferred navigation decision:
- keep current submit behavior attached to the existing Step 2 implementation path for this slice
- do not move submission to Step 5 yet

## Done Definition

- Wizard shell visibly shows 5 steps
- Step 3/4/5 have dedicated placeholder panels
- Step 1/2 current behavior still works
- No step-specific business logic is absorbed

## Risks / Blockers

- Main risk: accidentally mixing Step 3/4/5 logic into the shell task
- Main risk: changing current submit timing in a way that regresses Step 1/2
- Main risk: touching shared API/types without necessity

## Exact Closure Slice Candidates

### Preferred slice

- `DOCWIZ-WIZARD-SHELL-EXPAND-01`
  - implement 5-step shell expansion only

### Explicit non-closure

- no Step 3/4/5 logic
- no backend patch
- no API/types change

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a frontend shell expansion implementation slice.
