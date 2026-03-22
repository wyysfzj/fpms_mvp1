# Batch 3 Execution Runbook (2026-03-16)

## Purpose

This runbook defines the mandatory execution process for `Batch 3` and any later batch that reuses the same operating model.

It is designed to prevent the execution failures seen in `Batch 1` and `Batch 2`.

This runbook is binding together with:
- `AGENTS.md`
- `docs/Batch_Execution_Improvement_Plan_20260316.md`
- the batch-specific planning document

## Iron Rules

1. No implementation may begin before freeze output exists.
2. No implementation may begin before an explicit manifest exists.
3. One spawned worker = one exact atomic task file path.
4. One worker = one closure slice only.
5. Shared ownership files must be serialized.
6. Dirty worktree baseline must be recorded before each wave.
7. No task may claim `PASS` without artifacts.
8. No batch may claim complete without QA close audit `PASS`.

## Step 0: Execution Freeze

`explorer` MUST first output:
- covered `Partially Implemented` items
- excluded items
- document generation exclusion confirmation
- shared ownership files
- forbidden modules / forbidden files
- candidate tasks for this batch
- candidate `Deferred` / `Blocked` items

If this step is incomplete, stop.

## Step 1: Explicit Manifest

`default / Team Lead` MUST produce a manifest before implementation.

Every manifest row MUST contain:
- `task_id`
- exact task file path
- role
- allowlist
- required verification
- dependency
- shared ownership flag
- done definition

If one row cannot be defined cleanly, that work must remain `Deferred` or `Blocked`.

## Step 2: Dirty Baseline

Before Wave 1, `monitor` MUST record:
- allowlist baseline diff
- allowlist-external dirty files
- known contamination risks

This baseline must be referenced during task acceptance.

## Step 3: Wave Planning

Waves may be parallel only if:
- owned files do not overlap
- no shared ownership file is touched by more than one task
- no SQLite write-test conflict exists

If any of those conditions fail, serialize the wave.

## Step 4: Worker Execution

Each worker MUST follow this exact sequence:

1. confirm allowlist
2. add failing test or failing proof
3. implement minimum fix
4. run minimum verification
5. generate evidence
6. stop and report

Workers MUST NOT continue into a second slice within the same task.

## Step 5: Evidence Contract

Each `PASS` task MUST contain:
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/git/diff.patch`

Frontend tasks MUST encode:
- lint as `step=lint`
- typecheck as `step=test`

until `scripts/task_validate.sh` is changed.

## Step 6: Task Gate

After evidence exists, run:
- `./scripts/task_validate.sh <TASK-ID>`

If it fails:
- task cannot be marked `PASS`
- fix evidence or verification before proceeding

## Step 7: Idle Triage

If a worker appears stalled, do not immediately call it idle.

The lead or monitor must check:
- diff growth
- artifact timestamps
- running verification activity
- whether only evidence closure is missing

Only after no movement across those signals should the worker be considered idle.

## Step 8: Final QA Close Audit

Final QA close audit may start only when:
- all implementation tasks are `PASS`
- all gates are `PASS`
- all artifacts exist

The QA task must verify:
- scope compliance
- no Batch spillover
- no `document generation` implementation
- no unapproved shared-file contamination
- all in-scope `Partially Implemented` items are actually covered

## Step 9: Batch Stop Line

After QA close audit:
- update execution summary
- declare batch outcome
- stop

Do not automatically begin the next batch.

## Required Output Per Task

Every completed task must report:
- task id
- task file path
- owned files
- covered items
- verification run
- evidence path
- final status

## Required Output For Batch Close

Batch close output must report:
- covered items
- task mapping
- wave order
- shared-file serialization decisions
- blocked/deferred items
- final stop line

## Default Stop Conditions

Stop immediately if:
- no manifest exists
- allowlist is ambiguous
- a shared ownership collision is detected
- schema change is required but not approved
- task gate cannot pass
- scope expands into another batch

## Batch 3 Start Checklist

- [ ] freeze complete
- [ ] manifest complete
- [ ] dirty baseline recorded
- [ ] waves defined
- [ ] ownership conflicts resolved
- [ ] verification commands defined
- [ ] evidence convention confirmed
- [ ] QA close task reserved for final wave

## Governing Statement

Starting with `Batch 3`, execution MUST follow this runbook.

If a future prompt asks to skip these steps, the prompt must be corrected before implementation begins.
