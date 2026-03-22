# Batch 3 Execution Runbook v2 (2026-03-18)

## Purpose

This runbook supersedes the weaker operational parts of:
- `tasks/postenhancement/BATCH3_EXECUTION_RUNBOOK_20260316.md`

It keeps the same freeze / manifest / baseline / gate structure, but hardens:
- exact closure slice definition
- explicit non-closure statements
- QA ledger requirements
- takeover discipline

This v2 runbook should be reused for `Batch 4+` unless a stricter batch-specific runbook replaces it.

Binding documents:
- `AGENTS.md`
- `docs/Batch_Execution_Improvement_Plan_20260316.md`
- `docs/BATCH_EXECUTION_TASK_TEMPLATE_20260318.md`
- `docs/BATCH_EXECUTION_QA_LEDGER_TEMPLATE_20260318.md`
- `docs/BATCH_EXECUTION_TAKEOVER_RULES_20260318.md`

## Iron Rules

1. No implementation may begin before freeze output exists.
2. No implementation may begin before an explicit manifest exists.
3. One spawned worker = one exact atomic task file path.
4. One worker = one exact closure slice only.
5. Every task file must include an explicit non-closure statement.
6. Shared ownership files must be serialized.
7. Dirty worktree baseline must be recorded before each wave.
8. No task may claim `PASS` without artifacts.
9. No batch may claim complete without QA ledger + QA close audit `PASS`.
10. Takeover must follow `docs/BATCH_EXECUTION_TAKEOVER_RULES_20260318.md`.

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

Manifest rows MUST describe:
- exact closure slice
- explicit non-closure
- remaining follow-up task ids

If one row cannot be defined cleanly, that work must remain `Deferred` or `Blocked`.

## Step 2: Dirty Baseline

Before every implementation wave, `monitor` MUST record:
- `artifacts/<TASK-ID>/baseline_allowlist.diff`
- `artifacts/<TASK-ID>/baseline_external_files.txt`

These files are mandatory for any task that begins with a dirty worktree.

Acceptance must evaluate only the incremental delta created after the baseline.

## Step 3: Wave Planning

Waves may be parallel only if:
- owned files do not overlap
- no shared ownership file is touched by more than one task
- no SQLite write-test conflict exists

If any of those conditions fail, serialize the wave.

If implementation is serialized, multi-agent may still be used for:
- freeze and dependency review
- artifact/gate monitoring
- idle triage support

## Step 4: Worker Execution

Each worker MUST follow this exact sequence:

1. confirm allowlist
2. record dirty baseline artifacts
3. add failing test or failing proof
4. implement minimum fix
5. run minimum verification
6. generate evidence
7. run task gate
8. stop and report

Workers MUST NOT continue into a second closure slice within the same task.

## Step 5: Task File Discipline

Every task file used in execution MUST explicitly state:
- exact closure slice
- explicit non-closure statement
- remaining follow-up task ids

If a task file does not state these clearly, rewrite it before execution.

## Step 6: Evidence Contract

Each `PASS` task MUST contain:
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/git/diff.patch`

Frontend tasks MUST encode:
- lint as `step=lint`
- typecheck as `step=test`

until `scripts/task_validate.sh` changes.

## Step 7: Task Gate

After evidence exists, run:
- `./scripts/task_validate.sh <TASK-ID>`

If it fails:
- task cannot be marked `PASS`
- fix evidence or verification before proceeding

## Step 8: Idle Triage and Takeover

If a worker appears stalled:
- do not immediately label it idle
- apply `docs/BATCH_EXECUTION_TAKEOVER_RULES_20260318.md`

Takeover may be:
- evidence-only
- verification-only
- limited slice-completion

Takeover may NOT:
- cross into a second slice
- rewrite the task boundary silently
- substitute for splitting a needed follow-up task

## Step 9: Final QA Ledger

Before close audit, `monitor` or QA owner MUST prepare a ledger using:
- `docs/BATCH_EXECUTION_QA_LEDGER_TEMPLATE_20260318.md`

The ledger must map every in-scope `Partially Implemented` item to:
- required slices
- implemented task ids
- evidence
- residual gap
- close decision

If any in-scope item remains `partial`, `deferred`, or `blocked`, the batch cannot be declared complete.

## Step 10: Final QA Close Audit

Final QA close audit may start only when:
- all implementation tasks are `PASS`
- all gates are `PASS`
- all artifacts exist
- the QA ledger exists

The QA task must verify:
- scope compliance
- no batch spillover
- no `document generation` implementation
- no unapproved shared-file contamination
- no mismatch between task slice and batch-close claim

## Step 11: Batch Stop Line

After QA close audit:
- update execution summary
- declare batch outcome
- stop

Do not automatically begin the next batch.

## Required Output Per Task

Every completed task must report:
- task id
- task file path
- exact closure slice
- explicit non-closure
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
- QA ledger conclusion
- final stop line

## Default Stop Conditions

Stop immediately if:
- no manifest exists
- allowlist is ambiguous
- a shared ownership collision is detected
- schema change is required but not approved
- task gate cannot pass
- scope expands into another batch
- exact closure slice cannot be stated cleanly
- QA ledger shows unresolved residual gap

## Batch 4 Start Checklist

- [ ] freeze complete
- [ ] manifest complete
- [ ] every task rewritten to exact-slice format
- [ ] dirty baseline artifacts defined
- [ ] waves defined
- [ ] ownership conflicts resolved
- [ ] verification commands defined
- [ ] evidence convention confirmed
- [ ] takeover rules acknowledged
- [ ] QA ledger task reserved for final wave

## Governing Statement

Starting now, this v2 runbook should be treated as the stronger execution model.

If a later prompt asks to skip these steps, the prompt must be corrected before implementation begins.
