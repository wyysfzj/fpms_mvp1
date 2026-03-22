# Batch Execution Takeover Rules (2026-03-18)

## Purpose

These rules define how the main thread and monitor should respond when a worker appears stalled.

The goal is to avoid:
- false idle classification
- accidental scope expansion during rescue work
- redoing implementation that already exists in partial form
- closing the wrong task because the acceptance criteria were too broad

## Core Principle

Takeover is allowed only to preserve task closure discipline.

Takeover is NOT a license to silently finish a larger task than the worker was assigned.

## Idle Triage Sequence

Before calling a worker `idle` or `stalled`, check all of the following:

1. Has the allowlist diff changed recently?
2. Have artifact timestamps changed recently?
3. Is verification still running?
4. Is the task only missing evidence or task-gate closure?
5. Does the current diff already satisfy the exact closure slice?

Only if all of those are negative for a sustained interval may the worker be treated as truly stalled.

## Allowed Takeover Types

### 1. Evidence-Only Takeover

Allowed when:
- implementation appears complete
- verification has already passed
- only artifacts or gate closure are missing

Allowed actions:
- generate or repair `summary.md`
- generate or repair `results.jsonl`
- refresh `git/diff.patch`
- run `./scripts/task_validate.sh <TASK-ID>`

Forbidden:
- expanding implementation scope
- adding unrelated validation
- silently changing acceptance criteria

### 2. Verification-Only Takeover

Allowed when:
- implementation exists
- artifacts exist or can be generated
- task is blocked only by missing verification evidence

Allowed actions:
- rerun listed task verification
- rerun task gate
- record results

Forbidden:
- new feature work
- new slice work

### 3. Slice-Completion Takeover

Allowed only when:
- the worker clearly implemented part of the exact same closure slice
- the remaining work is still inside the same exact closure slice
- no new acceptance boundary is crossed

Required before doing this:
- explicitly state the remaining delta
- confirm it does not enter a second slice

If that confirmation cannot be made, do NOT take over implementation. Split a new follow-up task instead.

## Forbidden Takeover Types

Do NOT take over if doing so would:
- combine two closure slices into one task
- reinterpret a cluster-sized task as “close enough”
- expand from read/query to write-path redesign
- enter another batch
- bypass shared-file serialization

## Mandatory Takeover Report

Any takeover must record:
- original task id
- reason for takeover
- idle triage observations
- takeover type
- what was added by takeover
- what remained unchanged
- whether a new follow-up task is still required

## Split-Instead-of-Takeover Rule

If the worker’s partial result is valid but insufficient to satisfy the original task file because the task file was too broad:
- do NOT “finish it in place”
- do NOT stretch acceptance
- create a new follow-up task
- narrow the old task to the slice actually completed, if appropriate

## Required Decision Table

| Situation | Action |
|---|---|
| diff growing, artifacts changing | keep waiting |
| code done, artifacts missing | evidence-only takeover |
| code done, verification missing | verification-only takeover |
| slice partly done, same slice remains | limited slice-completion takeover |
| next remaining work is another slice | split new follow-up task |
| acceptance too broad vs actual slice | rewrite task / split task, do not stretch close |

## Enforcement

If a takeover crosses a slice boundary, the task must not be marked `PASS`.
