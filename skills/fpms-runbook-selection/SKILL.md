---
name: fpms-runbook-selection
description: "Use when preparing any multi-step FPMS task that needs writing-plans: classify story shape, choose a runbook, and emit the minimum planning fields required by the governance rule."
---

# FPMS Runbook Selection

Use this skill before `writing-plans` for any multi-step story. The goal is not automation; the goal is to force an explicit, auditable choice of execution shape before planning starts.

## First Pass

Before any classification or output-format rules, read the current story background and the existing constraints first. Use the task/spec context, the task file, and any governing repo rules as the source of truth before choosing a runbook.

## When To Use

Use this skill when a task is more than a simple single-file change and needs a plan, wave structure, or follow-up tasks.

Do not use it for:

- trivial single-file fixes
- pure documentation edits
- one-off questions that do not need planning

## Required Story Shape Classification

Classify the story with these four dimensions:

- `shared_file_density`
- `prereq_dependency_density`
- `be_fe_coupling`
- `evidence_cost`

Use short qualitative values. Examples:

- `shared_file_density: low | medium | high`
- `prereq_dependency_density: low | medium | high`
- `be_fe_coupling: none | chained (BE -> FE) | coupled`
- `evidence_cost: low | medium | high`

Always add:

- `chosen_runbook: <runbook-id>`

## Runbook Families

Choose one of these runbooks:

1. `P0-single-lane-story`
   - Use when the task is concentrated in one hotspot and must move serially.

2. `P0-prereq-heavy-story`
   - Use when the hardest part is freezing shared prerequisites before execution can proceed.

3. `P0-multi-lane-parallel-story`
   - Use when the work can be safely split across independent lanes or waves.

4. `P0-frontend-heavy-story`
   - Use when backend contract is already stable and the main work is UI closure.

## Selection Rules

Apply these rules in order:

- If the story cannot start until shared prerequisites are frozen, or if `prereq_dependency_density = high`, you must choose `P0-prereq-heavy-story`.
- This prereq-heavy rule overrides every other runbook choice. Do not select `P0-single-lane-story`, `P0-multi-lane-parallel-story`, or `P0-frontend-heavy-story` when the prereq-heavy condition applies.
- If `shared_file_density = high` and `be_fe_coupling = chained`, prefer `P0-single-lane-story`.
- When `P0-prereq-heavy-story` is chosen, require a `Preflight Dependency Audit` before execution.
- If both `P0-multi-lane-parallel-story` and `P0-frontend-heavy-story` are eligible, choose `P0-frontend-heavy-story`.
- If only shared files are low and the slices are independent, choose `P0-multi-lane-parallel-story`.
- If only backend contract is frozen and the UI is the main workload, choose `P0-frontend-heavy-story`.

## Required Planning Outputs

When you move into planning, ensure the spec and the plan both record:

- `Story Shape`
- `chosen_runbook`
- `Runbook Rationale`
- `Preflight Dependency Audit`
- `Execution Mode`
- `Baseline Promotion Protocol`
- `Replan Triggers`
- `Atomic Task Inventory`
- `Wave Plan`

## Preflight Dependency Audit

Before execution, check for:

- permission and RBAC prerequisites
- state machine reachability
- shared ownership file conflicts
- shared test file conflicts
- router wiring, shared schemas, export helpers, permission registries, and shared API clients that may need to be cut out first

If a new shared prerequisite appears, stop and replan instead of pushing forward on the wrong baseline.

## Baseline Promotion Protocol

Use this baseline policy:

- one atomic task owns one fresh worktree
- reviewer diff is judged against `HEAD^..HEAD`
- accepted work becomes the next baseline commit immediately
- the next task starts from the latest accepted baseline in a new worktree

## Replan Triggers

Replan when any of these appear:

- a new shared prerequisite is discovered
- shared ownership conflicts exceed the current allowlist
- the state machine is not reachable
- the apparent slice actually depends on a second uncut slice
- the plan is missing a prerequisite wave

## Recommended Execution Mode

Map the chosen runbook to an execution mode:

- `P0-single-lane-story` -> `single-thread`
- `P0-prereq-heavy-story` -> `serialized subagent`
- `P0-multi-lane-parallel-story` -> `multi-lane parallel`
- `P0-frontend-heavy-story` -> `serialized subagent` or `multi-lane parallel`, depending on shared-file risk

## Minimum Output Template

Use a compact structure like this in the spec and plan:

```md
## Story Shape
- shared_file_density: ...
- prereq_dependency_density: ...
- be_fe_coupling: ...
- evidence_cost: ...

## Chosen Runbook
- chosen_runbook: ...

## Runbook Rationale
- why this runbook
- why the others were not chosen

## Preflight Dependency Audit
- ...

## Execution Mode
- ...

## Baseline Promotion Protocol
- ...

## Atomic Task Inventory
- ...

## Wave Plan
- ...

## Replan Triggers
- ...
```

Keep the classification explicit. If the story cannot be classified cleanly, do not enter `writing-plans` yet.
