# RPT-CASE Grant-Rate Implementation Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `resolved by prior semantics freeze`
- `be_fe_coupling`: `shared summary contract across API client and CaseList page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`CASERPT-RATE-SPEC-01` 已经冻结 `RPT-CASE` 的授权率语义，但当前 `GET /cases` summary 仍未返回：

- `granted_count`
- `grant_rate`
- `terminated_count`
- `invalidated_count`
- `in_prosecution_count`

因此下一步应只实现这组案件统计指标，并在现有 `CaseList.vue` 上展示，不新建报表页，也不吸收 trend reporting。

## Assumptions

- `CASERPT-RATE-SPEC-01` 的授权率语义为当前权威
- `trend reporting` 继续保持 prerequisite-blocked
- 当前实现只扩展现有 `GET /cases` report summary
- 不新增 schema / migration
- 关闭标准继续固定为真实产品行为存在

## Scope

- 后端为 `GET /cases` summary 新增授权率相关指标
- 前端 `cases` API client/types 接入新 summary 字段
- `CaseList.vue` 展示授权率相关指标
- 保持现有案件列表/筛选/聚合摘要行为不回归

## Explicit Non-scope

- 不做 year/month trend reporting
- 不做图表 / 导出 / BI shell
- 不新建 `CaseReport.vue`
- 不修改案件状态 carrier

## Metric Semantics

- `granted_count`
  - count current status in:
    - `GRANTED`
    - `TERMINATED`
    - `INVALIDATED`
    - `EXPIRED`
- `grant_rate_denominator`
  - count current status in:
    - granted-lineage
    - `REJECTED`
    - `WITHDRAWN`
    - `ABANDONED`
- `grant_rate`
  - `granted_count / grant_rate_denominator`
  - `null` when denominator is `0`
- `terminated_count`
  - count current `TERMINATED`
- `invalidated_count`
  - count current `INVALIDATED`
- `in_prosecution_count`
  - count statuses excluded from denominator and not yet closed

## Shared-file / Ownership Analysis

Serialized backend ownership:

- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/tests/test_case_report.py`

Serialized frontend ownership:

- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseList.vue`

## Batch Recommendation

- `CASERPT-RATE-BE-01`
  - extend summary contract and backend metric computation
- `CASERPT-RATE-FE-01`
  - render the new metrics on `CaseList.vue`
- `CASERPT-RATE-QA-01`
  - audit evidence and exact closure

## SQLite / Phase Compatibility

- No schema change required
- Pure query/service + page contract extension
- Compatible with current SQLite / Phase constraints

## Risks

- Reintroducing ambiguous denominator semantics
- Accidentally mixing trend reporting into the same slice
- Rendering `0` denominator as `0%` instead of explicit unavailable state

## Exact Closure Slice

- Implement grant-rate summary metrics on the existing case report page and summary contract, nothing more
