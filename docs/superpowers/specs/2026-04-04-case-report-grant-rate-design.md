# RPT-CASE Grant-Rate Semantics Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `semantics freeze before report metric implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-CASE` 在 `CASERPT-AGGREGATE-01` 之后仍缺 `授权率` 指标，但当前仓库尚未冻结“授权率”的分子/分母语义。如果直接进入实现，很容易把当前 `Case.status` 枚举硬拼成一个未经定义的假指标。因此下一步应先冻结 grant-rate semantics，再决定是否进入实现。

## Assumptions

- `CASERPT-BE-01` / `CASERPT-FE-01` / `CASERPT-QA-01` 的 first-round closure 继续有效
- `CASERPT-AGG-BE-01` / `CASERPT-AGG-FE-01` / `CASERPT-AGG-QA-01` 的 grouped aggregate closure 继续有效
- `CASERPT-TREND-PREREQ-01` 对 trend reporting 的 blocked 判断继续有效
- 当前目标仅冻结授权率口径，不实现授权率产品行为
- 关闭标准继续固定为：
  - 只有真实产品行为存在，才允许新的 rate capability 计入 closure

## Scope

- 冻结 `授权率` 指标的分子/分母语义
- 明确哪些 `Case.status` 计入“曾授权”
- 明确哪些 `Case.status` 计入授权率分母
- 明确哪些 `Case.status` 必须排除
- 判断该指标是否可在当前 carrier 下直接进入实现

## Explicit Non-scope

- 不做任何案件统计产品实现补丁
- 不做年/月趋势统计
- 不做 schema / migration change
- 不更新 `RPT-CASE` 或 `#13` close decision

## Current Carrier Inventory

### Available now

- `backend/app/modules/cases/enums.py`
  - `GRANTED`
  - `REJECTED`
  - `WITHDRAWN`
  - `ABANDONED`
  - `EXPIRED`
  - `TERMINATED`
  - `INVALIDATED`
- `backend/app/modules/cases/service.py`
  - `_TERMINAL_STATUS_ALLOWED_TRANSITIONS`
  - already groups granted-lineage statuses under `CaseStatus.GRANTED`
- `frontend/src/constants/displayText.ts`
  - visible labels for the same status codes
- `frontend/src/constants/workflow.ts`
  - granted-lineage branch statuses continue to map back to the授权阶段

### Not available now

- No separate persisted “historically granted” boolean
- No dedicated prosecution outcome enum
- No grant-rate-specific backend summary contract
- No current `INVALIDATED_PARTIAL` status in runtime enum carrier

## Spec Alignment

`FPMS SPEC 2.0` `9.4.1` requires:

- 按代理人统计案件数量和授权率等
- 指标字段包括：
  - 授权数量/授权率
  - 终止/无效数量
  - 正在审中数量

The spec names the metric, but does not define the exact denominator. That denominator must therefore be frozen here before implementation.

## Recommended Grant-Rate Semantics

### Numerator — granted outcome count

Count a case as `授权成功` if its current status is in the granted-lineage set:

- `GRANTED`
- `TERMINATED`
- `INVALIDATED`
- `EXPIRED`

Reasoning:

- These statuses all imply the case had already reached the授权阶段.
- `TERMINATED / INVALIDATED / EXPIRED` are post-grant downstream outcomes, not prosecution failures before grant.
- Counting only current `GRANTED` would undercount historically granted cases.

### Denominator — closed prosecution outcome count

Include a case in the grant-rate denominator if its current status is one of:

- granted-lineage statuses:
  - `GRANTED`
  - `TERMINATED`
  - `INVALIDATED`
  - `EXPIRED`
- non-grant closed outcomes:
  - `REJECTED`
  - `WITHDRAWN`
  - `ABANDONED`

Reasoning:

- These statuses represent cases whose prosecution outcome is already settled enough to classify success vs non-success.
- This makes grant rate a prosecution success ratio, not a portfolio coverage ratio.

### Explicitly excluded from denominator

- `NOT_FILED`
- `WAITING_RECEIPT`
- `PENDING`
- `PRELIM_EXAM`
- `PRELIM_PASS`
- `AMENDMENT`
- `PUBLISHED`
- `SUB_EXAM`
- `OA1`
- `OA2`
- `REEXAM`
- `GRANT_PENDING`

Reasoning:

- These cases are still在途 / 审中 and do not yet have a closed prosecution outcome.
- Including them would make the metric fluctuate with pipeline mix instead of authorization effectiveness.

## Derived Metric Definition

- `granted_count`
  - number of cases in granted-lineage statuses
- `grant_rate_denominator`
  - number of cases in the denominator set above
- `grant_rate`
  - `granted_count / grant_rate_denominator`
  - return `null` when denominator is `0`

## Related Metrics Separation

The following metrics remain separate and MUST NOT be merged into grant rate:

- `terminated_count`
  - count current `TERMINATED`
- `invalidated_count`
  - count current `INVALIDATED`
- `in_prosecution_count`
  - count current in-progress statuses excluded from denominator

This keeps the metric family aligned with `SPEC 2.0`:

- 授权数量/授权率
- 终止/无效数量
- 正在审中数量

## Implementation Readiness Judgment

### Can grant-rate be implemented under current carrier?

- `Yes`

### Why it is not blocked like trend reporting

- Grant-rate can be derived from current `Case.status` semantics without requiring new date fields
- Existing runtime carrier already distinguishes:
  - granted-lineage statuses
  - closed non-grant outcomes
  - in-progress statuses
- No schema or migration appears necessary for a first implementation slice

## Recommended Follow-up Slice

- `CASERPT-RATE-01`

### Exact closure candidate

- extend `GET /cases` summary with:
  - `granted_count`
  - `grant_rate`
  - `terminated_count`
  - `invalidated_count`
  - `in_prosecution_count`
- add FE presentation for the above metrics on `CaseList.vue`

## Explicitly Deferred

- year/month trend reporting
- charts
- export
- client-grouped authorization rate
- any schema carrier for historical partial invalidation

## SQLite / Phase Compatibility Assessment

- This semantics-freeze story is doc-only and fully compatible
- The recommended follow-up slice appears achievable without schema change
- If future product semantics require `INVALIDATED_PARTIAL` or richer outcome history, that must be handled as a separate prerequisite story

## Risks / Blockers

- Mistaking current `GRANTED` as the only successful outcome
- Mistaking all terminal statuses as prosecution failures
- Mixing在途案件 into the denominator
- Folding trend semantics into the same grant-rate slice

## Exact Closure Slice Candidates

### Preferred

- `CASERPT-RATE-SPEC-01`
  - freeze grant-rate numerator/denominator semantics and decide implementation readiness

### Explicit non-closure

- no API/UI implementation
- no trend reporting
- no close update

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task should be a doc-only semantics freeze story before `CASERPT-RATE-01` implementation.
