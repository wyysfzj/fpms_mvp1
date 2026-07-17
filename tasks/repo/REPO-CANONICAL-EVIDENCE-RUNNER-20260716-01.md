# REPO-CANONICAL-EVIDENCE-RUNNER-20260716-01

Status: PASS
Risk tier: `HIGH` — authoritative Evidence 1.1 execution tooling
Execution class: `CONTRACT FROZEN`
Chosen runbook: `P0-prereq-heavy-story`

## Authority

- User approval on 2026-07-16 of the GPT-5.6 execution-efficiency audit.
- Evidence 1.1 artifact names, dirty-baseline producer and shared semantic consumer remain
  authoritative and backward compatible.

## Exact Closure Slice

Implement one backward-compatible canonical Evidence 1.1 task runner:

1. make `scripts/evidence_run.sh` delegate command/result recording to a Python JSON encoder
   so every appended `commands.jsonl` and `results.jsonl` line is valid JSON for quotes,
   backslashes, Unicode and arbitrary argument boundaries;
2. preserve the existing `evidence_run.sh <TASK-ID> <step> <command...>` interface and the
   command's caller working directory while always locating artifacts at repository root;
3. add a canonical backend-pytest mode that runs from `backend/` with `.venv/bin/pytest`,
   supports `red` expected-nonzero and final `test`, owns and releases the SQLite lock only
   around the command, fails closed on lock contention and always releases its own lock;
4. add a canonical close mode that, after the owner has set a truthful PASS summary/task
   status and an independent reviewer has written the exact zero-finding verdict, records
   `scope`, validates and records `independent_review`, then runs and records `task_gate`
   and `atomic_evidence` in that order with required canonical steps;
5. never relabel, rewrite or delete historical results, never fabricate a successful test,
   and never mutate task/product/review/summary content during close.

## Frozen CLI

- Legacy compatibility: `./scripts/evidence_run.sh <TASK-ID> <step> <command...>`.
- Canonical backend RED: `python3 scripts/evidence_task.py backend-pytest <TASK-ID>
  --step red --expect-nonzero -- <pytest-args...>`.
- Canonical backend GREEN: `python3 scripts/evidence_task.py backend-pytest <TASK-ID>
  --step test -- <pytest-args...>`.
- Canonical close: `python3 scripts/evidence_task.py close <TASK-ID>`.
- Expected-nonzero RED returns success to the controller only when pytest actually returns
  nonzero, while `results.jsonl` retains the real nonzero process return code and explicit
  expectation metadata. Final GREEN never accepts or relabels a nonzero return code.
- The repository SQLite lock is `/tmp/fpms_v8_sqlite.lockdir`; contention fails immediately,
  and a process may remove only the lock directory it successfully created.

## Explicit Non-Closure

- No change to Evidence 1.1 artifact names, baseline subtraction, allowlist semantics,
  result/log freshness, review strength, task/atomic consumer semantics or release gate.
- No automatic task/summary/review approval, product test selection, test-fixture redesign,
  migrated-database cache, parallel SQLite policy, V8 product source or AGENTS change.
- No commit, push, reset, clean, stash or discard.

## Dependencies

- `REPO-AGENTS-56-FAST-PATH-HOTFIX-20260716-01`: must be independently accepted PASS.

## Remaining Follow-Up Task IDs

- `REPO-PYTEST-SQLITE-ISOLATION-AFTER-FOUNDATION-20260716-01` — deferred until Foundation
  close and separately materialized.

## Allowed Files

- `tasks/repo/REPO-CANONICAL-EVIDENCE-RUNNER-20260716-01.md`
- `scripts/evidence_run.sh`
- `scripts/evidence_task.py`
- `scripts/tests/test_evidence_task.py`
- `artifacts/REPO-CANONICAL-EVIDENCE-RUNNER-20260716-01/**`

No other path is authorized. Preserve and subtract the dirty baseline.

## Verification Commands

1. Initialize Evidence 1.1 exactly once through `scripts/evidence_init.sh`.
2. RED: focused unittest proves current recorder emits malformed command JSON for shell
   backslashes/quotes and lacks canonical cwd/lock/close behavior.
3. GREEN: implement the minimum runner and preserve the legacy shell interface.
4. Run only:
   - `python3 -m unittest scripts.tests.test_evidence_task -v`
   - scoped Ruff check/fix/format/check for the two allowed Python files;
   - `bash -n scripts/evidence_run.sh`;
   - `git diff --check` for the exact allowlist;
   - Evidence 1.1 scope finalization.
5. Obtain one independent HIGH evidence-tooling review with zero P0/P1/P2 findings.
6. Run the repository task gate and atomic evidence validation only after approval.

No product pytest, frontend, Playwright, migration, broad or release command is authorized.

## Evidence Path

- `artifacts/REPO-CANONICAL-EVIDENCE-RUNNER-20260716-01/**`

## Done Definition

Focused RED/GREEN proves valid JSON, caller/backend cwd, expected RED semantics, lock
contention/release and close ordering/fail-closed behavior; legacy CLI compatibility remains;
scope, evidence, independent review and both final gates pass.
