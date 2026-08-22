# FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `199`
Executor role: Team Lead / default

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md`
- Source catalog line: `698`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-GRANT-EVIDENCE-SOURCE[GLOBAL], DG-GRANT-MANUAL-REVIEW[GLOBAL], DG-FEE-APPLICATION-DRAFT[GLOBAL], DG-FEE-GRANT-YEAR-DRAFT[GLOBAL], DG-FEE-FUTURE-ANNUITY[GLOBAL], DG-PAYMENT-WORKBOOK[GLOBAL], DG-SERVICE-RATE-VERSION[GLOBAL], DG-LEGACY-FORM-CLASS[form-001], DG-LEGACY-FORM-CLASS[form-002], DG-LEGACY-FORM-CLASS[form-003], DG-LEGACY-FORM-CLASS[form-004], DG-LEGACY-FORM-CLASS[form-005], DG-LEGACY-FORM-CLASS[form-006], DG-LEGACY-FORM-CLASS[form-007], DG-LEGACY-FORM-CLASS[form-008], DG-LEGACY-FORM-CLASS[form-009], DG-LEGACY-FORM-CLASS[form-010], DG-LEGACY-FORM-CLASS[form-011], DG-LEGACY-FORM-CLASS[form-012], DG-LEGACY-FORM-CLASS[form-013], DG-LEGACY-FORM-CLASS[form-014], DG-LEGACY-FORM-CLASS[form-015], DG-LEGACY-FORM-CLASS[form-016], DG-LEGACY-FORM-CLASS[form-017], DG-LEGACY-FORM-CLASS[form-018], DG-LEGACY-FORM-CLASS[form-019], DG-LEGACY-FORM-CLASS[form-020], DG-LEGACY-FORM-CLASS[form-021], DG-LEGACY-FORM-CLASS[form-022]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails when any of the exact seven `GLOBAL` or 22 requested `form-NNN` identities is missing, unresolved or replaced by a requested `ALL-22` prerequisite.
- GREEN expectation: Exact QA/gate commands prove all 29 requested identities, legacy fallback provenance, supported per-form branch execution and immutable-catalog coverage.

## Exact Closure Slice

Materialize the full-program manifest only when all eight gate codes have sufficient applicable persisted confirmation coverage, including a positive or negative value for every legacy-form scope; include every catalog task exactly once, require each per-form classification task to execute its recorded branch, reuse existing foundation/lane evidence and pass the catalog coverage gate. It does not implement or approve any product task.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section is authoritative for High implementation. Complete applicable gate coverage
means exactly 29 public requested identities: the seven non-legacy gate codes below each
at exact requested scope `GLOBAL`, plus 22 separate `DG-LEGACY-FORM-CLASS` requests at
ascending exact scopes `form-001` through `form-022`.

- Every one of the seven non-legacy `GLOBAL` requests must resolve through the accepted
  decision-gate read service to a persisted, current and source-backed confirmation for
  that exact requested identity.
- Every one of the 22 legacy-form requests must independently resolve through that read
  service to exactly one supported classification: `CURRENT_OFFICIAL`, `HISTORICAL` or
  `INTERNAL_ONLY`. `CURRENT_OFFICIAL` requires its positive activation branch;
  `HISTORICAL` and `INTERNAL_ONLY` require their recorded negative reference-only branch.
- `ALL-22` is never a public requested prerequisite and is never sufficient by itself.
  It may appear only when the accepted resolver selects a valid persistence fallback for
  an exact `form-NNN` request. That result must preserve
  `requested_scope_key=form-NNN`, `resolved_scope_key=ALL-22`, the extracted supported
  classification and the selected carrier's exact source provenance.
- Finding or validating one `ALL-22` carrier does not replace the 22 public form
  resolutions. Any missing, duplicate, unresolved, unsupported or scope-mismatched one
  of the 29 requested identities keeps the full manifest absent and fails closed.
- This task reads already persisted decisions only. It does not record, confirm,
  synthesize, default or otherwise create a customer decision.
- Full activation may execute only after the effective Foundation close task
  `FPMS-V8-FOUNDATION-CLOSE-20260712-01` is PASS. That accepted close is the transitive
  prerequisite carrier for both materialization controllers and all five external-task
  gates/evidence; this task must not bypass, duplicate or absorb those external nodes.
- The resulting full manifest contains every row of the immutable 283-task catalog
  exactly once, reuses existing foundation/lane evidence and passes the catalog coverage
  gate. It does not rewrite the immutable catalog or absorb additive external tasks as
  catalog rows.

## Ultra Contract Freeze — 2026-07-14 (delta-3)

This additive section changes only the inherited close proof. The delta-2 decision-gate
contract above remains authoritative and unchanged: activation still requires the exact
seven `GLOBAL` requests plus 22 separate `form-001..form-022` requests, never a requested
`ALL-22`, and this task still reads rather than records or activates customer decisions.

- The delta-3 supplemental manifest and materialization controller are authoritative for
  this inherited override. Full activation may begin only after the effective Foundation
  close `FPMS-V8-FOUNDATION-CLOSE-20260712-01` is PASS.
- That Foundation PASS must prove exactly 204 unique product task IDs: the immutable 197
  Foundation IDs plus three delta-1, two delta-2 and two delta-3 external prerequisites,
  `197 + 3 + 2 + 2 = 204`. The immutable Foundation manifest remains 197 rows, the
  immutable catalog remains 283 rows, the effective product graph is 290 nodes and the
  deferred set remains 86.
- The same Foundation PASS must prove the task/evidence gates and independent acceptance
  for all three materialization controllers and for G1/G2. Those controllers and G1/G2
  are audit-only governance gates outside both the 204-task Foundation product count and
  the 290-node effective product graph; they must never be counted as product tasks.
- The cumulative delta-3 validator at
  `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
  is the mandatory current overlay gate. Earlier delta validators remain historical
  read-only inputs and are not sufficient for this activation.
