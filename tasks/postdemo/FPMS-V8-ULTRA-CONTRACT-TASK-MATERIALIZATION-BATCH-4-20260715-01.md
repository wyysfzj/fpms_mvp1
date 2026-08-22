# FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01

Status: PASS / ULTRA CONTROLLER CLOSED 2026-07-16 / READY FOR HIGH / PRODUCT NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `U4-2 — serialized Delta-4 contract materialization controller`
Executor role: Ultra Architect / materialization controller

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: deterministic validation rejects any missing/duplicate row, task-path
  drift, non-frozen closure, allowlist/dependency conflict, parent/hash drift, graph/count
  error, migration branch, SQLite overlap, self-approval or premature release gate.
- GREEN expectation: the exact 34-row manifest, 33 row contracts and cumulative Delta-4
  overlay validate 302 product nodes, 216 Foundation nodes, 86 deferred nodes, zero cycle
  and the unchanged final release-gate position.

## Exact Closure Slice

Materialize and independently audit exactly the approved Delta-4 supplemental manifest:
twelve new High-ready Foundation task contracts, seventeen existing task re-freezes or
recovery contracts, four close-propagation contracts and one deterministic controller
overlay, without implementing any product behavior.

## Explicit Non-Closure

No product source, product test, migration, seed, API, UI, repository-tool behavior,
customer decision or rate activation is implemented; no immutable parent, `AGENTS.md`,
external skill or release gate is modified or run; no row task is marked product PASS;
no commit, push, reset, clean, stash or discard. This controller never edits row 01–33
task files and cannot approve itself.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-4-20260715-01` — R3 independently approved and
  evidence-gated PASS; frozen spec SHA-256
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`.
- Delta-1/2/3 specs, manifests, overlays and normalized task hashes remain immutable
  historical parents.
- Rows 01–33 must be materialized by one exact task-file owner per row before controller
  overlay/reviews/gates close row 34.

Shared ownership is serialized: this controller alone owns its task, the Delta-4 batch
manifest and its artifact family. It never edits a row 01–33 task file.

## Remaining Follow-Up Task IDs

- The dependency-ready High tasks selected by the validated cumulative Delta-4 overlay.

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/**`

No row 01–33 task, product, test, script, parent or shared ownership file is authorized.
Preserve and subtract the captured dirty baseline.

## Runtime Contracts

- Manifest has exactly 34 unique rows and one exact task-file path per row.
- Rows 01–33 remain NOT STARTED after contract materialization; row 34 closes only after
  every row-specific independent verdict and both controller review axes approve.
- Parent bytes and latest Delta-3 normalized task hashes validate before applying exact
  Delta-4 latest-wins task-contract overlays; unknown non-Status drift fails closed.
- Product graph is exactly 302; effective Foundation is exactly 216; deferred remains 86;
  all Delta controllers stay audit-only outside product counts.
- The exact migration chain is `v8_w5_pay_list_export_artifact_01` →
  `v8_d4_annuity_lineage_01` → `v8_d4_legacy_fee_provenance_01`.
- `GLOBAL_SQLITE_SERIAL_QUEUE` has maximum writer 1; all shared task files and verification
  owners are serialized; Foundation → Full → ledger → final → release remains immutable.
- Controller PASS does not authorize product implementation until the user manually routes
  execution to High.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01.md`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/analysis/validate_delta4_overlay.py`
- `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01.md tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (contract materialization only).

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/**`

## Done Definition

- Exactly 34 unique task-file rows and all 33 row contracts validate with one closure,
  non-closure, allowlist, dependency/runbook, verification and evidence contract each.
- Cumulative deterministic overlay proves immutable parents, 302/216/86, zero unresolved,
  zero cycles, exact shared/migration/SQLite/close order and no governance miscount.
- Independent reviewers issue a separate APPROVED/P0=P1=P2=0 verdict for every row and
  approve controller task-shape/scope plus graph/domain/fail-closed safety.
- Required dirty-baseline, results, summary and scoped diff evidence exists; task and atomic
  evidence gates pass; no product implementation or release action occurred.
