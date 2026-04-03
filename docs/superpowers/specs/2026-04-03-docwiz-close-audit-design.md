# P1 #8 中间文件 5 步向导 Close Audit Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after residual program freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#8 中间文件 5 步向导` 在 refresh review 中当前仍标记为 `Partially Closed`，但这已经落后于最新证据。按照当前已冻结的解释，该条不是“等待完整 5-step FE/BE 实现的大故事”，而是一个 `wizard residual program`。在这个解释下，Step 1/2 representative slices 已实现，Step 3/4/5 residual contract 也都已完成并通过 QA，因此需要进行一次 close-audit refresh，把 review baseline 与 mitigation ledger 更新到真实状态。

## Assumptions

- 权威对象固定为：
  - `#8 close-audit refresh`
- 关闭标准固定为：
  - Step 1/2 representative slices 已实现
  - Step 3 residual contract `PASS`
  - Step 4 residual contract `PASS`
  - Step 5 residual contract `PASS`
- 结果形态固定为：
  - `refresh review + mitigation ledger close update`
- 最小闭环固定为：
  - update refresh review
  - update mitigation ledger
  - update counts if needed
  - explicit closure record

## Scope

- 更新 `FPMS_SPEC2_2nd_Review_REFRESH.md` 中 `#8` 的状态与说明
- 更新 `priority-ranked-mitigation-ledger.md` 中 `#8` 的状态或移除该项
- 更新 summary counts（如有必要）

## Explicit Non-scope

- 不重审 `#13/#15/#19` 的具体 residual 结论
- 不新增 residual story
- 不做任何产品实现补丁

## Current Evidence Ledger

### Step 1/2 representative slices

- [2026-03-29-documents-step12-wizard.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/plans/2026-03-29-documents-step12-wizard.md)
- [2026-03-29-documents-step12-wizard-prereq-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-03-29-documents-step12-wizard-prereq-design.md)
- [DOCWIZ-BE-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-BE-01.md)
- [DOCWIZ-FE-SHELL-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/frontend/DOCWIZ-FE-SHELL-01.md)
- [DOCWIZ-FE-STEP1-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/frontend/DOCWIZ-FE-STEP1-01.md)
- [DOCWIZ-FE-STEP2-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/frontend/DOCWIZ-FE-STEP2-01.md)

### Step 3 residual contract

- [2026-04-03-docwiz-step3-deadline-linkage-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-03-docwiz-step3-deadline-linkage-design.md)
- [2026-04-03-docwiz-step3-deadline-linkage.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/plans/2026-04-03-docwiz-step3-deadline-linkage.md)
- [DOCWIZ-STEP3-SPEC-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP3-SPEC-01.md)
- [DOCWIZ-QA-STEP3-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-QA-STEP3-01.md)

### Step 4 residual contract

- [2026-04-03-docwiz-step4-fee-linkage-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-03-docwiz-step4-fee-linkage-design.md)
- [2026-04-03-docwiz-step4-fee-linkage.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/plans/2026-04-03-docwiz-step4-fee-linkage.md)
- [DOCWIZ-STEP4-SPEC-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP4-SPEC-01.md)
- [DOCWIZ-QA-STEP4-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-QA-STEP4-01.md)

### Step 5 residual contract

- [2026-04-03-docwiz-step5-attachment-generation-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-03-docwiz-step5-attachment-generation-design.md)
- [2026-04-03-docwiz-step5-attachment-generation.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/plans/2026-04-03-docwiz-step5-attachment-generation.md)
- [DOCWIZ-STEP5-SPEC-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-STEP5-SPEC-01.md)
- [DOCWIZ-QA-STEP5-01.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/DOCWIZ-QA-STEP5-01.md)

## Close Decision

- `#8` should now be marked `Closed`

## Why This Is Correct

- `#8` has already been reinterpreted as a wizard residual program instead of a missing full-implementation mega story.
- Under that interpretation, all required residual slices are now covered:
  - Step 1/2 representative slices
  - Step 3 residual contract
  - Step 4 residual contract
  - Step 5 residual contract
- Keeping `Partially Closed` would no longer match the committed evidence chain.

## Required Refresh Updates

- Update section `4.8 P1 #8 中间文件 5 步向导` from `Partially Closed` to `Closed`
- Replace the old residual-gap wording with:
  - `None for current interpretation`
- Update top-level counts if needed
- Remove `#8` from the mitigation ledger and next-story candidates

## Risks / Blockers

- Main risk: silently changing the close standard back to “must have full 5-step implementation”.
- Main risk: accidentally reopening `#13/#15/#19` while updating summary counts.

## Exact Closure Slice Candidates

### Preferred slice

- `DOCWIZ-CLOSE-01`
  - refresh-close `#8` based on completed Step 1/2 + Step 3/4/5 evidence

### Explicit non-closure

- no re-review of `#13/#15/#19`
- no new story creation
- no product-code change

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a doc-only close-audit refresh for `#8`.
