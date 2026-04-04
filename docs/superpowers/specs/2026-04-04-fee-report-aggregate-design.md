# RPT-FEE Aggregate Implementation Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `resolved by residual map`
- `be_fe_coupling`: `shared summary contract across API client and FeeDraftList page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`FEERPT-RESIDUAL-01` 已经冻结 `RPT-FEE` 的 first residual slice，但当前 `GET /fees/drafts` summary 仍未返回 grouped amount summaries：

- `client_amounts`
- `case_type_amounts`
- `country_amounts`

因此下一步应只实现这组 grouped amount summaries，并在现有 `FeeDraftList.vue` 上展示，不新建报表页，也不吸收代理人收入、已收/未收语义或趋势统计。

## Assumptions

- `FEERPT-RESIDUAL-01` 的 residual map 为当前权威
- 当前实现只扩展现有 `GET /fees/drafts` report summary
- 当前 grouped aggregates 继续基于 first-round carrier：
  - `T_FeeDraft`
  - `T_FeeItem`
  - related `T_Case`
- 不新增 schema / migration
- 关闭标准继续固定为真实产品行为存在

## Scope

- 后端为 `GET /fees/drafts` summary 新增 grouped amount summaries
- 前端 `fees` API client/types 接入新 summary 字段
- `FeeDraftList.vue` 展示 grouped amount summaries
- 保持现有费用草单列表/筛选/summary cards 行为不回归

## Explicit Non-scope

- 不做 agent-attributed service income
- 不做 billed / received / unpaid semantics
- 不做 year/month trend reporting
- 不做图表 / 导出 / new report page

## Grouped Summary Semantics

### `client_amounts`

- group key:
  - `FeeDraft.client_id`
- label:
  - client `name_cn` if available, else `client_id`, else `未分配客户`
- metrics per group:
  - `draft_count`
  - `service_fee_amount`
  - `government_fee_amount`
  - `income_amount`

### `case_type_amounts`

- group key:
  - related `Case.case_type`
- label:
  - case-type code itself
- metrics per group:
  - `draft_count`
  - `service_fee_amount`
  - `government_fee_amount`
  - `income_amount`

### `country_amounts`

- group key:
  - `Case.to_country` first
  - else `Case.from_country`
  - else `未填写`
- label:
  - same as key
- metrics per group:
  - `draft_count`
  - `service_fee_amount`
  - `government_fee_amount`
  - `income_amount`

## Shared-file / Ownership Analysis

Serialized backend ownership:

- `backend/app/modules/fees/service.py`
- `backend/app/modules/fees/schemas.py`
- `backend/tests/test_fee_report.py`

Serialized frontend ownership:

- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/modules/fees/pages/FeeDraftList.vue`

## Batch Recommendation

- `FEERPT-AGG-BE-01`
  - extend summary contract and backend grouped amount computation
- `FEERPT-AGG-FE-01`
  - render grouped amount summaries on `FeeDraftList.vue`
- `FEERPT-AGG-QA-01`
  - audit evidence and exact closure

## SQLite / Phase Compatibility

- No schema change required
- Pure query/service + page contract extension
- Compatible with current SQLite / Phase constraints

## Risks

- Accidentally treating grouped draft totals as billed / received semantics
- Pulling agent-income attribution into the same slice
- Over-coupling grouped summary output to client/case masterdata labels

## Exact Closure Slice

- Implement grouped fee-report amount summaries on the existing fee-report page and summary contract, nothing more
