# FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `U3-C1 — RAW rejected/current-attempt evidence authority correction`
Executor role: Ultra Evidence Governance Architect
Risk tier: `HIGH` — document/evidence provenance and lineage authority

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md`
- `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md`
- `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01.md`
- `tasks/postdemo/v8/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/historical/raw_task_rejection/inventory.json`

## Story Shape Classification

- `shared_file_density`: low — this task owns one task file and its own evidence family.
- `prereq_dependency_density`: high — future live-family reuse is gated by two
  independent product guard tasks and their evidence/task gates.
- `be_fe_coupling`: none — no product or UI contract changes.
- `evidence_cost`: high — this closure governs rejected/current-attempt evidence identity
  and therefore requires deterministic provenance checks and independent review.
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-DOC / TC-QA`

- TC-DOC RED expectation: the approved delta-3 statement that old task evidence is
  read-only conflicts with the same-ID RAW successor's obligation to generate fresh
  standard evidence in its live artifact family; no authoritative rejected/current
  attempt boundary resolves which bytes may be trusted.
- TC-DOC GREEN expectation: one additive, independently reviewed execution contract
  makes the controller-owned inventory/archive the immutable rejected-attempt authority
  and defines the exact conditions under which the same-ID live family becomes a fresh
  current-attempt evidence workspace.
- TC-QA RED expectation: deterministic validation rejects a missing or changed inventory,
  a hash other than the frozen SHA-256, a count other than 29, guard bypass, reuse of a
  rejected review/result, archive mutation authority, or product-graph/count drift.
- TC-QA GREEN expectation: the frozen inventory/hash/count, two-guard gate, fresh
  current-attempt requirements, archive immutability, attempt labels and unchanged
  290/204/86 counts are all explicit and mechanically verifiable.

## Authority and Precedence

This is a narrow additive successor contract for RAW evidence-lineage handling. Once this
task is independently approved and `PASS`, it controls only the operational conflict
between line 47 of the approved delta-3 specification (old task evidence and PASS history
remain read-only) and the same-ID RAW H3-3 successor's requirement to produce truthful
new evidence. It does not rewrite the delta-3 specification or any prior task/evidence.

The phrase "old task evidence remains read-only" is satisfied by the controller-owned
immutable rejected-attempt snapshot below. It does not permanently reserve the same task
ID's live artifact namespace against a later, independently gated current attempt.

## Exact Closure Slice

Freeze exactly one auditable evidence-authority rule: the controller-owned RAW rejection
snapshot is the sole immutable authority for the rejected attempt, while the same-ID RAW
successor may create fresh current-attempt standard evidence in its live family only
after both delta-3 guard tasks are `PASS`, without changing product closure or history.

## Frozen Rejected-Attempt Authority

- Authoritative inventory:
  `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/historical/raw_task_rejection/inventory.json`
- Inventory SHA-256:
  `b192e6efe85806dd94ed3cf96efe1579587174256fb2199d6751eaf0bf38ec13`
- Inventory `file_count`: `29`; the `files` array must also contain exactly 29 unique
  `source_path` and 29 unique `archive_path` entries.
- The inventory's `archive_family` and every listed `archive_path` identify the frozen
  rejected-attempt bytes under the controller artifact family.
- Neither this task nor a future same-ID RAW executor may delete, replace, edit, relabel
  or regenerate the inventory or any archived rejected-attempt file.
- The controller snapshot, not a same-named file still present in the live RAW family, is
  the historical authority for the rejected attempt.

## Frozen Current-Attempt Contract

### Before both guards pass

The live family
`artifacts/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01/**` is not reusable as
current-attempt evidence. Its existing root summary, review, task metadata, commands,
results, outputs and diff cannot satisfy a dependency, review, evidence or PASS gate.
No rejected-attempt success record or independent-review verdict may be carried forward.

The two mandatory guards are:

