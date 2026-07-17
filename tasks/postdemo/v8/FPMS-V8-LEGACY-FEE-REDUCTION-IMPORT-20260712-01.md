# FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `15. Migration and compatibility cutover`
Catalog ordinal: `255`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `777`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Map explicit no-reduction `0`; map `0.7/0.85` only with source/scope; never coerce missing/invalid to zero.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): validator

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01.md`
- `backend/scripts/backfill_v8_fee_reduction.py`
- `backend/tests/test_v8_legacy_fee_reduction_import.py`
- `artifacts/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_fee_reduction_import.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_fee_reduction_import.py`
- `cd backend && .venv/bin/ruff check --fix scripts/backfill_v8_fee_reduction.py tests/test_v8_legacy_fee_reduction_import.py && .venv/bin/ruff format scripts/backfill_v8_fee_reduction.py tests/test_v8_legacy_fee_reduction_import.py && .venv/bin/ruff check scripts/backfill_v8_fee_reduction.py tests/test_v8_legacy_fee_reduction_import.py`
- `git diff --check -- backend/scripts/backfill_v8_fee_reduction.py backend/tests/test_v8_legacy_fee_reduction_import.py tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 750–779, with the D4-12 provenance carrier at lines 735–748.
- Supplemental authority: row `29 / M4-H / H4-5` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work, evidence and customer migration remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact grammar, approved-manifest, provenance, plan, replay and transaction contract below; every other inherited byte and the existing allowlist remain unchanged history.

### Exact public seam, grammar and authority

- Public seam is exact `import_legacy_fee_reductions(*, transaction: Session, manifest: LegacyFeeReductionMigrationManifest, dry_run: bool, expected_plan_sha256: str | None = None) -> LegacyFeeReductionImportResult`.
- Accept only byte-exact strings `"0"`, `"0.7"`, `"0.85"`; never trim, parse/reformat a number, accept an alias, coerce invalid/missing input, or infer that missing means zero.
- The externally approved manifest supplies its exact version/hash, accountable actor and naive confirmation time, case ID, exact legacy value, source reference/version/snapshot hash, and nullable approval ID. Missing, unapproved, malformed or contradictory authority fails closed.
- D4-12 `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01` must have independently accepted PASS before High starts this importer.
- Provenance stores the exact approved legacy value and manifest/source/actor/time truth. Its `approval_id` is null for `"0"` and non-null for `"0.7"`/`"0.85"`; identity is exact `(case_id, manifest_hash)` and creation audit is immutable.

### Deterministic dry-run and apply plan

- Process rows in deterministic case-ID order. Dry-run performs zero writes and emits the exact input hash, deterministic plan hash and per-row classification.
- Apply requires non-null `expected_plan_sha256` exactly equal to the preceding approved dry-run plan hash; changed input, manifest, ordering, classification or plan fails closed before any write.
- Result exposes exact counts `scanned`, `explicit-zero`, `reused-70`, `reused-85`, `unchanged`, `invalid`, `missing-approval`, `ambiguous-approval`, `planned-writes`, plus input, plan and output hashes.
- Counts, classifications and hashes are deterministic for identical input and approved manifest; do not depend on database row order, wall clock, generated actor/time or permissive parsing.

### Exact provenance, approval and mutation rules

- `"0"` may create or reuse only the exact confirmed provenance row named by the approved manifest and never creates or associates a fee-reduction approval.
- `"0.7"` or `"0.85"` requires exactly one pre-existing confirmed approval matching exact ratio, case, applicant scope, fee scope, year scope, effective interval, evidence scope and content hash, plus the manifest approval ID. Missing or multiple matches fail closed.
- The importer never creates, approves, edits, supersedes or guesses an approval and never upgrades source/customer data into legal authority.
- For a passing row, update only the legacy case fee-reduction field to its exact canonical string and create or reuse the matching immutable provenance; no adjacent case, fee, approval or evidence field changes.

### Atomicity, replay and non-closure

- The entire apply batch is one caller-owned transaction. Any invalid row, approval/provenance/hash conflict or write failure rolls back every row; no partial case update, provenance row, count or success survives.
- Exact replay reuses the same provenance and canonical legacy value with no mutation. Any changed source, manifest, approval, hash, classification, value or plan under the same identity fails 409.
- Keep the existing Allowed Files list exact. Do not implement or alter D4-12, add schema/migration/API/UI paths, create an approval, infer customer intent, activate source data or absorb another V8 row.
- Synthetic implementation/tests may eventually PASS only under the normal task-local evidence gates. Without the real externally approved manifest, actual customer migration remains gated and must not run.
- This Ultra materialization performs no importer/test edit, evidence initialization, dry-run, apply, customer migration or product verification and runs only the repository atomic task check.