- Full activation is a single declared lane, but its atomic evidence validation must use
  the G2 repository wrapper `scripts/atomic_evidence_validate.py`. With no declared peer,
  invoke the wrapper without `--manifest` or `--concurrent-task`; single-lane execution
  does not authorize direct use of the external helper.
- All SQLite-writing tests and shared-file verification remain serialized. This task does
  not run, move, duplicate or weaken the release gate.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`

The Foundation dependency is an execution precondition, not a catalog expansion. Its
PASS proves the cumulative effective Foundation close: 204 product tasks, all three
materialization controllers, G1/G2 and all seven external product prerequisite
task/evidence gates. The controllers and G1/G2 are audit-only and excluded from product
counts; the seven external product nodes remain outside the immutable 283-row catalog.
None is repeated as a direct full-activation dependency.

### External, gate and inherited prerequisites

Inherited audit-only Foundation gates, carried transitively rather than counted as
product tasks:

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` (`G1`)
- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` (`G2`)

Inherited external product prerequisites included in the effective 204-task Foundation
set but not in the immutable 197-row Foundation manifest or 283-row catalog:

- `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`
- `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`

The cumulative delta-3 validator named above is a read-only inherited gate. It validates
the current overlay before activation and is neither a product task nor a catalog row.

- `gate` — `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-GRANT-MANUAL-REVIEW:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-FEE-APPLICATION-DRAFT:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-FEE-FUTURE-ANNUITY:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-PAYMENT-WORKBOOK:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-SERVICE-RATE-VERSION:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-LEGACY-FORM-CLASS:form-001`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-002`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-003`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-004`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-005`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-006`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-007`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-008`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-009`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-010`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-011`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-012`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-013`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-014`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-015`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-016`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-017`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-018`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-019`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-020`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-021`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `DG-LEGACY-FORM-CLASS:form-022`: Exact public requested scope must resolve to a supported classification under the frozen legacy-form rule above.
- `gate` — `ALL_APPLICABLE_GATE_COVERAGE`: All seven exact `GLOBAL` identities and all 22 exact public requested form identities have sufficient persisted resolution coverage; gate-code-only or requested `ALL-22` coverage is insufficient.

- Approved source dependency cell (verbatim): complete applicable gate coverage; decision-gate read service; catalog coverage gate

### Shared ownership serialization

- `FULL_MANIFEST_OWNERSHIP` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-MITIGATION-20260712-01.md`
- `backend/tests/test_v8_full_manifest_activation_contract.py`
- `artifacts/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Full activation is one declared lane. Atomic evidence validation still uses
  `scripts/atomic_evidence_validate.py` without manifest or peer arguments.
- Follow the frozen Foundation-to-Full order. Full activation does not run the release gate.

## Exact QA Acceptance Matrix

`backend/tests/test_v8_full_manifest_activation_contract.py` MUST prove:

1. Activation requires exactly the seven named non-legacy gate identities at requested
   scope `GLOBAL` and 22 legacy identities at requested scopes `form-001..form-022`.
2. The accepted decision-gate read service resolves every requested identity; the task
   does not query decision rows directly, infer coverage by gate code or create decisions.
3. No prerequisite request uses `ALL-22`. A valid fallback result keeps requested
   `form-NNN`, resolved `ALL-22`, the extracted supported value and exact source
   provenance, and the resolver still completes all 22 separate form requests.
4. Each legacy request resolves one of `CURRENT_OFFICIAL`, `HISTORICAL` or
   `INTERNAL_ONLY`, and its matching per-form classification task has executed the
   corresponding positive activation or negative reference-only branch.
5. Any missing, duplicate, unresolved, unsupported or scope-mismatched requested identity
   fails closed and leaves the full manifest absent; one `ALL-22` carrier alone never
   satisfies activation.
6. Activation remains absent until the effective Foundation close has proved the
   cumulative delta-3 overlay, exactly 204 product tasks, all three audit-only controller
   gates and audit-only G1/G2 gates without counting governance as product scope.
7. The full manifest includes every immutable catalog task exactly once, permits only this
   activation row under the existing self-pending rule, reuses accepted foundation/lane
   evidence and passes `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`.
8. `FULL_MANIFEST_OWNERSHIP` remains serialized at order key `1`, and no immutable catalog
   row or additive external prerequisite is moved, duplicated or reclassified.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_full_manifest_activation_contract.py`; run it before implementation and preserve the expected failure proving missing exact 29-identity coverage, improper requested `ALL-22` sufficiency or catalog duplication.
