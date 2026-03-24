# Runbook Selection and Story Shape Classification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为本仓库落地“先做 Story Shape Classification，再选择 runbook，再进入 planning / execution”的最小可执行机制。

**Architecture:** 先在 `AGENTS.md` 增加强制规则，再补一个 repo-local 指引 skill 文件，随后补统一的计划模板和轻量 plan gate，最后用单独 QA close audit 验证这 4 个载体已经形成闭环。执行上采用文档 / 流程文件单路径原子任务，避免把规则、skill、模板、脚本混在一个 slice 里。

**Tech Stack:** Markdown, Python 3, repository policy docs, lightweight validation script

---

## Story Shape

- `shared_file_density: low`
- `prereq_dependency_density: medium`
- `be_fe_coupling: none`
- `evidence_cost: medium`

## Chosen Runbook

- `chosen_runbook: P0-prereq-heavy-story`
- Rationale: 本次目标不是产品功能，而是执行协议治理。真正的风险不在共享产品代码，而在是否先冻结规则、skill、模板与 gate 这组共享前置依赖；因此应先完成 prerequisite-style 基础设施，再允许后续故事使用。
- Non-selected runbooks:
  - `P0-single-lane-story`: 不适用，本次不围绕单一热点产品文件串行推进
  - `P0-multi-lane-parallel-story`: 不适用，规则与模板/脚本存在共享约束，不宜并行写入
  - `P0-frontend-heavy-story`: 不适用，本次不以前端交互为主

## Runbook Rationale

先冻结规则，再提供 skill，再统一计划模板，最后用脚本 gate 做可审计检查。任何顺序反过来都会造成“有模板没规则”或“有规则没执行入口”的失配。

## Preflight Dependency Audit

- `AGENTS.md` 必须先定义硬约束，否则后续 skill/plan 无法成为 repo 级强制
- repo-local skill 路径必须在仓库内稳定、可被 `AGENTS.md` 引用
- plan template 必须独立成文件，避免 runbook 结构只存在于单次计划文本
- gate 脚本必须基于固定标题进行最小校验，不能依赖模型推断
- QA close audit 需要在所有前述文件存在后执行

## Execution Mode

- Mode: serialized single-thread
- Why: 四个任务分别命中共享规则文件、共享 skill 文件、共享模板文件、共享 gate 脚本，不适合多 agent 并行写入

## Baseline Promotion Protocol

- 一个原子任务对应一个 fresh worktree
- reviewer diff 以 `HEAD^..HEAD` 为准
- 接受后立即固化为新基线提交
- 下一任务只能从最新接受基线开新 worktree
- 若某任务仅修改文档/脚本，也不得与其他任务共用未提交 worktree

## Replan Triggers

- 新发现 repo 已存在更高优先级的本地 skill / template 约定，与本计划路径冲突
- `AGENTS.md` 新增规则导致后续 task allowlist 失真
- gate 脚本实现时发现模板标题集合需要重定义
- reviewer 认定某任务实际跨越两个文件路径或两个 closure slice

## File Structure Lock

### Shared ownership

- `AGENTS.md`
- `skills/fpms-runbook-selection/SKILL.md`
- `docs/templates/runbook_plan_template.md`
- `scripts/validate_plan_runbook.py`

### Task document root

- `tasks/runbook-selection/`

## Atomic Task Inventory

Executable task docs:

- `tasks/runbook-selection/RBSEL-RULE-01.md`
- `tasks/runbook-selection/RBSEL-SKILL-01.md`
- `tasks/runbook-selection/RBSEL-TPL-01.md`
- `tasks/runbook-selection/RBSEL-GATE-01.md`
- `tasks/runbook-selection/RBSEL-QA-01.md`

## Wave Plan

Wave 1:
- `RBSEL-RULE-01`
- Mode: serialized, sole owner of `AGENTS.md`

Wave 2:
- `RBSEL-SKILL-01`
- Mode: serialized, sole owner of `skills/fpms-runbook-selection/SKILL.md`

Wave 3:
- `RBSEL-TPL-01`
- Mode: serialized, sole owner of `docs/templates/runbook_plan_template.md`

Wave 4:
- `RBSEL-GATE-01`
- Mode: serialized, sole owner of `scripts/validate_plan_runbook.py`

Wave 5:
- `RBSEL-QA-01`
- Mode: serialized, monitor-only final close audit after Waves 1-4 pass

## Task Steps

### Task 1: `RBSEL-RULE-01` Add mandatory repo rule

**Files:**
- Modify: `AGENTS.md`
- Spec: `tasks/runbook-selection/RBSEL-RULE-01.md`