1. `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
2. `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`

Both tasks must have truthful `PASS` task status, required standard evidence, repository
task-gate success and atomic-evidence validation before H3-3 initializes a new attempt.
Missing, partial, failed, blocked or merely materialized guard state fails closed.

### After both guards pass

The same-ID RAW successor may reinitialize the live family as a current-attempt evidence
workspace and generate its standard evidence. The current attempt must be truthful and
self-contained:

- `task.json` describes the current initialization, allowlist and dirty baseline;
- `commands.jsonl` and `results.jsonl` contain current-attempt command/result records,
  not appended or copied rejected-attempt records;
- `git/diff.patch` is the current baseline-subtracted scoped diff;
- `summary.md` reports only the current task outcome while linking the frozen inventory,
  naming the rejected attempt as rejected, and clearly separating it from the current
  attempt;
- `review/independent_review.md` is a new independent review of the current attempt's
  scoped diff and evidence, links the frozen inventory, and explicitly distinguishes the
  rejected attempt from the reviewed current attempt;
- required baseline files, outputs and other standard evidence are generated from the
  current execution and may not be satisfied by copying the rejected snapshot.

The live family is a working namespace, not a second historical authority. Reinitializing
or replacing stale live evidence after both guards pass does not alter history because
the exact rejected bytes remain preserved by the immutable controller snapshot.

## Invariants Preserved

- The RAW product task ID remains
  `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`.
- Its enum-only product closure, source/test allowlist, H3-3 position, P1/P2 prerequisites,
  RED/GREEN requirements, guard regressions and follow-up adapters remain unchanged.
- The effective product graph remains exactly 290 nodes; Foundation remains exactly 204
  product tasks; deferred scope remains exactly 86 product tasks.
- This governance task is audit-only and is not a product graph node or Foundation task.
- No product, tool, parent spec, parent plan, manifest, overlay, task, graph, count,
  customer decision, release state or controller archive is changed by this closure.

## TC-DOC / QA Acceptance Cases

- `TC-DOC-01`: cite the exact delta-3 read-only statement and resolve it additively
  without editing the approved spec or prior history.
- `TC-DOC-02`: name the controller inventory as the sole rejected-attempt authority and
  freeze its exact SHA-256 and 29-file cardinality.
- `TC-DOC-03`: state that pre-guard live-family bytes cannot satisfy any current evidence,
  review, dependency or PASS gate.
- `TC-DOC-04`: authorize same-ID live-family current evidence only after both named guards
  and their task/evidence gates are `PASS`.
- `TC-DOC-05`: require new summary and independent review to link the inventory and label
  rejected and current attempts separately.
- `QA-01`: validate inventory SHA-256, `file_count`, array length, uniqueness and archive
  path containment.
- `QA-02`: validate archive immutability language and absence of any controller-archive
  write authorization.
- `QA-03`: validate current `task.json`, commands, results, diff, summary and review are
  current-attempt records and rejected records cannot be reused.
- `QA-04`: validate both guard IDs and fail-closed prerequisite wording.
- `QA-05`: validate unchanged RAW task ID/closure boundary and exact 290/204/86 counts.
- `QA-06`: validate the task/artifact-only allowlist against the captured dirty baseline.

## Explicit Non-Closure

No product source, test, enum, service, API, UI, schema, migration, seed, repository tool,
external skill, `AGENTS.md`, parent spec/plan/manifest/overlay, product task, product graph,
Foundation/Full/final/release contract, customer decision, controller archive, old PASS
history or live RAW evidence is modified. This task does not execute either guard or RAW,
does not mark them `PASS`, does not run product tests, and does not approve itself.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-3-20260714-01` — approved design parent.
- The frozen controller inventory must exist at the exact path, SHA-256 and 29-file
  cardinality before this contract can be independently approved.

The two product guards are not prerequisites for this governance task itself; they are
mandatory fail-closed prerequisites for future reuse of the same-ID RAW live family.

## Remaining Follow-Up Task IDs

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01.md`
- `artifacts/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01/**`

No other file is authorized. All referenced product, task, spec, manifest, overlay,
controller and archive paths are read-only. Preserve and subtract the captured dirty
baseline.

## Verification Commands

- Task shape: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01.md`
- Contract/inventory QA: `python3 artifacts/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01/analysis/validate_contract.py`
- Scope/baseline QA: `python3 artifacts/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01/analysis/validate_scope.py`
- Scoped patch builder: `python3 artifacts/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01/analysis/build_scoped_diff.py`
- Scoped whitespace check: `git diff --check -- tasks/postdemo/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01.md artifacts/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01`
- Independent review: a reviewer other than this task's executor must write
  `artifacts/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01/review/independent_review.md`
  with an explicit per-task verdict over the current scoped diff and QA evidence.
- Task gate, after independent approval: `./scripts/task_validate.sh FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01`
- Atomic evidence validation, after independent approval: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Product pytest, Ruff, migrations, frontend checks, Playwright, full-repo checks and the
release gate are prohibited. Expected HTTP status codes: `None` (governance-only task).

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01/**`
- Required final PASS evidence: `results.jsonl`, `summary.md`, `git/diff.patch`, the dirty
  baseline artifacts, independent review and successful task/atomic evidence gates.

## Done Definition

The inventory exists with the exact frozen SHA-256 and 29 unique files; the rejected and
current attempts have one unambiguous authority each; live evidence is fail-closed until
both guards and their gates pass; current evidence cannot reuse rejected results/review;
new summary/review link the inventory and distinguish both attempts; RAW product closure,
task ID, graph 290, Foundation 204 and deferred 86 remain unchanged; scope and evidence
checks pass; an independent reviewer approves this exact contract; task and atomic gates
pass. Only then may this governance task be marked `PASS`.
