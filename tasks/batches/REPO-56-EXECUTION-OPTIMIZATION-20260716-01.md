# REPO 5.6 Execution Optimization Batch — 2026-07-16

Status: USER APPROVED / READY FOR SERIAL EXECUTION
Risk: `HIGH` — governance and Evidence 1.1 execution tooling
Chosen runbook: `P0-prereq-heavy-story`

## Exact Batch Closure

Execute the two approved atomic tasks below without resuming V8 product development.

| Wave | Exact task-file path | Ownership | Dependency | Shared/serialization decision |
| --- | --- | --- | --- | --- |
| G56-1 | `tasks/repo/REPO-AGENTS-56-FAST-PATH-HOTFIX-20260716-01.md` | governance | user approval | exclusive `AGENTS.md`; no other task executes until independent PASS |
| G56-2 | `tasks/repo/REPO-CANONICAL-EVIDENCE-RUNNER-20260716-01.md` | evidence tooling | G56-1 PASS | exclusive evidence runner/test files |

Each task retains its own closure, non-closure, allowlist, TDD/evidence, independent review
and gates. An implementer cannot approve its own task.

## Explicit Non-Closure

- No V8 product task, Foundation/Full/Final/release execution or Goal resumption.
- No broad `AGENTS.md` modularization or pytest/SQLite test-fixture redesign in this batch.
- No commit, push, reset, clean, stash or discard.

## Deferred Approved Follow-Ups

- `REPO-AGENTS-56-MODULARIZATION-AFTER-FOUNDATION-20260716-01`: move source inventory,
  completed transition history and legacy operational recipes into routed authoritative
  references after Foundation close.
- `REPO-PYTEST-SQLITE-ISOLATION-AFTER-FOUNDATION-20260716-01`: prove isolated SQLite test
  processes, migration-template caching and automatic FIFO execution after Foundation close.

These follow-ups are deliberately not materialized as implementation-ready tasks now; the
approved sequencing says they must not block current product development.

## Batch Done Definition

Both rows independently PASS with scoped evidence and zero-finding independent reviews.
Only then is the repository ready to resume the existing product Goal under the optimized
controller practice.
