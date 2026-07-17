# FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `M6 — serialized contract materialization controller`
Executor role: Ultra Architect / materialization controller

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: validation fails if any baseline hash/count changes, any of the fifteen
  High-ready contracts or sixteen manifest rows drifts, an external prerequisite or
  contract override is omitted, the effective graph cycles, or final-close serialization
  can bypass the three external tasks.
- GREEN expectation: the immutable `283/197/86` baseline remains byte-identical and one
  deterministic additive overlay validates exactly twelve overrides, three external
  prerequisites, sixteen unique manifest rows, effective Foundation count `200`, and all
  required dependency/serialization/final-close gates.

## Exact Closure Slice

Audit and materialize exactly the approved sixteen-row Ultra contract batch by creating
one explicit contract-materialization manifest, one deterministic additive delta overlay,
and one fail-closed validator for task shape, hashes, dependency closure, serialization
and Foundation final-close reachability without rewriting the immutable V8 baseline.

## Explicit Non-Closure

No product source, test, schema, migration, seed, API, UI or runtime behavior is
implemented; no rows 01–15, AGENTS.md, baseline materialization JSON, historical
materializer, immutable 197-row Foundation manifest, customer decision or release gate is
modified or executed. This task does not authorize one worker to implement multiple High
tasks and does not mark any product task PASS.

## Dependencies

All fifteen materialization rows below must exist, pass atomic task-shape checks, and remain
`READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-13 / NOT STARTED` before this controller
can complete:

1. `tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md`
2. `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md`
3. `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md`
4. `tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md`
5. `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md`
6. `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md`
7. `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md`
8. `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md`
9. `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01.md`
10. `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md`
11. `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
12. `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01.md`
13. `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md`
14. `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01.md`
15. `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md`

Shared ownership is serialized in M6: this controller is the sole writer of the delta
manifest and overlay family. No product/SQLite verification runs in this task.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- The individual High implementation task IDs in the effective Foundation execution
  overlay; each remains independently owned and gated.

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-20260713-01.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01/**`

No other task, manifest, source, test, schema, migration, UI, baseline materialization or
shared ownership file is authorized. Preserve the captured dirty baseline.

## Runtime Contracts

- The overlay is deterministic JSON and contains no `generated_at` or other clock value.
- Baseline files are read-only and must retain their captured SHA-256 hashes and
  `283/197/86` counts.
- Effective Foundation closure is the immutable original 197 task IDs plus exactly three
  external prerequisites; the immutable manifest itself remains 197 rows.
- Dependency and serialization validation fails closed; no missing ID, cycle, hash drift,
  shared-file overlap or final-close bypass is accepted.
- Two independent reviewers are required; the implementing controller cannot approve its
  own task.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01.md`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01/analysis/validate_delta_overlay.py`
- `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01.md tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-20260713-01.md artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Product tests, Ruff, migration execution, frontend build, Playwright, release gate and
repo-wide gates are prohibited in this materialization task.

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01/**`

## Done Definition

- Exactly sixteen unique manifest rows and fifteen High-ready task contracts validate.
- Exactly twelve contract overrides and three external prerequisites carry current task
  hashes, exact dependencies, closures and allowlists.
- Baseline hashes/counts remain unchanged; effective dependency graph is acyclic.
- The full effective `backend/app/modules/fees/official_rate_book.py` chain preserves all
  eleven baseline owners in their relative order and inserts Provider exactly after
  activation; snapshot precedes grant adapter and annuity, all Alembic and SQLite-writing
  verification remains serialized, and Provider precedes HTTP, legacy migration and close.
- Foundation close contains the controller, validator and all three external task gates.
- Both independent reviews approve with no blocking finding.
- Required dirty-baseline, results, summary and scoped-diff evidence exists; scoped task
  gate and atomic evidence validation pass.
- No product or immutable baseline file changed and no product/release verification ran.
