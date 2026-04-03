# P1 #5 多代理人提成分成 Existing Carrier Reclassification Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared commission program; carrier status assessment before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`COMMSPLIT-DB-01` 不能直接继续按 “mandatory schema prerequisite” 执行，因为当前 repo 中已经存在并被消费的 `CaseAgentSplit / T_CaseAgentSplit` 结构。当前真正需要关闭的是一次纠偏型 assessment：判定现有 `CaseAgentSplit` 究竟是 `真实 durable carrier`、`部分 carrier 但语义不足`，还是 `仅是 UI/case 辅助结构`，并据此决定 `COMMSPLIT-DB-01` 是否应保留、改名、降级或删除。

## Assumptions

- 本轮是一个 `reclassification checkpoint`
- 权威对象固定为：
  - `existing CaseAgentSplit carrier status`
- 本轮判断标准固定为：
  - 是否能稳定表达多参与方
  - 是否能稳定表达 `share_ratio`
  - 是否能作为 commission calculation 的 source-of-truth
  - 是否已被 commission service 实际消费
  - 是否能支撑单代理 fallback
  - 是否缺少关键约束或状态语义
- 本轮结果形态固定为：
  - `carrier status assessment`
  - `task reclassification recommendation`
- 本轮最小闭环固定为：
  - 评估 `CaseAgentSplit` 的真实 carrier 地位
  - 判断 `COMMSPLIT-DB-01` 是否仍应存在
  - 如需调整，给出新的 follow-up mapping
  - explicit deferred slices

## Scope

- 核对现有 `CaseAgentSplit / T_CaseAgentSplit` 的模型、schema、service、API、commission consumption
- 判断其是否已经构成 current effective split source-of-truth
- 评估 `COMMSPLIT-DB-01` 的存续必要性
- 输出 reclassification recommendation

## Explicit Non-scope

- schema/migration changes
- ORM model changes
- commission calculation changes
- settlement linkage changes
- API contract changes
- FE viewing/editing
- report/payout/export

## Existing Evidence

### Model-layer evidence

- [cases/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/models.py)
  - `class T_CaseAgentSplit`
  - columns:
    - `case_id`
    - `agent_id`
    - `role`
    - `share_ratio`
  - uniqueness:
    - `uq_case_agent_split_agent`

### Schema evidence

- [cases/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/schemas.py)
  - `class CaseAgentSplitIn`
  - `agent_splits: list[CaseAgentSplitIn] | None = None`

### Service/API evidence

- [cases/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/service.py)
  - `validate_case_agent_splits(...)`
  - delete + recreate case split rows
- [cases/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/api.py)
  - reads `T_CaseAgentSplit.agent_id`
  - reads `T_CaseAgentSplit.role`
  - reads `T_CaseAgentSplit.share_ratio`

### Commission consumption evidence

- [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
  - reads `T_CaseAgentSplit.agent_id`
  - reads `T_CaseAgentSplit.share_ratio`
  - therefore `CaseAgentSplit` is already consumed by commission logic

## Assessment Against the Frozen Criteria

### Multi-participant support

- Current assessment:
  - `Yes`

### `share_ratio` support

- Current assessment:
  - `Yes`

### Commission source-of-truth viability

- Current assessment:
  - `Partially yes`
- Rationale:
  - `commission/service.py` already reads split rows, but the current repo still needs a sharper judgment on whether this is the sole authoritative split source and whether fallback semantics are fully frozen.

### Commission service consumption

- Current assessment:
  - `Yes`

### Single-agent fallback

- Current assessment:
  - `Likely yes, but needs explicit semantic confirmation`

### Missing constraints / state semantics

- Current assessment:
  - `Likely yes`
- High-probability gaps:
  - ratio-total semantics
  - primary/secondary role semantics
  - current/effective split semantics
  - settlement linkage semantics as consumer-only vs source-of-truth

## Reclassification Recommendation

- `COMMSPLIT-DB-01` should NOT proceed as a default schema prerequisite
- `COMMSPLIT-DB-01` should be repurposed into:
  - existing carrier status assessment
  - task tree correction
  - follow-up remapping

## Frozen Assessment Snapshot

- Carrier classification:
  - `partial carrier`
- Frozen interpretation:
  - `CaseAgentSplit / T_CaseAgentSplit` is a real persisted and consumed carrier, so it is not an auxiliary-only UI structure.
  - It is still partial because the current code only proves current-effective split rows, validation, API exposure, and commission consumption, while broader settlement / report / source-of-truth semantics remain deferred.
- Old `COMMSPLIT-DB-01` meaning:
  - `mandatory DB prerequisite` is removed
  - the story is narrowed and renamed to `existing carrier reclassification checkpoint`
- Follow-up mapping:
  - `COMMSPLIT-BE-01` freezes case / commission split contract semantics
  - `COMMSPLIT-BE-02` handles calculation / recompute logic
  - `COMMSPLIT-BE-03` handles settlement linkage semantics if still needed
  - `COMMSPLIT-FE-01` handles case-page viewing / editing

## Current Recommendation

1. Repurpose `COMMSPLIT-DB-01` into a reclassification checkpoint
2. After that checkpoint:
   - if `CaseAgentSplit` is sufficient, continue with narrowed backend semantic-hardening follow-ups
   - if `CaseAgentSplit` is insufficient, open a new narrowed DB task with evidence-backed scope

## Recommended Follow-up Mapping

- `COMMSPLIT-DB-01`
  - reclassification checkpoint only
- `COMMSPLIT-BE-01`
  - freeze case/commission split contract semantics
- `COMMSPLIT-BE-02`
  - calculation / recompute logic
- `COMMSPLIT-BE-03`
  - settlement linkage semantics if still needed
- `COMMSPLIT-FE-01`
  - case-page viewing/editing

## Deferred Slices Ledger

- `schema/migration changes`
- `ORM model changes`
- `commission calculation changes`
- `settlement linkage changes`
- `API contract changes`
- `FE viewing/editing`
- `report/payout/export`

## SQLite / Phase Compatibility Assessment

- This assessment wave is compatible with current Phase constraints because it is document-only.
- If a later wave proves the existing `CaseAgentSplit` schema insufficient, that later wave must open a narrowed DB task explicitly.
- If the existing schema is sufficient, later work may shift toward `Phase 3.5` service semantics rather than DB prerequisites.

## Risks / Blockers

- Continuing to treat `COMMSPLIT-DB-01` as mandatory DB work would preserve an already weakened premise.
- Treating existing commission consumption as full closure would also be incorrect; current evidence only proves that `CaseAgentSplit` is already a real participant in the domain.
- The key risk is mixing:
  - existing carrier facts
  - missing semantics
  - future implementation work
  into one story.

## Exact Closure Slice Candidates

### Preferred first slice

- `COMMSPLIT-DB-01`
  - assess whether the existing `CaseAgentSplit` already constitutes the durable carrier and decide whether the old DB prerequisite interpretation should be kept, narrowed, renamed, or removed

### Explicit non-closure

- no schema/migration changes
- no ORM model changes
- no service changes
- no API changes
- no frontend changes
- no settlement/report implementation

## Design Conclusion

- `不可直接实现，必须先新增 prerequisite task(s)`
- The prerequisite here is no longer “new DB carrier by default”; it is “assessment and task-tree correction before any implementation wave.”
- `CaseAgentSplit` is frozen as a partial carrier, not an auxiliary-only structure, so the old mandatory DB prerequisite reading is removed in favor of the reclassification checkpoint.
