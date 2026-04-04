# RPT-FEE Agent Income Semantics Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `semantics freeze before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-FEE` 在 grouped aggregate slice 后，剩余最容易被误做假的能力是“按代理人统计其所负责案件带来的服务费收入”。当前 repo 同时存在：

- `T_Case.primary_agent_id / second_agent_id`
- `T_CaseAgentSplit`
- commission 多代理 split 逻辑

如果不先冻结 fee report 的 agent-income authority，后续实现很容易在：

- `primary_agent_id` 单归属
- `primary + second` 双归属
- `case_agent_split` 比例归属

之间随意切换，导致报表和提成口径不一致。

## Assumptions

- `FPMS SPEC 2.0 9.4.2` 的语义是：
  - “按代理人统计其所负责案件带来的服务费收入”
- `RPT-FEE` 当前 authority 仍是：
  - `GET /fees/drafts`
  - `FeeDraftList.vue`
- 关闭标准继续固定为：
  - 只有真实产品行为存在，才允许该 residual capability 计入 closure
- 本 wave 只冻结语义，不做任何产品实现

## Scope

- 冻结 `agent-attributed service income` 的 source-of-truth
- 冻结 split / fallback / amount attribution semantics
- 判断该能力当前是否可直接进入实现
- 推荐下一条 implementation slice

## Explicit Non-scope

- 不做任何 fees/billing/cases/commission 产品实现补丁
- 不做 billed / received / unpaid semantics
- 不做趋势统计
- 不做图表 / 导出
- 不更新 `RPT-FEE` 或 `#13` close decision

## Current Carrier Evidence

- `backend/app/modules/cases/models.py`
  - `T_Case.primary_agent_id`
  - `T_Case.second_agent_id`
  - `T_CaseAgentSplit`
- `backend/app/modules/commission/service.py`
  - `_load_case_agent_splits(...)`
  - `apply_commission_for_bill(...)`
  - 现有 commission 语义：
    - 若存在 `case_agent_split`，按 split rows 分摊
    - 否则 fallback 到 `primary_agent_id = 100%`
- `backend/app/modules/fees/service.py`
  - 当前 fee report 仍未实现 agent income summary

## Semantics Decision

### Source-of-truth

- `T_CaseAgentSplit` 是 agent-income attribution 的首要 authority
- 当某案件存在当前有效 `T_CaseAgentSplit` rows 时：
  - fee report 必须按 split rows 分摊服务费收入
  - 不再额外把 `second_agent_id` 当作独立 attribution source

### Fallback

- 当某案件不存在 `T_CaseAgentSplit` rows 时：
  - fallback 到 `primary_agent_id = 100%`
- `second_agent_id` 在 fallback 语义中只保留 context-only 身份
  - 不自动分到任何服务费收入

### Metric scope

- 本 residual 只统计 `service_fee_amount`
- 不统计：
  - `government_fee_amount`
  - `misc`
  - `income_amount` 全口径

### Amount source

- 第一轮继续以 `T_FeeDraft.total_service` 为 amount source
- 不在本 slice 中引入：
  - billed / received split
  - offset / receipt semantics

### Group row contract

- 每个代理人 row 至少应包含：
  - `agent_id`
  - `draft_count`
  - `service_fee_amount`
- label 可以在后续实现中先用 `agent_id`
  - 如需用户姓名映射，可作为同 slice 内的 display enhancement

## Implementation Readiness Judgment

- `agent-attributed service income` 在当前 carrier 下可直接进入实现
- 不需要新增 schema / migration
- 但必须单独作为一个 residual implementation slice，不能与 billed/received/unpaid 或趋势统计混做

## Recommended Next Slice

- `FEERPT-INCOME-01`
- exact closure candidate:
  - extend `GET /fees/drafts` summary with grouped `agent_service_amounts`
  - case split semantics:
    - `case_agent_split` first
    - `primary_agent_id` fallback
  - render grouped agent service income on `FeeDraftList.vue`

## Explicitly Deferred

- billed / received / unpaid semantics
- time trend reporting
- chart / export
- commission settlement reporting alignment beyond attribution semantics

## Risks

- 把 `second_agent_id` 错当成与 `primary_agent_id` 平分收入
- 在 fee report 与 commission split 之间采用不同 authority
- 把 `total_service` 与 billed/received service revenue 混为一谈

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- 但必须先以本语义冻结作为 authority，再进入 `FEERPT-INCOME-01`