- GREEN and scoped checks:
- `./scripts/task_validate.sh FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-FOUNDATION-CLOSE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_full_manifest_activation_contract.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_full_manifest_activation_contract.py && .venv/bin/ruff format tests/test_v8_full_manifest_activation_contract.py && .venv/bin/ruff check tests/test_v8_full_manifest_activation_contract.py`
- `git diff --check -- tasks/batches/FPMS-POSTDEMO-V8-MITIGATION-20260712-01.md backend/tests/test_v8_full_manifest_activation_contract.py artifacts/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01/** tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01`
- Evidence validation (single declared lane; no manifest or peer arguments): `python3 scripts/atomic_evidence_validate.py FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The effective Foundation close task `FPMS-V8-FOUNDATION-CLOSE-20260712-01` is PASS first,
thereby carrying exactly 204 product tasks plus PASS requirements for all three audit-only
materialization controllers, audit-only G1/G2 and all seven external-product task/evidence
gates without absorbing those nodes into the immutable catalog; the cumulative delta-3
validator passes; the exact RED is preserved; the minimum allowlisted change makes the
exact GREEN prove all 29 requested gate identities, legacy fallback provenance, supported
per-form branches and every immutable catalog task exactly once; targeted regressions
pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were
serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent
reviewer approves the exact closure and non-closure; single-lane atomic evidence validation
uses the G2 repository wrapper and `./scripts/task_validate.sh
FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01` passes. The release gate is not run by this
task. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, especially lines 919–944.
- Supplemental authority: row `31 / M4-H / FULL-ACTIVATION` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; Full activation, product work, customer decisions and release work remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` remains the latest-wins runbook for Delta-4 execution.
- This appendix is latest-wins only for effective counts, Foundation prerequisites, cumulative gates and the no-activation boundary below; every other inherited byte and the existing allowlist remain unchanged history.

### Immutable catalog and effective graph counts

- The accepted 283-row V8 product catalog remains immutable and is not regenerated, reordered, duplicated or rewritten.
- The accepted 197-row Foundation manifest remains immutable and is not expanded or rewritten.
- Delta-4 adds 12 external product nodes to the prior effective graph: effective product graph is exact `290 + 12 = 302`; effective Foundation is exact `204 + 12 = 216`; deferred remains exact `86`.
- `302` and `216` are effective product-graph counts, not catalog or manifest row counts. Delta spec/controller/review/overlay and other audit-only governance gates are excluded from both counts and must never be counted as catalog rows.
- The 12 Delta-4 product nodes, 17 re-frozen task contracts and four close overlays append authority without rewriting the immutable 283 catalog or 197 Foundation manifest.

### Exact Full start gate

- Full activation may start only after `FPMS-V8-FOUNDATION-CLOSE-20260712-01` has an effective, independently accepted PASS proving all exact 216 Foundation product nodes plus every required Delta-1/2/3/4 controller and governance gate.
- Foundation PASS must include task-local evidence, baseline-subtracted scope, independent acceptance, repository task gate and shared Evidence 1.1 atomic validation for every required node; a count, status label or manifest row alone is insufficient.
- The deterministic cumulative Delta-4 overlay must validate parent hashes, normalized task anchors, exact `302/216/86`, zero unresolved nodes, zero cycles, and exact shared-file, migration, SQLite and close order.
- The Delta-4 materialization controller and all 34 row verdicts must pass their task/evidence gates, with independent zero-finding approvals, before this Full lane is eligible to start.
- Existing customer decision gates remain additional prerequisites after effective Foundation close: all seven exact non-legacy `GLOBAL` identities and all 22 exact requested `form-001..form-022` legacy identities must resolve through the accepted read service under the inherited fail-closed matrix.
- A gate-code-only result, one requested `ALL-22`, missing/duplicate/unresolved/unsupported/scope-mismatched decision, inferred default or unapproved customer choice cannot satisfy activation. This task reads decisions; it never records, synthesizes or activates one.

### Full-lane acceptance and non-closure

- When later authorized, Full activation remains one declared serialized lane and must prove every immutable catalog task exactly once, reuse accepted Foundation/lane evidence, permit only this activation row under the inherited self-pending rule, and pass the existing catalog-manifest coverage gate.
- Keep the existing Allowed Files list exact. Do not move or reclassify an immutable catalog row, absorb an external product/governance node into the catalog, weaken a customer gate, or alter Foundation/Full ownership.
- This Delta-4 materialization performs no customer-gate resolution or activation, no Full manifest mutation, no product/test edit, no evidence initialization, no Foundation/Full close and no release execution.
- Release remains the unchanged final-close manifest-defined last step; this task never runs, moves or weakens the release gate.
- This contract-freeze turn runs only the repository atomic task check. Later PASS still requires the cumulative overlay, prerequisite task/evidence gates, scoped TDD and verification, independent approval, `./scripts/task_validate.sh`, and shared Evidence 1.1 validation named by the inherited contract.
