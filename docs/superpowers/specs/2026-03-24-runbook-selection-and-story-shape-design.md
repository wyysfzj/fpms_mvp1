# Runbook Selection and Story Shape Classification Design

Date: 2026-03-24

Scope: 为当前仓库增加一套可审计的“先分类、再选 runbook、再进入 planning/execution”的机制，降低类似 `FR-FE-04` 这类多步骤故事在执行中的返工、worktree 污染和共享前置依赖漏判问题。

---

## 1. Goal

本设计的目标不是引入“自动智能编排器”，而是把多步骤任务的执行协议前移、标准化、可审计化。

机制必须实现以下效果：

1. 进入 `writing-plans` 之前，先做 `Story Shape Classification`
2. 在 spec 和 plan 中显式记录 `chosen_runbook`
3. 遇到新的共享前置依赖时，强制回退到 planning，而不是继续在错误基线上执行
4. reviewer / lead 能依据统一结构审查执行协议，而不是依赖个人记忆

本机制覆盖范围：

- 所有需要 `writing-plans` 的多步骤任务

本机制不覆盖：

- 简单单文件修复
- 纯文档修订
- 纯问答类任务
- 自动业务拆分
- 自动生成 atomic task

---

## 2. Problem Statement

`FR-FE-04` 的最终闭环已经完成，但过程暴露出 3 类系统性问题：

1. 共享前置依赖识别过晚
- `PayList.Read`、`PayList.Export`、状态机前置规则并未在初始计划阶段冻结
- 导致执行中途插入 `RBAC` 与 `STATE` 任务，打断基线推进

2. worktree / baseline 协议未前置冻结
- 早期任务曾在同一 worktree 上串行推进，导致 diff 污染
- reviewer 不能把任务视为干净的单 slice

3. evidence gate 触发过晚
- 早期任务 evidence 在最终 QA 阶段才补齐和规范化
- 把本应在任务关闭时暴露的问题推迟到故事关闭时才显现

因此，本设计要解决的是“执行拓扑与协议治理”，不是单个业务故事本身。

---

## 3. Core Model

### 3.1 Story Shape Classification

任何进入 `writing-plans` 的多步骤任务，必须先记录以下 4 个维度：

- `shared_file_density`
- `prereq_dependency_density`
- `be_fe_coupling`
- `evidence_cost`

记录格式不追求复杂打分，采用简洁定性值即可，例如：

- `shared_file_density: high`
- `prereq_dependency_density: high`
- `be_fe_coupling: chained (BE -> FE)`
- `evidence_cost: high`

必须再补一个汇总结论：

- `chosen_runbook: <runbook-id>`

### 3.2 Runbook Family

初始版本只定义 4 个 runbook：

1. `P0-single-lane-story`
- 适用：热点文件集中、整体只能串行推进

2. `P0-prereq-heavy-story`
- 适用：真正难点在共享前置依赖冻结，未先清 prereq 会反复返工

3. `P0-multi-lane-parallel-story`
- 适用：多个任务切片分布在不同文件群，可安全并行分波

4. `P0-frontend-heavy-story`
- 适用：后端 contract 基本稳定，主要工作量在前端交互与页面闭环

### 3.3 Selection Rules

选择规则采用简单优先级，而非复杂算法：

- 若 `shared_file_density = high` 且 `be_fe_coupling = chained`，优先 `P0-single-lane-story`
- 若 `prereq_dependency_density = high`，无论主 runbook 是什么，都必须执行 `Preflight Dependency Audit`
- 若共享文件低且任务切片彼此独立，才允许 `P0-multi-lane-parallel-story`
- 若后端 contract 已冻结且 UI 是主要工作量，才允许 `P0-frontend-heavy-story`

### 3.4 Example Classification

`FR-FE-04` 应作为标准样例记录为：

- `shared_file_density: high`
- `prereq_dependency_density: high`
- `be_fe_coupling: chained (BE -> FE)`
- `evidence_cost: high`
- `chosen_runbook: P0-single-lane-story`

---

## 4. Layered Enforcement Model

该机制采用三层叠加：

### 4.1 AGENTS.md

`AGENTS.md` 负责铁律与强制条件：

