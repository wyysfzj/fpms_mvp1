# FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["data", "fee", "source-authority", "sqlite"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B.md
Chosen runbook: `P0-single-lane-story`

## Design References

- User-approved design:
  `docs/superpowers/specs/2026-08-25-fpms-demo-v6-runtime-official-source-design.md`.
- Implementation plan:
  `docs/superpowers/plans/2026-08-25-fpms-demo-v6-runtime-official-source.md`.
- Parent V6 design:
  `docs/superpowers/specs/2026-08-23-fpms-demo-v6-dual-track-fee-enrichment-design.md`.

## Exact Closure Slice

For V6 bundles only, require one inline, digest-bound `official_fee_source` containing one canonical
CNIPA rate-book candidate and exactly the fee rows selected by `official_fee_selector`. Validate the
book, rows, authority ledger, canonical replacement-grant due date, and shared row digests before
service start. During a fresh isolated local run, create the candidate and rows in one dedicated
transaction, activate it through the existing activation service with the local reviewer and one
actual bootstrap timestamp, verify the persisted active tuple and digests, and remove the unserved
run root after any post-copy bootstrap failure. Existing grant preview remains the sole amount
consumer and calculation path.

## Fixed Scope Decision

- `shared_file_density=LOW`
- `prereq_dependency_density=LOW`
- `be_fe_coupling=NONE`
- `evidence_cost=HIGH`
- `chosen_runbook=P0-single-lane-story`
- SQLite-writing tests and canonical rehearsal run serially.
- Scope expansion is denied. A newly discovered schema, API, UI, migration, general importer, or
  second rate calculation requirement stops this task.

## Exact Behavior

1. V1 and Integrated A V1 bundle behavior remains byte-for-byte compatible.
2. Integrated A V2 requires `official_fee_source` with one complete rate book and exact selected
   rows; unknown, missing, duplicate, mismatched, inactive-row, non-GOV, non-CNY, non-positive,
   non-fixed, reducible, untrusted-source, non-canonical snapshot, digest, version, reference, or
   effective-interval drift raises `DemoBundleError`.
3. Rate book and every row cover the replacement grant notice `official_due_date=2026-11-24` in the
   synthetic fixture. The immutable snapshot carries that exact date.
4. One core-owned digest helper implements `FPMS_DEMO_RATE_ROW_DIGEST_V1`; the existing grant preview
   imports it and preserves its 400/409 semantics.
5. Fresh V6 bootstrap persists exactly one `PENDING/INACTIVE` candidate and two selected rows, then
   calls `activate_official_rate_book`. The local reviewer is both local actors; `approved_at` and
   `activated_at` are the same actual Asia/Shanghai-naive bootstrap timestamp.
6. Persisted book state is exactly `APPROVED/ACTIVE`, current identity is
   `CNIPA|<book_code>`, row/book digests equal the bundle, and later grant task due date must equal the
   snapshot due date before preview.
7. A materialization or later bootstrap exception rolls back book/rows/activation, disposes the
   engine, and removes the copied unserved run root.
8. `SYNTHETIC_TEST_ONLY` remains technical-only and cannot use `CUSTOMER_DEMO` or reach
   `DEMO_READY`; no test fixture is claimed as actual official fee truth.

## Explicit Non-Closure

- No database schema, migration, global/dev/production seed, new table, API, UI, document, stage,
  fee-reduction behavior, network fetch, or generic importer.
- No customer-authorized bundle creation or activation and no claim that the synthetic fee facts are
  official or customer-ready.
- No change to amount calculation, manual confirmation, GOV/SERVICE separation, downstream drafts,
  PayList, GovPayment, billing, payment, offset, lifecycle, deadline generation, permissions, or
  security.
- No cleanup or refactor outside the exact changed lines needed by this task.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B.md`
- `docs/superpowers/specs/2026-08-25-fpms-demo-v6-runtime-official-source-design.md`
- `docs/superpowers/plans/2026-08-25-fpms-demo-v6-runtime-official-source.md`
- `backend/app/core/demo_bundle.py`
- `backend/app/modules/grant_fees/demo_official_fee.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `backend/tests/test_demo_v6_grant_official_fee.py`
- `artifacts/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B/**`

## Verification Commands

- Recorded contract-complete RED for the new V6 bundle and fresh-run behavior before product edits.
- Focused GREEN:

  ```bash
  backend/.venv/bin/python -m pytest -q backend/tests/test_demo_abc_runtime_bundle.py backend/tests/test_demo_abc_local_runner.py backend/tests/test_demo_v6_grant_official_fee.py
  ```

- Existing integration contract and activation compatibility:

  ```bash
  backend/.venv/bin/python -m pytest -q backend/tests/test_demo_integrated_a_runner.py backend/tests/test_v8_official_rate_book_activation.py
  ```

- Scoped Ruff:

  ```bash
  backend/.venv/bin/ruff check backend/app/core/demo_bundle.py backend/app/modules/grant_fees/demo_official_fee.py backend/scripts/run_local_demo_abc.py backend/tests/test_demo_abc_runtime_bundle.py backend/tests/test_demo_abc_local_runner.py backend/tests/test_demo_v6_grant_official_fee.py
  ```

- Exact scope/diff check and one canonical V6 rehearsal from stages 01–11. If the rehearsal fails,
  preserve evidence and do not broaden this task.

  ```bash
  backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py --profile TECHNICAL_REHEARSAL --runs 2 --headless --artifact artifacts/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B/rehearsal
  ```
- Independent HIGH review of the exact frozen implementation with one final `Verdict: APPROVED`,
  `P0: 0`, `P1: 0`, and `P2: 0`.
- Task gate and atomic evidence validation after the approved review.

Expected HTTP status codes: unchanged existing API semantics; loader/bootstrap failures occur before
HTTP service start.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-CANONICAL-E2E-20260823-06` resumes at its first incomplete rehearsal ordinal after
  this task passes.
- `FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07` remains blocked on an external
  `CUSTOMER_AUTHORIZED` bundle.

## Done Definition

The exact V6 runtime bundle closes the fresh-database source gap; two isolated runs can materialize
the same source digests without shared business identities; the canonical stage 01–11 rehearsal
passes; all scoped checks and independent review pass; evidence validates. No non-closure item is
implemented or claimed.
