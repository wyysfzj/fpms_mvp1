# FEERPT Agent Income Implementation Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `shared FE/BE residual implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`RPT-FEE` 已完成 grouped client/case-type/country summaries，下一条 residual implementation slice 是 `agent-attributed service income`。本轮必须把已经冻结的归属语义真正落成产品行为：在现有 `GET /fees/drafts` summary 中增加 `agent_service_amounts`，并在现有 `FeeDraftList.vue` 上渲染“按代理人服务费汇总”。

## Assumptions

- source-of-truth 已冻结：
  - `T_CaseAgentSplit` first
  - `primary_agent_id` fallback
  - `second_agent_id` context-only
- amount source 继续固定为：
  - `T_FeeDraft.total_service`
- 本轮不引入 billed / received / unpaid semantics

## Scope

- backend:
  - extend `GET /fees/drafts` summary with `agent_service_amounts`
- frontend:
  - consume and render grouped agent service income on `FeeDraftList.vue`
- qa:
  - verify exact closure and evidence

## Explicit Non-scope

- no billed / received / unpaid semantics
- no trend reporting
- no chart / export
- no new report page
- no schema change

## Exact Closure Slice

- `agent_service_amounts`
  - split rows first
  - `primary_agent_id` fallback
  - current service-fee attribution only

## Follow-up

- `FEERPT-BALANCE-SPEC-*`
- `FEERPT-TREND-*`
