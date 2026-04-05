# Grant Fee Document / Reminder Linkage Semantics Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `semantics freeze before linkage implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`GF-RESIDUAL-SPEC-01` 已明确 `document / reminder linkage` 是 `#15 授权费管理` 的下一类 residual。当前 repo 中已经存在：

- grant-fee task 自身的 `notice_sent / notify_count` carrier
- 通用文书模块 `Document / DocTemplate / DocAttachment`
- 通用任务模块 `Task / TaskTemplate`

但还没有 grant-fee 专属的 reminder/document linkage authority。现在不能直接实现“生成授权费通知书”或“补建提醒任务”，否则会把通知语义、文书生成、任务回投和状态联动混成一条故事。当前必须先冻结：

- grant-fee reminder/document 的 source-of-truth
- 第一轮 linkage 到底是 reminder-only、document-only，还是两者都不自动进入
- 第一条最小 follow-up story 应该关闭哪一个可验证行为

## Assumptions

- 当前 grant-fee task carrier 已存在：
  - `T_GrantFeeTask.notice_sent`
  - `T_GrantFeeTask.notify_count`
- 当前通用文书 authority 已存在：
  - `Document`
  - `DocTemplate`
  - 单文书附件与模板渲染链
- 当前通用任务 authority 已存在：
  - `Task`
  - `TaskTemplate`
- 第一轮 document/reminder linkage 不自动包含：
  - dispatch / envelope
  - outgoing document wizard
  - billing / receipt semantics

## Scope

- 冻结 grant-fee document/reminder linkage 的 source-of-truth
- 冻结 grant-fee `notice_sent / notify_count` 与真实文书/提醒对象的边界
- 冻结第一轮 in-scope 的最小 linkage slice
- 推荐一个最小 follow-up story

## Explicit Non-scope

- 不做任何 grant-fee / documents / tasks 产品实现补丁
- 不做 bill / receipt semantics
- 不更新 `#15` close decision

## Current Carrier Assessment

### Available

- grant-fee task side:
  - `notice_sent`
  - `notify_count`
  - worklist 已显示 “已通知 / 待通知”
- documents side:
  - `Document`
  - `DocTemplate`
  - outgoing document creation/edit/detail flows
- tasks side:
  - `Task`
  - `TaskTemplate`
  - 通用基于文书的 deadline/reminder 生成

### Missing as explicit contract

- grant-fee notice 是否必须落成真实 `Document`
- grant-fee reminder 是否必须落成真实 `Task`
- `notice_sent` 是否等价于“已有文书”
- `notify_count` 是否等价于“已有 reminder attempts”
- 第一轮应该先做观察性 visibility，还是直接做生成动作

## Authority Freeze

### Reminder / document source-of-truth

- 第一轮 `GF-DOC` authority **不**把 `notice_sent` 直接等价为真实 `Document` existence
- 第一轮 `GF-DOC` authority **不**把 `notify_count` 直接等价为真实 `Task` existence
- `notice_sent / notify_count` 当前只代表 grant-fee workflow 内部通知状态 carrier

### First-round linkage rule

- 第一轮 document/reminder linkage 应先保持 observational / contract-freeze 解释
- 真实文书或提醒对象必须来自通用模块中的显式对象：
  - `Document`
  - `Task`
- 如果没有这样的显式对象，就不能把 grant-fee 行标记为“已关联合同文书/提醒”

### Recommended first product slice

- 第一轮推荐先做 `GF-NOTICE-VIS-01`
- exact closure candidate:
  - 只在 grant-fee worklist 上增加一个只读 visibility slice
  - 明确显示当前内部通知状态 carrier：
    - `notice_sent`
    - `notify_count`
  - 并将“文书联动”继续保留为 deferred，而不是假装已有真实 `Document`

### Why this is recommended first

- 当前 worklist 已经承载通知状态展示，最小 follow-up 是把其语义说明和 visibility 做严谨，而不是直接跨模块生成对象
- 直接做文书生成会同时碰：
  - grant-fee task state
  - documents creation flow
  - template selection
  - case/document lineage
- 直接做提醒任务会同时碰：
  - tasks module
  - reminder semantics
  - duplicate prevention

## Residuals Explicitly Deferred

- grant-fee 专属 `Document` 生成
- grant-fee 专属 `Task` reminder 生成
- dispatch / envelope
- outgoing document template resolution
- notice proof 回投到 grant-fee 状态机

## SQLite / Phase Compatibility Assessment

- This semantics-freeze story is doc-only and compatible
- The recommended first follow-up `GF-NOTICE-VIS-01` appears achievable without schema change
- Any later true document/task generation slice must be split as a separate cross-module story

## Risks / Blockers

- treating `notice_sent` as proof that a real outgoing document exists
- treating `notify_count` as proof that real reminder tasks exist
- folding visibility, document generation, task generation, and state-machine updates into one story

## Exact Closure Slice Candidates

### Preferred

- `GF-DOC-SPEC-01`
  - freeze grant-fee document/reminder linkage semantics and recommend one narrow follow-up story

### Explicit non-closure

- no product implementation
- no real document/task linkage
- no close update for `#15`

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