- [ ] Read the approved spec and identify the exact mandatory rule set to add.
- [ ] Add a new `Story Shape Classification & Runbook Selection (MANDATORY)` section without weakening existing rules.
- [ ] Ensure the section explicitly requires classification in both spec and plan, requires `chosen_runbook`, and mandates replanning on new shared prerequisites.
- [ ] Verify wording does not accidentally apply to simple single-file or doc-only tasks.
- [ ] Run a focused text check:
  - `rg -n "Story Shape Classification|chosen_runbook|Replan|planning" AGENTS.md`
- [ ] Generate `artifacts/RBSEL-RULE-01/**`.
- [ ] Commit only task-allowlist changes.

### Task 2: `RBSEL-SKILL-01` Add repo-local skill

**Files:**
- Create: `skills/fpms-runbook-selection/SKILL.md`
- Spec: `tasks/runbook-selection/RBSEL-SKILL-01.md`

- [ ] Write the repo-local skill with one clear entry purpose: classify story shape and choose a runbook before `writing-plans`.
- [ ] Include the 4 required dimensions, the 4 runbook families, selection rules, and required outputs.
- [ ] Include explicit prompts for `Preflight Dependency Audit`, `Baseline Promotion Protocol`, and `Replan Triggers`.
- [ ] Keep the skill repo-local and self-contained; do not rewrite global superpowers skills.
- [ ] Run a focused text check:
  - `rg -n "shared_file_density|chosen_runbook|Preflight Dependency Audit|Baseline Promotion Protocol|Replan Triggers" skills/fpms-runbook-selection/SKILL.md`
- [ ] Generate `artifacts/RBSEL-SKILL-01/**`.
- [ ] Commit only task-allowlist changes.

### Task 3: `RBSEL-TPL-01` Add plan template

**Files:**
- Create: `docs/templates/runbook_plan_template.md`
- Spec: `tasks/runbook-selection/RBSEL-TPL-01.md`

- [ ] Create a reusable plan template section set for all multi-step tasks covered by the new mechanism.
- [ ] Ensure the template includes `Story Shape`, `Chosen Runbook`, `Runbook Rationale`, `Preflight Dependency Audit`, `Execution Mode`, `Baseline Promotion Protocol`, `Replan Triggers`, `Atomic Task Inventory`, and `Wave Plan`.
- [ ] Keep the template compatible with the existing `writing-plans` header style already used in the repo.
- [ ] Run a focused text check:
  - `rg -n "^## Story Shape|^## Chosen Runbook|^## Preflight Dependency Audit|^## Baseline Promotion Protocol|^## Replan Triggers" docs/templates/runbook_plan_template.md`
- [ ] Generate `artifacts/RBSEL-TPL-01/**`.
- [ ] Commit only task-allowlist changes.

### Task 4: `RBSEL-GATE-01` Add lightweight plan gate

**Files:**
- Create: `scripts/validate_plan_runbook.py`
- Spec: `tasks/runbook-selection/RBSEL-GATE-01.md`

- [ ] Write a small Python CLI that accepts a plan path and exits non-zero when any required section heading is missing.
- [ ] Require at least these headings: `Story Shape`, `Chosen Runbook`, `Preflight Dependency Audit`, `Baseline Promotion Protocol`, `Replan Triggers`.
- [ ] Print concise missing-section diagnostics suitable for task evidence logs.
- [ ] Verify the script passes against the plan created in this story and fails against a minimal malformed sample.
- [ ] Run targeted verification:
  - `python3 scripts/validate_plan_runbook.py docs/superpowers/plans/2026-03-24-runbook-selection-and-story-shape-implementation.md`
- [ ] Generate `artifacts/RBSEL-GATE-01/**`.
- [ ] Commit only task-allowlist changes.

### Task 5: `RBSEL-QA-01` Final close audit

**Files:**
- Modify: `artifacts/RBSEL-RULE-01/**`
- Modify: `artifacts/RBSEL-SKILL-01/**`
- Modify: `artifacts/RBSEL-TPL-01/**`
- Modify: `artifacts/RBSEL-GATE-01/**`
- Create: `artifacts/RBSEL-QA-01/results.jsonl`
- Create: `artifacts/RBSEL-QA-01/summary.md`
- Create: `artifacts/RBSEL-QA-01/git/diff.patch`
- Spec: `tasks/runbook-selection/RBSEL-QA-01.md`

- [ ] Run the task gate or equivalent focused verification for `RBSEL-RULE-01`, `RBSEL-SKILL-01`, `RBSEL-TPL-01`, and `RBSEL-GATE-01`.
- [ ] Confirm the new rule, skill, template, and gate all exist on the accepted baseline.
- [ ] Validate that the implementation plan itself satisfies the new gate.
- [ ] Produce a summary ledger mapping each mechanism layer to its concrete file path and verification evidence.
- [ ] Generate `artifacts/RBSEL-QA-01/**`.
- [ ] Commit only evidence-only changes allowed by the task.

