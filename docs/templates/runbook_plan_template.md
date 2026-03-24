# Runbook Plan Template

Use this template for any multi-step plan that must classify story shape and select a runbook before execution.

---

## Story Shape

- shared_file_density: `<low|medium|high>`
- prereq_dependency_density: `<low|medium|high>`
- be_fe_coupling: `<none|chained (BE -> FE)|parallel>`
- evidence_cost: `<low|medium|high>`

## Chosen Runbook

- chosen_runbook: `<P0-single-lane-story|P0-prereq-heavy-story|P0-multi-lane-parallel-story|P0-frontend-heavy-story>`

## Runbook Rationale

- Why this runbook fits the story shape:
- Why the other runbooks were not chosen:

## Preflight Dependency Audit

- Permission / RBAC prerequisites:
- State machine reachability:
- Shared ownership file conflicts:
- Shared test file conflicts:
- Router / shared schema / export helper / permission registry / shared API client checks:

## Execution Mode

- Mode: `<single-thread|serialized subagent|multi-lane parallel>`
- Why this execution mode is safe for the current story shape:

## Baseline Promotion Protocol

- One atomic task equals one fresh worktree.
- Reviewer diff is evaluated as `HEAD^..HEAD`.
- Accepted work is committed immediately as the new baseline.
- The next task starts from the latest accepted baseline only.

## Replan Triggers

- A new shared prerequisite is discovered.
- A shared file conflict exceeds the current allowlist.
- The state machine is no longer reachable from the current baseline.
- The closure slice depends on a second unplanned slice.
- The reviewer determines the current plan is missing a prerequisite wave.

## Atomic Task Inventory

- `<TASK-ID>`:
  - Exact closure slice:
  - Explicit non-closure:
  - Remaining follow-up task ids:
  - Allowlist:
  - Done definition:

## Wave Plan

- Wave 1:
  - Tasks:
  - Mode:
  - Shared ownership notes:
- Wave 2:
  - Tasks:
  - Mode:
  - Shared ownership notes:
- Wave 3:
  - Tasks:
  - Mode:
  - Shared ownership notes:
