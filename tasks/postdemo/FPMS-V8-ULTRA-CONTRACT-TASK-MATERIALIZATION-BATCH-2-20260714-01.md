# FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `M2-9 — serialized delta-2 contract materialization controller`
Executor role: Ultra Architect / materialization controller

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: validation fails if a parent hash/count changes, any of the 24
  materialized contracts or 25 manifest rows drifts, either external prerequisite or any
  override is omitted, the effective graph is not exactly 288 resolved acyclic nodes, or
  Foundation/Full/Release can bypass the additive gates.
- GREEN expectation: immutable `283/197/86` parents and accepted delta-1 remain
  byte-identical while a deterministic delta-2 overlay validates 22 overrides, two
  external prerequisites, 25 unique manifest rows, effective Foundation count `202`, and
  all dependency, serialization and close gates.

## Exact Closure Slice

Audit and materialize exactly the approved 25-row Ultra delta-2 contract batch by creating
one explicit contract-materialization manifest, one deterministic additive overlay and one
fail-closed validator for task shape, hashes, dependency closure, shared ownership,
effective Foundation, Full activation and final Release reachability without rewriting the
immutable V8 baseline or accepted delta-1.

## Explicit Non-Closure

No product source, test, schema, migration, seed, API, UI or runtime behavior is
implemented; no rows 01–24, `AGENTS.md`, immutable baseline, delta-1 manifest/overlay,
customer decision or release gate is modified or executed. This task does not authorize
one worker to implement multiple High tasks and does not mark any product task PASS.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01` — PASS.
- `FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01` — PASS.
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01` — PASS and read-only.
- Rows 01–24 of
  `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-2-20260714-01.md` must exist,
  pass atomic task-shape checks and remain
  `READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED`.

Shared ownership is serialized in M2-9: this controller is the sole writer of its task,
delta-2 manifest and artifact family. No product or SQLite verification runs here.

## Remaining Follow-Up Task IDs

- `FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01`
- `FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- The individually owned High implementation tasks in the effective Foundation overlay.

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-2-20260714-01.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01/**`

No row 01–24 task, product file, immutable parent, accepted delta-1 or shared ownership
file is authorized. Preserve and subtract the captured dirty baseline.

## Runtime Contracts

- The overlay is deterministic JSON and contains no `generated_at` or clock value.
- All four immutable baseline JSON files, the accepted delta-1 manifest and accepted
  delta-1 overlay retain their captured SHA-256 hashes.
- Effective product graph is exactly `283 + 3 + 2 = 288`; controller tasks remain audit
  gates outside that graph.
- Effective Foundation is the immutable 197 task IDs plus all five external prerequisites,
  exactly 202 unique IDs; the immutable manifest itself remains 197 rows.
- Dependency and serialization validation fails closed on any missing ID, cycle, hash
  drift, shared-owner overlap, 29-entry composite-identity loss or close bypass.
- Foundation requires both controllers and all five external task gates. Full activation
  requires 7 `GLOBAL` plus 22 form-scoped requests. Final close preserves the existing
  release gate as the last manifest-defined gate.
- Two independent read-only reviewers are required; the controller cannot approve itself.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01.md`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01/analysis/validate_delta_overlay.py`
- `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01.md tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-2-20260714-01.md artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Product pytest, Ruff, migration execution, frontend build/typecheck, Playwright, release
gate and repo-wide gates are prohibited in this materialization task.

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01/**`

## Done Definition

- Exactly 25 unique manifest rows and 24 High-ready task contracts validate.
- Exactly 22 contract overrides and two external prerequisites carry current task hashes,
  exact closures, dependencies and allowlists.
- Parent hashes/counts remain unchanged; effective graph is 288 resolved acyclic nodes.
- Shared source, frontend, Alembic and SQLite owners are serialized; the 29 composite gate
  entries survive backend, frontend, fixture and E2E chains without code-only dedup.
- Effective Foundation is 202 while its immutable manifest remains 197; Full and final
  close retain both overlays/controllers, all five external tasks and the release gate.
- Both independent reviews approve with no blocking finding.
- Required dirty-baseline, results, summary and scoped-diff evidence exists; scoped task
  gate and atomic evidence validation pass.
- No product, row 01–24, immutable parent, accepted delta-1 or `AGENTS.md` file changed.
