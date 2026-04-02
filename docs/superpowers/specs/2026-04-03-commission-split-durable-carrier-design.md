# P1 #5 多代理人提成分成 Durable Carrier Decision Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared commission program; schema decision before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`COMMSPLIT-PRE-02` 不是 schema 实现任务，而是 durable carrier decision story。当前 repo 已经通过 `COMMSPLIT-PRE-01` 冻结：现有 `Case.second_agent_id`、`Commission.s1_rate/s2_rate`、以及 settlement 结构都只能算上下文，不是真实 split carrier。下一步必须决定是否需要新增 durable carrier，以及这个 carrier 应该挂在 case 侧、commission 侧，还是独立 allocation entity 侧。

## Assumptions

- 本轮只比较以下 3 种候选：
  - `CaseAgentSplit` 明细表
  - `CommissionAllocation` 独立表
  - `Settlement-linked allocation` 方案
- 本轮判断标准固定为：
  - 能否表达多参与方
  - 能否表达 `ratio / share`
  - 能否支撑单代理 fallback
  - 能否与现有 settlement/report 兼容
  - 能否保持 SQLite-safe
- 本轮结果形态固定为：
  - `durable carrier design decision`
  - `schema prerequisite recommendation`
- 本轮最小闭环固定为：
  - candidate comparison
  - recommended carrier choice
  - schema prerequisite recommendation
  - explicit deferred slices

## Scope

- 比较 3 种 durable carrier 方案
- 评估与 case / commission / settlement 的归属关系
- 给出推荐选择
- 判断是否必须拆真正的 DB prerequisite task

## Explicit Non-scope

- migration SQL
- ORM fields implementation
- API payload 细节
- commission calculation
- settlement behavior changes
- FE editing/viewing
- reports / payout / export

## Candidate Comparison

### Option A: `CaseAgentSplit` 明细表

#### Strengths

- 与 case assignment/current effective configuration 最接近
- 最自然支撑单代理 fallback
- 对 commission generation / recompute 来说，source-of-truth 清晰
- 比 settlement-linked 方案更不容易混淆 definition 与 result

#### Weaknesses

- case domain 会承载更多 commission-related semantics
- 如果后续需要复杂历史版本化，扩展设计会更重

### Option B: `CommissionAllocation` 独立表

#### Strengths

- 语义最清晰
- 将 split definition 从 case 与 settlement 两侧解耦
- 对未来更复杂 allocation semantics 可扩展性最好

#### Weaknesses

- 对当前 MVP1 来说偏重
- 当前 repo 会引入更重的独立概念
- 若 source-of-truth 实际就是 case current config，这一层可能过度抽象

### Option C: `Settlement-linked allocation`

#### Strengths

- 直接贴近结算出口

#### Weaknesses

- 不适合作为 generation/recompute 的上游 source-of-truth
- 会把 split definition 错绑到 settlement result 层
- 对单代理 fallback 和未结算重算语义都不自然

## Current Recommendation

当前推荐顺序：

1. `CaseAgentSplit` 明细表
2. `CommissionAllocation` 独立表
3. `Settlement-linked allocation` 不推荐

## Recommended Carrier Choice

推荐选择：

- `CaseAgentSplit` 明细表

## Frozen Decision

- Final carrier choice:
  - `CaseAgentSplit` 明细表
- Final schema prerequisite recommendation:
  - 必须拆出 `COMMSPLIT-DB-01`

推荐理由：

- 与当前已冻结的“current effective configuration”语义最一致
- 最容易保持：
  - 单代理 fallback
  - generation/recompute 清晰
  - settlement/report compatibility
- 对 MVP1 当前结构最轻且最稳

## Schema Prerequisite Recommendation

正式建议：

- 必须拆出真正的 schema prerequisite task
- 推荐 follow-up 为：
  - `COMMSPLIT-DB-01`

该 follow-up 才处理：

- migration
- ORM model
- SQLite-safe schema details

## Deferred Slices Ledger

- `migration implementation`
- `ORM model implementation`
- `case API contract`
- `commission calculation`
- `settlement behavior changes`
- `FE editing/viewing`
- `reports / payout / export`

## Model-layer Impact

高概率影响：

- `cases` domain as source-of-truth owner
- downstream `commission` service consumption
- later settlement compatibility review

## API / Service Impact

本轮不直接改 API / service。

后续建议拆为：

- `COMMSPLIT-DB-01`
- `COMMSPLIT-BE-01`
- `COMMSPLIT-BE-02`
- `COMMSPLIT-FE-01`

## UI / Permission Impact

本轮不直接改 UI / permission。

## Cross-module Impact

- `cases`
- `commission`
- `settlement`
- `reports`
- frontend case page

## SQLite / Phase Compatibility Assessment

- 本轮 design decision 与当前 Phase 约束兼容
- 真正功能推进高概率需要 schema/migration prerequisite
- 因此当前结论仍是 prerequisite-first，而不是直接实现

## Risks / Blockers

- 若过早进入 DB 实现，可能把错误 carrier 固化
- 若选 `Settlement-linked allocation`，会混淆 definition 与 result
- 若过度设计成独立配置中心，会超出 MVP1

## Decomposition Recommendation

推荐拆法：

1. `COMMSPLIT-PRE-02`
   - durable carrier decision + schema prerequisite recommendation
2. `COMMSPLIT-DB-01`
   - durable carrier schema prerequisite
3. `COMMSPLIT-BE-01`
   - case contract / read current split config
4. `COMMSPLIT-BE-02`
   - calculation / recompute logic
5. `COMMSPLIT-FE-01`
   - case-page editing/viewing

## Exact Closure Slice Candidates

### Preferred first slice

- `COMMSPLIT-PRE-02`
  - 比较并冻结 durable split carrier 的三种候选方案，明确推荐 carrier 选择，并给出是否必须拆 schema prerequisite 的正式判断。

### Explicit non-closure

- 不实现 migration
- 不实现 ORM model
- 不实现 case API contract
- 不实现 commission calculation
- 不实现 settlement behavior changes
- 不实现 FE editing/viewing
- 不实现 reports / payout / export

## Design Conclusion

- `不可直接实现，必须先新增 prerequisite task(s)`
