# P1 #8 中间文件 5 步向导 Strict Implementation Gap Ledger Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `spec-gap ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`#8 中间文件 5 步向导` 不能再依赖 residual contract chain 判断 closure。接下来最重要的不是继续写 residual spec，也不是马上写实现，而是先建立一份严格对照 `FPMS SPEC 2.0.md` 的 implementation gap ledger：把 `#8` 的每个 step-level capability 明确标记为 `Implemented`、`Contract Frozen Only` 或 `Missing`，并据此给出真正的 implementation slice mapping。

## Assumptions

- 权威对象固定为：
  - `#8 strict spec-gap ledger`
- 只有 `Implemented` 才允许计入 closure
- `Contract Frozen Only` 不等于产品实现完成
- 结果形态固定为：
  - `strict spec-gap ledger`
  - `implementation-slice mapping`
- 最小闭环固定为：
  - extract step-level capabilities from spec
  - classify each capability
  - group residual buckets
  - recommend implementation slices

## Scope

- 对 `#8` 做 strict spec-gap inventory
- 标记 `Implemented / Contract Frozen Only / Missing`
- 给出后续 implementation-slice 建议

## Explicit Non-scope

- 任何产品实现补丁
- 任何新的 close-audit update
- dispatch / search / reporting / downstream status work

## Current-state Capability Inventory

### Implemented

- Step 1:
  - case input / parsing
  - direction / template / doc date defaults
- Step 2:
  - row editing
  - batch-create contract

Primary evidence:
- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [documents/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)

### Contract Frozen Only

- Step 3 wizard behavior
  - [2026-04-03-docwiz-step3-deadline-linkage-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-03-docwiz-step3-deadline-linkage-design.md)
- Step 4 wizard behavior
  - [2026-04-03-docwiz-step4-fee-linkage-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-03-docwiz-step4-fee-linkage-design.md)
- Step 5 wizard behavior
  - [2026-04-03-docwiz-step5-attachment-generation-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-03-docwiz-step5-attachment-generation-design.md)

### Missing

- actual 5-step wizard UI path
- Step 3 product implementation
- Step 4 product implementation
- Step 5 product implementation
- final end-to-end 5-step user path parity

## Gap Classification Rules

### `Implemented`

- Product behavior exists in current code
- User path is reachable
- Supporting contract is not only doc-level

### `Contract Frozen Only`

- Spec/plan/contract exists
- May have runtime carrier support
- But user-facing/product step behavior is not implemented

### `Missing`

- No sufficient product behavior
- No usable user path
- May or may not have partial carrier support

## Residual Buckets

### Bucket A — Wizard shell expansion

- expand wizard from current 2-step shell to actual 5-step path

### Bucket B — Step 3 implementation

- task candidate preview/edit
- final submit integration

### Bucket C — Step 4 implementation

- fee candidate preview/edit
- final submit integration

### Bucket D — Step 5 implementation

- attachment/template generation workflow
- final submit integration

## Suggested Implementation Slice Mapping

- `DOCWIZ-IMPL-LEDGER-01`
  - strict spec-gap ledger only
- `DOCWIZ-WIZARD-SHELL-EXPAND-01`
  - expand visible wizard flow from 2 steps toward full path
- `DOCWIZ-STEP3-IMPL-01`
  - one Step 3 product implementation slice
- `DOCWIZ-STEP4-IMPL-01`
  - one Step 4 product implementation slice
- `DOCWIZ-STEP5-IMPL-01`
  - one Step 5 product implementation slice

## SQLite / Phase Compatibility Assessment

- Compatible because this story is doc-only ledger work
- Actual implementation slices must re-evaluate phase and shared-file ownership before execution

## Risks / Blockers

- Main risk: continuing to treat contract-freeze work as product closure
- Main risk: directly jumping into implementation without freezing the strict gap ledger
- Main risk: mixing dispatch/search/reporting into the wizard implementation buckets

## Exact Closure Slice Candidates

### Preferred slice

- `DOCWIZ-IMPL-LEDGER-01`
  - strict spec-gap ledger for `#8`

### Explicit non-closure

- no product implementation
- no closure decision update
- no non-wizard document capability work

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a doc-only strict implementation gap ledger for `#8`.
