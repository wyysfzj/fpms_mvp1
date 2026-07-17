# FPMS-V8-LIVE-FIXTURE-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `17. Wave 8 — real paths and release close`
Catalog ordinal: `275`
Executor role: Tester / monitor

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- Source catalog line: `820`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails on missing evidence or coverage.
- GREEN expectation: Exact audit/E2E/gate commands pass and any failure becomes a new task.

## Exact Closure Slice

Create dedicated live fixture with >100 activities, all lanes, gates/conflicts/unverified facts; do not modify shared P1 live seed.

## Ultra Contract Freeze — 2026-07-14

This section is the complete High implementation contract for the dedicated V8 live
fixture and its exact backend verification. It adds the delta-2 decision-gate fixture
coverage without changing the existing closure slice, product behavior, customer policy
or shared P1 seed.

### Dedicated fixture boundary

- Create only
  `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py`
  and `backend/tests/test_v8_overlay_live_seed.py` for the fixture implementation and
  proof. Do not edit, import as a seed implementation, invoke or append another variant
  to `pdP1LiveSeed.py`.
- The V8 seed owns a distinct, deterministic fixture namespace. Cleanup and reseeding
  may delete only rows carrying that namespace; all P1 live fixture rows and IDs remain
  untouched. Re-running the V8 seed produces the same logical fixture and no duplicate
  current identity.
- The seed remains restricted to an approved dev/test/demo SQLite database with foreign
  keys enabled. It must fail before mutation for a non-SQLite or non-approved
  environment. It must not disable a CHECK, UNIQUE or foreign-key constraint to create
  an error scenario.
- The fixture has more than 100 ordered activities and covers CENTER, DOCUMENT and FEE
  lanes. It includes at least one legacy conflict, at least one unverified fact and the
  warning/provenance needed to observe each through the overlay. Activity sequences are
  deterministic and span the existing three-page cursor path.

### Frozen 29-entry gate fixture

For every dedicated V8 fixture case, the real overlay response MUST contain exactly 29
requested gate entries in the accepted server order:

1. the seven non-legacy `DecisionGateCode` values in enum order, each requested with
   exact scope `case:{case_id}`; then
2. 22 `DG-LEGACY-FORM-CLASS` entries requested in ascending exact scope order
   `form-001` through `form-022`.

Entry identity is exactly `(gate_code, requested_scope_key)`. The repeated legacy gate
code therefore remains 22 distinct entries; the seed and test must not build a
gate-code-keyed dictionary, deduplicate by code or infer a missing scope.

The deterministic data set MUST include all of the following observable cases while
remaining valid under the physical SQLite schema:

- resolved direct non-legacy decisions and at least one each of not-found, REVOKED,
  future-effective and schema-valid-but-semantically-corrupt current rows, projected by
  the overlay as independent `UNRESOLVED` entries with the accepted exact error code;
- direct legacy sentinels `form-001=CURRENT_OFFICIAL`, `form-002=HISTORICAL` and
  `form-003=INTERNAL_ONLY`;
- one valid, canonical and complete `ALL-22` persistence carrier from which at least
  `form-004`, `form-005` and `form-006` resolve respectively as `CURRENT_OFFICIAL`,
  `HISTORICAL` and `INTERNAL_ONLY` when no direct current row exists;
- direct legacy sentinels `form-007` REVOKED, `form-008` future-effective and
  `form-009` schema-valid-but-semantically-corrupt. Each direct current row shadows the
  valid `ALL-22` carrier and becomes its own exact unresolved result rather than falling
  through; and
- deterministic valid direct or fallback coverage for `form-010` through `form-022`, so
  all 22 requested form identities remain present even when individual entries are
  unresolved.

The fail-closed scenarios above are application-level resolver inputs, not an invalid
database fixture. In particular, the seed must not violate the unique current-identity
constraint, corrupt the one valid canonical `ALL-22` carrier, disable foreign keys or
leave the transaction partially committed.

### Provenance and activation boundary

- A direct legacy resolution keeps the requested `form-NNN` and reports the same direct
  `resolved_scope_key`. A fallback resolution keeps requested `form-NNN`, reports
  `resolved_scope_key=ALL-22`, and preserves the selected carrier's exact gate ID,
  source reference, source version, confirmer and effective time.
