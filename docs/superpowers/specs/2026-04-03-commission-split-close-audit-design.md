# P1 #5 多代理人提成分成 Close Audit Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only audit on top of frozen and implemented backend/frontend slices`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`P1 #5 多代理人提成分成` 的 `review refresh` 与 `mitigation ledger` 仍停留在早期 `Still Missing` 基线，但当前 repo 已经具备：
- `CaseAgentSplit` carrier
- split-aware commission generation / settlement semantics
- case-side split editing
- case detail split viewing

本轮不是再做产品实现，而是执行一次 item-level close audit，把 `#5` 的 review/ledger 结论更新为当前真实状态。

## Scope

- 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md` 中 `#5` 的 item-level conclusion 和 summary counts
- 更新 `docs/priority-ranked-mitigation-ledger.md`，移除已关闭的 `#5`
- 生成 close-audit evidence

## Explicit Non-scope

- 不修改任何产品代码
- 不新增新的 commission/product behavior
- 不重写其他非 `#5` item 的结论
- 不扩展到 `#8/#13/#15/#19` 的 residual replan

## Current Evidence Basis

- Backend carrier:
  - `backend/app/modules/cases/models.py` -> `T_CaseAgentSplit`
  - `backend/app/modules/cases/service.py` -> `validate_case_agent_splits(...)`
  - `backend/app/modules/cases/api.py` -> `agent_splits` output
- Backend commission semantics:
  - `backend/app/modules/commission/service.py`
    - `_load_case_agent_splits(...)`
    - `_split_money_by_ratios(...)`
    - `apply_commission_for_bill(...)`
    - `_commission_is_rewritable(...)`
    - `recompute_commission_settleable(...)`
    - `generate_commission_settlement_lines(...)`
- Frontend exposure:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
- Prior close evidence:
  - `artifacts/COMMSPLIT-BE-01/**`
  - `artifacts/COMMSPLIT-BE-02/**`
  - `artifacts/COMMSPLIT-BE-03/**`
  - `artifacts/COMMSPLIT-FE-EDIT-01/**`
  - `artifacts/COMMSPLIT-FE-VIEW-01/**`

## Frozen Decision

- `#5` no longer fits `Still Missing`
- Current best interpretation is `Closed`
- Closure is achieved through `CaseAgentSplit` + generation + settlement semantics + FE exposure, not through a commission-table redesign exactly matching the old review wording

## Risks / Blockers

- The old review item was framed as `single-agent model only`; the close audit must avoid over-fitting to that old implementation guess.
- The doc update must not silently reopen residual scope beyond `#5`.

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a doc-only close audit for `P1 #5` baseline refresh.
