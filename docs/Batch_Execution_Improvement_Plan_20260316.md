# Batch Execution Improvement Plan (2026-03-16)

## Purpose

This document records the execution lessons from `Batch 1` and `Batch 2` and turns them into mandatory operating rules for all later batches.

Effective immediately:
- future batches MUST follow this document
- future batches MUST also follow the batch-specific execution runbook
- no batch may start implementation before the freeze + manifest rules below are satisfied

## Background

Observed issues across `2026-03-15` and `2026-03-16`:
- execution often started from a high-level batch plan instead of an explicit manifest
- atomic task size was too large, so workers finished only one slice while the main thread waited for a whole cluster
- dirty worktree contamination made valid diffs hard to accept cleanly
- evidence and task-gate closure happened too late
- frontend gate semantics were brittle because `task_validate.sh` expects `lint + test`
- workers were misclassified as `idle` when they were actually still producing diffs or artifacts
- close audits started before the implementation tasks had truly closed

## Root Cause Summary

The main failure mode was not model capability. The main failure mode was execution discipline:
- start implementing before freezing scope
- start coding before defining atomic task ownership
- start auditing before evidence was complete
- treat cluster-sized tasks as atomic tasks

## Mandatory Improvements

### 1. Freeze Before Implementation

Every batch MUST begin with a formal freeze step.

Required outputs:
- covered `Partially Implemented` items
- excluded items
- shared ownership files
- forbidden files / forbidden modules
- candidate execution waves
- identified `Deferred` and `Blocked` items

Without a freeze output, implementation MUST NOT begin.

### 2. Explicit Batch Manifest Is Mandatory

Every batch MUST be converted from plan form into an explicit manifest before coding starts.

Every manifest row MUST include:
- `task_id`
- exact task file path
- owner role
- allowlist
- required verification
- dependency notes
- shared-file flag
- done definition

If there is no explicit manifest:
- no real multi-agent implementation may start
- execution must remain in planning mode only

### 3. Smaller Atomic Tasks

One atomic task MUST equal one closure slice.

Allowed examples:
- one backend endpoint behavior
- one service-layer behavior
- one frontend page capability
- one final QA close audit

Disallowed examples:
- one whole module cluster
- one mixed backend+frontend mega task
- one task that combines defaults + linkage + queries + dashboard

### 4. Slice-Stop Rule

Each worker MUST stop after one gateable slice.

Required order:
1. add the smallest failing test or failing proof
2. implement the smallest fix
3. run minimal verification
4. generate evidence artifacts
5. report result

Workers MUST NOT silently continue into the next slice inside the same atomic task.

### 5. Dirty Worktree Baseline

Before each wave:
- record allowlist baseline diff
- record known allowlist-external modifications

Acceptance MUST evaluate only the incremental diff created after the baseline.

Existing unrelated dirty changes:
- MUST NOT be counted as current-task work
- MUST NOT relax allowlist boundaries

### 6. Evidence-First Closure

Every task claiming `PASS` MUST produce:
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/git/diff.patch`

Evidence generation is not a cleanup step. It is part of task completion.

### 7. Frontend Gate Contract

Until `scripts/task_validate.sh` is changed, frontend tasks MUST record:
- `step=lint` for lint
- `step=test` for typecheck

Reason:
- current gate script only validates `lint` and `test`
- without this convention, frontend tasks can fail the gate even when implementation is correct

### 8. Idle Triage Standard

Main thread MUST NOT mark a worker `idle` based only on a wait timeout.

Before labeling a worker idle, check all of:
- has allowlist diff grown recently
- have artifacts appeared or changed
- is the verification process still running
- is the task only missing evidence/gate closure

Only if all of the above remain unchanged for a sustained interval may the worker be treated as truly idle.

### 9. Close Audit Timing

Final QA close audit MUST start only after:
- all implementation tasks are complete
- all required evidence exists
- all task gates pass

Close audit MUST NOT be used as a substitute for unfinished implementation.

### 10. Shared Ownership Serialization

Any task touching shared ownership files MUST run in serialized ownership.

This includes at minimum:
- `backend/app/modules/documents/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/tasks/service.py`
- `frontend/src/api/*.ts`
- `frontend/src/api/*.types.ts`
- router wiring files
- permission constants
- shared exports / index files

If two tasks need the same shared file:
- split a new task, OR
- serialize them into different waves

## Required Batch Lifecycle

Every future batch MUST follow this lifecycle:

1. Freeze
2. Manifest generation
3. Dirty baseline capture
4. Wave planning
5. One-slice-per-task execution
6. Evidence generation
7. Task gate pass
8. Final QA close audit
9. Batch stop

## Required Status Vocabulary

Future batches MUST use only:
- `PASS`
- `FAIL`
- `BLOCKED`
- `PARTIAL`
- `DEFERRED`

No batch may be declared complete unless:
- all in-scope implementation tasks are `PASS`
- close audit is `PASS`
- execution summary has been updated

## Immediate Enforcement

Starting with the next batch:
- do not start coding directly from the planning document
- do not reuse oversized cluster tasks
- do not skip manifest generation
- do not skip dirty baseline recording
- do not run close audit early

## Action Checklist For Next Batch

- [ ] Produce freeze output first
- [ ] Produce explicit manifest
- [ ] Record dirty baseline before Wave 1
- [ ] Keep each worker on one slice only
- [ ] Generate artifacts before claiming `PASS`
- [ ] Run task gate per task
- [ ] Run close audit only after implementation tasks pass
- [ ] Stop after the batch close line

## Governing Rule

This document is now normative for subsequent batch execution.

If a later execution prompt conflicts with this document, the execution prompt must be corrected before work starts.