- Neither the seed, the test nor an observed overlay response may request or emit
  `requested_scope_key=ALL-22`. `ALL-22` exists only as stored fallback provenance and
  as the resolved scope of an individual requested form.
- `HISTORICAL` and `INTERNAL_ONLY` remain source-backed `RESOLVED` classifications that
  are reference-only and not activation-ready. `CURRENT_OFFICIAL` remains the only
  classification eligible for later form-lane activation. This fixture records and
  proves those distinctions only: it does not invoke an activation task, write a
  manifest decision, confirm a real customer choice or expose a mutation path.
- One entry's REVOKED, future or corrupt condition must not invalidate the fixture,
  suppress the other 28 gate entries, remove any activity lane or abort the overlay
  response.

### SQLite serialization

- Every cleanup, seed, commit and rollback performed by the dedicated fixture, and every
  SQLite-writing execution of `test_v8_overlay_live_seed.py`, runs only while holding the
  global lock directory `/tmp/fpms_v8_sqlite.lockdir`. Lock release must occur in a
  `finally` path after the database session is closed.
- The RED and GREEN pytest commands below are exact, but the executor must acquire that
  global lock before invoking either command. No fixture write or SQLite verification
  may overlap another V8 writer. Shared-file verification remains in the same global
  serialized queue.
- Do not add a second lock namespace, run the fixture writer concurrently, or modify a
  shared seed/package script to obtain serialization.

## Explicit Non-Closure

No product fix, schema change, shared P1 seed edit, customer-choice activation or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- `FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
- `FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
- `FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
- `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
- `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
- `FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): overlay UI

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py`
- `backend/tests/test_v8_overlay_live_seed.py`
- `artifacts/FPMS-V8-LIVE-FIXTURE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Follow the frozen foundation/full close order; QA tasks report failures and never repair product code.

## Exact Fixture Acceptance

`backend/tests/test_v8_overlay_live_seed.py` MUST prove through the dedicated seed and
the accepted overlay seam:

1. A first run and idempotent rerun preserve the P1 fixture and leave one namespaced V8
   case whose activity count is greater than 100, whose sequences are deterministic and
   whose CENTER, DOCUMENT and FEE lanes, legacy conflict and unverified fact are all
   present.
2. The returned overlay has exactly 29 decision-gate entries in frozen order: seven
   `(gate_code, case:{case_id})` identities followed by 22
   `(DG-LEGACY-FORM-CLASS, form-001..form-022)` identities.
3. The repeated legacy gate code remains 22 composite identities. No requested scope is
   `ALL-22`, no gate-code-only deduplication occurs and no entry is missing because
   another entry is unresolved.
4. Direct resolved provenance and valid `ALL-22` fallback provenance are both exact. A
   fallback entry simultaneously retains requested `form-NNN` and resolved `ALL-22`
   with unchanged source fields.
5. The frozen not-found, REVOKED, future-effective and corrupt sentinels produce their
   exact independent unresolved reasons without invalidating the overlay; the direct
   `form-007..form-009` sentinels shadow the valid aggregate carrier.
6. `CURRENT_OFFICIAL`, `HISTORICAL` and `INTERNAL_ONLY` are each represented in both
   direct/fallback coverage required above. The latter two remain resolved
   reference-only values, only the former is activation-ready, and the seed/test perform
   no activation or customer-decision mutation beyond namespaced synthetic fixture data.
7. Foreign keys and schema constraints remain enabled, cleanup is limited to the V8
   namespace, all writes are atomic, and a failure rolls back without leaving a partial
   fixture.
8. A lock probe proves fixture writes and the SQLite test execution use
   `/tmp/fpms_v8_sqlite.lockdir`; a second writer cannot enter the critical section until
   the first releases it.

The RED is the absent dedicated seed or any missing named fixture behavior. GREEN does
not authorize a product repair, shared P1 seed change, customer activation, real UI E2E
assertion or a second QA closure slice.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_overlay_live_seed.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_overlay_live_seed.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_overlay_live_seed.py && .venv/bin/ruff format tests/test_v8_overlay_live_seed.py && .venv/bin/ruff check tests/test_v8_overlay_live_seed.py`
- `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py backend/tests/test_v8_overlay_live_seed.py tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LIVE-FIXTURE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LIVE-FIXTURE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LIVE-FIXTURE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LIVE-FIXTURE-20260712-01` pass. Only then may this task be reported PASS.
