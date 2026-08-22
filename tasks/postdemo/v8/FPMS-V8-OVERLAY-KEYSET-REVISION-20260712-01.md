# FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `264`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `795`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

`sequence > after` and `<= as_of_revision`, ascending `limit+1`, stable next cursor; 121 rows across three pages without loss/duplication.

## Ultra Contract Freeze — 2026-07-14

This section is authoritative for High implementation. It materializes the
delta-2 cursor invariant without changing this task's keyset-only closure or
reopening the accepted decision-gate join.

### Frozen milestone keyset and cursor semantics

- On the first invocation, `after_sequence=0` and `as_of_revision=None`. The
  service reads and freezes the lifecycle revision as `R`; every later page
  reuses that exact `R` as `as_of_revision`.
- Keyset filtering and `limit + 1` apply only to `milestones`: select
  `sequence > after_sequence AND sequence <= R`, order by `sequence`
  ascending, fetch at most `limit + 1`, and return at most `limit` rows.
- `has_more` is `True` exactly when the bounded query produced the extra row.
  When `has_more=True`, `next_cursor` is the last returned milestone's
  `sequence`; otherwise `next_cursor=None`. The extra row is never returned.
- Rows appended with `sequence > R` after page one are excluded from every
  page in that traversal. Across the frozen 121-row fixture, three pages
  return every milestone exactly once, in ascending order, with no gap or
  duplicate.

### Frozen decision-gate snapshot preservation

- Milestone keyset filtering, `limit`, `after_sequence`, `has_more` and
  `next_cursor` MUST NOT paginate, truncate or otherwise transform
  `decision_gates`. Every page returns the complete ordered decision-gate
  snapshot unchanged.
- The snapshot contains exactly 29 entries with composite identity
  `(gate_code, requested_scope_key)`: seven non-legacy gate codes in the
  existing `DecisionGateCode` order, each requested as `case:<case_id>`, then
  `DG-LEGACY-FORM-CLASS` entries requested as `form-001` through `form-022` in
  ascending order.
- One overlay invocation captures exactly one timezone-naive UTC
  `generated_at` and supplies that same value as `as_of` to all 29 resolver
  calls in the same caller transaction. Pagination MUST NOT introduce a
  per-entry clock read or a first-page-only gate snapshot.
- The ordered tuple MUST NOT be dropped on later pages, merged, or deduplicated
  by `gate_code`; the legacy gate code intentionally repeats 22 times.
- `requested_scope_key` and `resolved_scope_key` provenance is preserved
  exactly. In particular, legacy resolution always requests the individual
  `form-NNN`; a valid fallback may return `resolved_scope_key=ALL-22` while
  preserving `requested_scope_key=form-NNN`, the extracted form value and its
  source. `requested_scope_key=ALL-22` is never emitted or sent to the read
  service.

### Frozen RED / GREEN matrix

`backend/tests/test_v8_lifecycle_overlay_pagination.py` MUST prove:

1. A frozen 121-milestone revision traverses three ascending pages with no
   loss or duplication; later `sequence > R` rows remain excluded.
2. `has_more` and `next_cursor` follow the exact extra-row rule on intermediate,
   final and empty pages.
3. Every page contains the same complete 29-entry ordered composite-identity
   set: seven `case:<case_id>` entries plus `form-001..form-022`; no page is
   first-page-only, truncated, merged or deduplicated by gate code.
4. One invocation timestamp is used as both `generated_at` and all 29 resolver
   `as_of` values, with unchanged requested/resolved scope provenance.
5. No resolver command or returned entry has `requested_scope_key=ALL-22`;
   `resolved_scope_key=ALL-22` remains valid only as preserved fallback
   provenance for an individually requested form.

The RED is missing milestone-only keyset/revision behavior or any page-scoped
loss of the inherited decision-gate snapshot. GREEN does not authorize a new
decision-gate resolver, endpoint, UI, schema or second dataset.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): decision-gate join

### Shared ownership serialization

- `backend/app/modules/cases/lifecycle_overlay_service.py` order key `5`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01.md`
- `backend/app/modules/cases/lifecycle_overlay_service.py`
- `backend/tests/test_v8_lifecycle_overlay_pagination.py`
- `artifacts/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_pagination.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_pagination.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_pagination.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_pagination.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_pagination.py`
- `git diff --check -- backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_lifecycle_overlay_pagination.py tasks/postdemo/v8/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01` pass. Only then may this task be reported PASS.
