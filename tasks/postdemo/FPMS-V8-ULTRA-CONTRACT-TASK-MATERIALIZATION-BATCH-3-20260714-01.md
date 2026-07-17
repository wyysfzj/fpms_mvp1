# FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01

Status: PASS / ULTRA CONTROLLER CLOSED 2026-07-14 / HIGH NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `M3-6 — serialized delta-3 materialization controller`
Executor role: Ultra Architect / materialization controller

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01.md`
- `tasks/postdemo/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: deterministic validation fails if any parent byte/hash, historical
  task trust anchor, row contract, dependency, allowlist, product count, shared-owner
  order, common-manifest rule or close gate is missing or changed.
- GREEN expectation: one cumulative overlay validates exactly 15 manifest rows, 14
  materialized contracts, a closed acyclic 290-node product graph, 204 effective
  Foundation product tasks, two audit-only governance tasks and the unchanged final
  release-gate position.

## Exact Closure Slice

Materialize and independently audit exactly the approved delta-3 supplemental
contract/execution manifest, fourteen High-ready task contracts and one deterministic
cumulative overlay without implementing any row's product or repository-tool behavior.

## Explicit Non-Closure

No product source, test, schema, migration, seed, API, UI or repository-tool behavior is
implemented; no parent spec/plan/manifest/overlay/evidence, external skill or `AGENTS.md`
is modified; no customer policy is chosen; no product task is marked PASS; no product
pytest, repo-wide Ruff, frontend build, Playwright or release gate is run. Materialization
does not authorize one agent to implement more than one task file.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01` — PASS with two independent
  approvals after tooling remediation.
- Delta-1 and delta-2 specs, manifests, overlays and immutable 283/197/86 baseline remain
  read-only historical parents.
- Rows 01–14 of the supplemental manifest must be independently materialized before this
  controller may build/finalize the cumulative overlay.
- `FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01` — independently approved
  `PASS`; freezes the controller-owned 29-file rejected-attempt snapshot as historical
  authority and permits same-ID live RAW evidence reuse only after P1/P2 PASS.

Shared ownership is serialized: this controller alone owns its task, the delta-3
manifest and its artifact family. It never edits row 01–14 task files.

## Remaining Follow-Up Task IDs

- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`
- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`
- The dependency-ready High tasks in the cumulative Foundation graph.

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/**`

No row 01–14 task, product, test, script, parent or shared ownership file is authorized.
Preserve and subtract the captured dirty baseline.

## Runtime Contracts

- Manifest has exactly 15 unique rows and one exact task-file owner per row.
- Controller PASS gates all High rows; the user must manually switch to High before
  implementation.
- G1 is H3-0, G2 is H3-1, P1/P2 share H3-2 and this manifest is their common authoritative
  peer manifest, RAW is H3-3, and remaining rows return to the dependency scheduler.
- Product graph is exactly 290; effective Foundation is exactly 204; deferred remains 86.
  G1/G2 and all three controllers remain audit-only outside product counts.
- Historical task normalization first proves the latest parent overlay's exact
  `task_sha256`; RAW uses only the frozen blocked-section exception. Unknown non-Status
  drift fails closed.
- The audit-only evidence-lineage correction and its task/review/evidence hashes validate
  before this controller. The cumulative validator trusts the immutable rejection archive,
  never mutable future same-ID live RAW evidence.
- `GLOBAL_SQLITE_SERIAL_QUEUE` remains one writer. Shared source and verification owners
  are serialized. Final release gate remains last and is not run here.
- Two independent read-only reviewers are required; the controller cannot approve itself.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
- `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (contract materialization only).

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/**`

## Done Definition

- Exactly 15 unique manifest rows and 14 task contracts validate with one closure,
  non-closure, allowlist, dependency set, runbook and High evidence command each.
- Immutable parent bytes and latest-overlay task hashes validate before Status
  normalization; RAW rejected history is preserved and explicitly re-frozen.
- The independently approved RAW evidence-lineage correction and immutable 29-file
  rejection inventory validate without becoming a product node or Foundation task.
- Effective graph is 290/closed/acyclic; Foundation is 204 unique product IDs; governance
  remains outside product counts.
- G1→G2→P1/P2→RAW, shared source, SQLite and Foundation→Full→ledger→final→release order
  cannot be bypassed.
- Both independent reviews approve; required dirty-baseline, results, summary and scoped
  diff evidence exists; task and atomic evidence gates pass.
- No product/tool implementation, row 01–14, parent, `AGENTS.md` or release state changed.
