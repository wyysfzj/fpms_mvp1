# P1 #5 多代理人提成分成 Prerequisite Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared commission program; prerequisite before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P1 #5 多代理人提成分成` 当前不能诚实地解释为一个“补一点提成规则”的 backend 小故事。当前 repo 只有 case 级 `second_agent_id`、commission 的 `s1_rate/s2_rate` 与既有 settlement 结构，但没有稳定的 multi-agent allocation carrier，也没有明确的 allocation ratio semantics 或 settlement ownership semantics。第一步不应直接进入 schema、API、service 或 FE 实现，而应先冻结 prerequisite 级设计结论。

## Assumptions

- 本条权威对象固定为：`commission allocation semantics`
- 当前明确不自动等同：
  - `Case.second_agent_id`
  - `Commission.s1_rate / s2_rate`
  - 现有 `CommissionSettlement / CommissionSettleLine`
- 第一轮只冻结：
  - allocation carrier definition
  - ratio / share semantics definition
  - settlement linkage semantics definition
- 第一轮结果形态固定为：
  - `prerequisite design / carrier freeze`
- 第一轮明确不包含：
  - schema/migration implementation
  - calculation logic
  - settlement UI
  - commission reports
  - historical migration/backfill
  - agent editing UI
  - payout/export

## Scope

- 盘点现有 `case / commission / settlement` 承载
- 明确哪些字段只能算上下文，不能算 multi-agent split carrier
- 比较 allocation carrier 与 settlement relation 的候选设计
- 给出 prerequisite-first decomposition recommendation

## Explicit Non-scope

- 一次做完整 multi-agent commission split program
- 直接实现 schema/migration
- 直接实现 commission generation / recompute
- 直接实现 case-page split editor
- 重做 settlement/report/export

## Exact Current Model / Field Inventory

### Case domain

- `backend/app/modules/cases/models.py`
  - `agent_id`
  - `second_agent_id`

Current interpretation:

- `second_agent_id` 只能算 case 辅助关系
- 不能表达多参与方集合
- 不能表达每个参与方 share ratio
- 不能表达 settlement ownership
- 不能被当作真实 split carrier

### Commission domain

- `backend/app/modules/commission/models.py`
  - `Commission.agent_id`
  - `Commission.base_fee`
  - `Commission.s1_rate / s1_amount / s1_done`
  - `Commission.s2_rate / s2_amount / s2_done`

Current interpretation:

- `s1/s2` 更像阶段或层级提成参数
- 不是 multi-agent allocation carrier
- 当前 commission row 仍然是一条记录对应一个 agent
- 不能被当作真实 split carrier

### Settlement domain

- `backend/app/modules/commission/models.py`
  - `CommissionSettlement`
  - `CommissionSettleLine`

Current interpretation:

- 现有 settle line 更像 settlement-to-commission 的单线条承载
- 当前没有显式 agent split line
- 当前没有 allocation participant carrier
- 不能被当作真实 split carrier

## Missing Carrier Analysis

当前 repo 中没有发现以下任一等价结构：

- `CommissionAllocation`
- `CommissionParticipant`
- `CommissionSplitLine`
- case-level current effective split detail table

因此，本条真实缺口在 carrier，而不是 service 层微调。

## Allocation Semantics Definition

第一轮必须冻结：

- 参与方来源
  - 是否来自 case-level current effective configuration
- 参与方集合
  - 是否只允许内部 agent 用户
- ratio 语义
  - `share_ratio` 是否以 100% 为总和约束
- 与单代理 fallback 的关系
  - 未配置 split 时如何保持现有单代理语义

## Settlement Linkage Options

只允许在以下三种候选里比较：

1. 一个 `commission` 对应多个 allocation lines
2. settlement line 按 agent split 展开
3. 独立 allocation entity，再映射到 settlement

当前推荐方向：

- 先冻结关系，不实现代码
- 明确哪种关系最能保留现有 settlement/report compatibility

## First-round Result Shape

第一轮交付物只应是：

- prerequisite design
- decomposition recommendation
- task/plan freeze

而不是：

- schema implementation
- API contract
- FE editing UI

## Deferred Slices Ledger

- `settlement UI`
- `commission reports`
- `historical migration/backfill`
- `agent editing UI`
- `payout/export`

## Model-layer Impact

高概率需要新增 durable carrier，影响：

- `cases` domain
- `commission` domain
- 可能的 settlement relation

但本轮不直接实现这些改动。

## API / Service Impact

本轮不直接改 API / service。

后续可能拆为：

- carrier prerequisite
- case contract
- commission calculation
- settlement linkage

## UI / Permission Impact

本轮不直接改 UI。

后续 FE 只应作为 follow-up story，且必须在 carrier 与 case contract 冻结后再进入 planning。

## Cross-module Impact

- `cases`
- `commission`
- `settlement`
- `reports`
- 可能影响 frontend case page

## SQLite / Phase Compatibility Assessment

- 作为 prerequisite design story：兼容当前 Phase 约束
- 作为真实功能实现：高概率需要 schema/migration prerequisite
- 因此本条当前结论不是直接实现，而是 prerequisite-first

## Risks / Blockers

- 语义偷换：
  - 把 `second_agent_id` 当 allocation carrier
  - 把 `s1/s2_rate` 当 split ratio
  - 把现有 settle line 当 multi-agent settlement
- 实施顺序错误：
  - 在 carrier 冻结之前写 calculation/UI
- scope creep：
  - 顺手吸收 settlement/report/export

## Decomposition Recommendation

推荐拆法：

1. `COMMSPLIT-PRE-01`
   - 冻结 allocation carrier / ratio semantics / settlement linkage semantics
2. `COMMSPLIT-PRE-02`
   - 若确认需要 durable carrier，则单独做 schema prerequisite
3. `COMMSPLIT-BE-01`
   - calculation logic
4. `COMMSPLIT-BE-02`
   - settlement linkage behavior
5. `COMMSPLIT-FE-01`
   - viewing/editing UI

## Exact Closure Slice Candidates

### Preferred first slice

- `COMMSPLIT-PRE-01`
  - 冻结多代理提成分成的 allocation carrier、ratio semantics、settlement linkage semantics，并明确当前 repo 中哪些现有字段只能视为相关上下文、不能视为真实 split carrier。

### Explicit non-closure

- 不实现 schema/migration
- 不实现 calculation logic
- 不实现 settlement UI
- 不实现 reports
- 不实现 historical migration/backfill
- 不实现 agent editing UI
- 不实现 payout/export

## Design Conclusion

- `不可直接实现，必须先新增 prerequisite task(s)`
