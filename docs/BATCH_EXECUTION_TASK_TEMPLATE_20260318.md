# Batch Execution Task Template (2026-03-18)

## Purpose

This template defines the required shape of every future atomic task file.

It exists to prevent:
- cluster-sized task definitions
- acceptance criteria that are broader than the intended closure slice
- ambiguous QA closure
- main-thread takeover that silently expands scope

This template is normative for all future post-enhancement tasks.

## Required Header

```md
# <TASK-ID> — <short task title>

- Source: `<manifest path>`
- Type: `endpoint` | `service` | `page` | `api client` | `qa gate` | `doc`
- Execution mode: Atomic (single-task, single-owner)
```

## Required Sections

### 1. Task Definition

Must contain:
- Goal
- Covered items
- Allowlist
- Out of scope
- Shared ownership flag
- Verification

### 2. Exact Closure Slice

This section is mandatory.

It must answer:
- What exact behavior does this task close?
- What is the smallest user-visible or contract-visible outcome that should change?
- Which single endpoint / service rule / page capability / query slice is being closed?

Example:
- close `PER_CLAIM` amount calculation only
- close receipt summary visibility for `last_receipt_date` only
- close `DELETE /tasks/{id}` 204 contract only

Disallowed wording:
- “close the remaining module”
- “finish the whole chain”
- “complete backend/frontend parity”
- “close the remaining feasible scope”

### 3. Explicit Non-Closure Statement

This section is mandatory.

It must explicitly list what this task does NOT close, even if those items are related.

Example:
- does not close `PER_PAGE`
- does not close fee draft list/detail parity
- does not close pay-list workflow
- does not close dashboard integration

If nothing remains, state that explicitly and justify why.

### 4. Remaining Follow-up Task IDs

This section is mandatory unless the task truly closes the full item.

List:
- follow-up task IDs that still remain after this slice
- or `None`

### 5. Done Definition

This section is mandatory.

A task may claim `PASS` only if all of the following are true:
- allowlist stayed clean
- the exact closure slice is implemented
- the explicit non-closure boundary was respected
- required verification passed
- required artifacts exist
- `./scripts/task_validate.sh <TASK-ID>` passed

### 6. Dirty Baseline Artifacts

This section is mandatory.

Every task must name two baseline artifacts:
- `artifacts/<TASK-ID>/baseline_allowlist.diff`
- `artifacts/<TASK-ID>/baseline_external_files.txt`

If a file had pre-existing dirty changes, acceptance must be limited to the incremental delta after the baseline.

### 7. Execution Checklist

Required checklist:

```md
- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
```

## Required Task File Skeleton

```md
# <TASK-ID> — <short task title>

- Source: `<manifest path>`
- Type: `<type>`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
- Covered items:
  - `<item>`
- Allowlist:
  - `<file>`
- Out of scope:
  - `<boundary>`
- Shared ownership:
  - `Yes` / `No`
- Verification:
  - `<cmd>`

## Exact Closure Slice

- This task closes exactly:
  - `<single closure slice>`

## Explicit Non-Closure Statement

- This task does NOT close:
  - `<remaining gap>`

## Remaining Follow-up Task IDs

- `<TASK-ID>` or `None`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/<TASK-ID>/baseline_allowlist.diff`
- `artifacts/<TASK-ID>/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
```

## Enforcement

If a proposed task file does not clearly separate:
- exact closure
- explicit non-closure
- remaining follow-up

then the task must NOT be executed until rewritten.
