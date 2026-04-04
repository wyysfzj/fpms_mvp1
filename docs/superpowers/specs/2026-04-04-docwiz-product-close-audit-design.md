# P1 #8 中间文件 5 步向导 Product Close Audit Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after full product implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#8 中间文件 5 步向导` 在 refresh review 中当前仍标记为 `Partially Closed`，但这已经落后于最新产品实现。当前 repo 已具备真实 5-step 向导壳层，以及 Step 3/4/5 的 preview 与 final-submit integration，因此需要进行一次严格按产品实现的 close-audit refresh，把 review baseline 与 mitigation ledger 更新到真实状态。

## Assumptions

- 权威对象固定为：
  - `#8 product close-audit refresh`
- 关闭标准固定为：
  - Step 1/2 已实现
  - Step 3 preview + final submit 已实现
  - Step 4 preview + final submit 已实现
  - Step 5 preview + final submit 已实现
  - 向导已形成真实 5-step 用户路径
- 结果形态固定为：
  - `refresh review + mitigation ledger close update`

## Scope

- 更新 `FPMS_SPEC2_2nd_Review_REFRESH.md` 中 `#8` 的状态与说明
- 更新 `priority-ranked-mitigation-ledger.md` 中 `#8` 的状态或移除该项
- 更新 summary counts（如有必要）

## Explicit Non-scope

- 不重审 `#13/#15/#19`
- 不新增 residual story
- 不做任何产品实现补丁

## Current Product Evidence

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
  - 已形成真实 5-step flow
  - 最后一步按钮为 `完成向导并提交`
- Step 3:
  - preview: [DOCWIZ-STEP3-BE-PREVIEW-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP3-BE-PREVIEW-01.md)
  - final submit: [DOCWIZ-STEP3-BE-FINAL-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP3-BE-FINAL-01.md)
- Step 4:
  - preview: [DOCWIZ-STEP4-BE-PREVIEW-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP4-BE-PREVIEW-01.md)
  - final submit: [DOCWIZ-STEP4-BE-FINAL-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP4-BE-FINAL-01.md)
- Step 5:
  - preview: [DOCWIZ-STEP5-BE-PREVIEW-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP5-BE-PREVIEW-01.md)
  - final submit: [DOCWIZ-STEP5-BE-FINAL-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP5-BE-FINAL-01.md)

## Required Refresh Updates

- Update section `4.8 P1 #8 中间文件 5 步向导` from `Partially Closed` to `Closed`
- Replace old residual-gap wording with:
  - `None for current implementation`
- Update top-level counts
- Remove `#8` from the mitigation ledger and next-story candidates

## Risks / Blockers

- Main risk: accidentally keeping old “contract-freeze only” wording after product implementation is complete
- Main risk: accidentally reopening `#13/#15/#19` while updating counts

## Exact Closure Slice Candidates

- `DOCWIZ-CLOSE-02`
  - refresh-close `#8` based on full product implementation
- `DOCWIZ-QA-CLOSE-02`
  - evidence audit for the close wave

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
