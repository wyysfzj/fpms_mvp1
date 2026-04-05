# P2 #15 授权费管理 Product Close Audit Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `close-audit after committed product slices`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#15 授权费管理` 在完成 `GF-BATCH-INSTR-*` 和 `GF-NOTICE-DOC-*` 后，已经具备重新进行 strict close-audit 的条件。当前需要根据 `FPMS SPEC 2.0` §5.7.2–5.7.3 的真实产品实现，判断该条目是否还能诚实保留为 `Partially Closed`，还是应该正式更新为 `Closed`。

## Scope

- 复核 `#15` 与 `SPEC 2.0` §5.7.2–5.7.3 的 product parity
- 更新 refresh review 中 `#15` 的结论
- 更新 mitigation ledger，移除已关闭的 `#15`

## Explicit Non-scope

- 不新增任何授权费产品实现
- 不重审 `#19`
- 不扩展到 billing settlement / dispatch / reminder / detail-edit

## Audit Basis

- `FPMS SPEC 2.0` §5.7.2：
  - 批量设置 `ClientInstruction = PAY/ABANDON`
  - 对 `ClientInstruction=NONE` 生成真实 `GRANT_FEE_NOTICE`
  - 文档存档并回写 `NoticeSent / NotifyCount`
- `FPMS SPEC 2.0` §5.7.3：
  - 对 `ClientInstruction=PAY && DraftGenerated=false` 生成授权费草单

## Current Product Evidence

- worklist / state / draft:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `backend/tests/test_grant_fee_state_machine_api.py`
  - `backend/tests/test_grant_fee_draft_linkage_api.py`
- batch client instruction:
  - `artifacts/GF-BATCH-INSTR-BE-01`
  - `artifacts/GF-BATCH-INSTR-FE-01`
  - `artifacts/GF-BATCH-INSTR-QA-01`
- real notice document generation:
  - `artifacts/GF-NOTICE-DOC-BE-01`
  - `artifacts/GF-NOTICE-DOC-FE-01`
  - `artifacts/GF-NOTICE-DOC-QA-01`

## Close Decision Rule

- If committed product behavior now covers:
  - worklist
  - batch PAY / ABANDON
  - real notice document generation + attachment archival + task write-back
  - draft generation for PAY rows
- then `#15` should be updated to `Closed`.

## Exact Closure Slice

- `GF-CLOSE-02`
  - refresh `#15` close decision based on committed product evidence

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