- 所有进入 `writing-plans` 的多步骤任务，必须先做 `Story Shape Classification`
- classification 必须同时记录在 spec 与 plan 中
- 必须显式写出 `chosen_runbook`
- 未完成 classification 和 runbook 选择前，不得进入 execution
- 若执行中发现新的共享前置依赖、共享 ownership 冲突、或主状态机不可达，必须回退到 planning
- reviewer / lead 不得接受未声明 `chosen_runbook` 的多步骤计划

### 4.2 Repo-local Skill

新增 repo-local skill，建议命名为：

- `fpms-runbook-selection`

该 skill 负责：

- 读取当前故事背景与已有约束
- 产出 4 维 classification
- 选择 `chosen_runbook`
- 生成 `Preflight Dependency Audit`
- 指定推荐执行方式：
  - `single-thread`
  - `serialized subagent`
  - `multi-lane parallel`
- 为 plan 生成固定章节骨架

### 4.3 Template / Gate

为防止流程流于形式，新增：

- plan 模板段落
- 轻量校验脚本

模板必须要求的章节：

- `Story Shape`
- `Chosen Runbook`
- `Runbook Rationale`
- `Preflight Dependency Audit`
- `Execution Mode`
- `Baseline Promotion Protocol`
- `Replan Triggers`
- `Atomic Task Inventory`
- `Wave Plan`

轻量 gate 建议为：

- `scripts/validate_plan_runbook.py`

职责仅为结构校验，不做复杂智能判断。

---

## 5. Required Plan Structure

所有适用本机制的计划文档，必须包含以下最小结构：

### 5.1 Story Shape

记录：

- `shared_file_density`
- `prereq_dependency_density`
- `be_fe_coupling`
- `evidence_cost`

### 5.2 Chosen Runbook

记录：

- `chosen_runbook`
- 为什么选择它
- 为什么没有选择其他 runbook

### 5.3 Preflight Dependency Audit

至少检查：

- 权限 / RBAC 前置依赖
- 状态机可达性
- 共享所有权文件冲突
- 共享测试文件冲突
- router / shared schema / export helper / permission registry / shared API client 等共享文件是否需前置切出

### 5.4 Baseline Promotion Protocol

计划必须显式写明：

- 一个原子任务对应一个 fresh worktree
- reviewer diff 以 `HEAD^..HEAD` 为准
- 接受后立即固化为新基线提交
- 下一任务只能从“最新接受基线”开新 worktree

### 5.5 Replan Triggers

计划必须列出触发回退到 planning 的条件，例如：

- 新的共享前置依赖被发现
- 共享文件冲突超出当前 allowlist
- 状态机不可达
- 任务 closure slice 实际依赖第二个未拆分 slice
- reviewer 认定当前计划缺失 prerequisite wave

---

## 6. First-phase Implementation Scope

第一阶段只做最小可执行版：

1. 修改 `AGENTS.md`
- 新增 `Story Shape Classification & Runbook Selection (MANDATORY)` 章节

2. 新增 repo-local skill
- `fpms-runbook-selection`

3. 新增 plan 模板或模板段落
- 强制出现上述结构

4. 新增轻量 gate 脚本
- `scripts/validate_plan_runbook.py`

第一阶段明确不做：

- 自动评分或自动分类引擎
- 过多 runbook 类型
- 现有所有旧计划的全面迁移
- 与全局 superpowers 技能的深度侵入式改造
- 自动生成 atomic task

---

## 7. Success Criteria

第一阶段成功标准：

1. 新的多步骤故事在 planning 前会显式完成 classification
2. spec 和 plan 都包含 `chosen_runbook`
3. 新共享前置依赖出现时，执行会回退到 planning，而不是继续硬推
4. reviewer 可基于统一结构审查执行协议
5. 类似 `FR-FE-04` 的单泳道故事不会再出现“执行中临时发明基线协议”的情况

---

## 8. Open Decisions Resolved

本设计已确认以下决策：

- 覆盖范围：所有需要 `writing-plans` 的多步骤任务
- 记录载体：spec 与 plan 都要有，plan 是最终执行依据
- 失配处理：发现新共享前置依赖时必须回退到 planning
- 主入口：`AGENTS.md` 与 skill 并列强制，模板/gate 提供可审计约束

---

## 9. Recommended Next Step

下一步应使用 `writing-plans` 为本设计生成实施计划，并拆分为原子任务，至少包括：

- `AGENTS.md` 规则增补
- repo-local skill 新建
- plan template / template section 新建
- `scripts/validate_plan_runbook.py` 新建

