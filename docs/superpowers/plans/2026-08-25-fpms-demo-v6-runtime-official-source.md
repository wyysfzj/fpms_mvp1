# FPMS Demo V6 Runtime Official Fee Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a fresh isolated V6 run materialize the exact digest-bound official fee source from its runtime bundle so the existing stage 07 preview can proceed.

**Architecture:** Extend only the Integrated A V2 manifest with one inline immutable rate-book source and exact selected rows. The core loader validates all source/selector/authority/due-date bindings and owns the canonical row digest; the local runner persists a pending candidate and rows, activates through the existing service, then verifies stored facts. The existing preview remains the only calculation consumer.

**Tech Stack:** Python 3.11, dataclasses, JSON/SHA-256, SQLAlchemy, SQLite, pytest, Ruff, existing FPMS demo runner and rate-book activation service.

---

Execution classification: `shared_file_density=LOW`, `prereq_dependency_density=LOW`,
`be_fe_coupling=NONE`, `evidence_cost=HIGH`, `chosen_runbook=P0-single-lane-story`.
All SQLite writes and canonical rehearsal execution are serialized.

## File map

- `backend/app/core/demo_bundle.py`: immutable runtime source types, strict V2 parsing, due-date and
  selector cross-binding, and the one canonical fee-row digest helper.
- `backend/app/modules/grant_fees/demo_official_fee.py`: import the core digest helper and fail before
  amount lookup when the stored task due date differs from the bundle's frozen replacement-notice
  due date; all other preview query, amount, status, and write behavior remains unchanged.
- `backend/scripts/run_local_demo_abc.py`: V6-only rate-book materialization/activation and complete
  unserved-run cleanup on bootstrap failure.
- `backend/tests/test_demo_abc_runtime_bundle.py`: canonical structurally valid synthetic V6 source,
  immutable snapshot assertions, and loader failure matrix.
- `backend/tests/test_demo_abc_local_runner.py`: fresh V6 persistence, activation tuple/digest checks,
  transaction rollback, and run-root cleanup.
- `backend/tests/test_demo_v6_grant_official_fee.py`: align its private source fixture with the new
  canonical loader shape while retaining private preview DB setup.

### Task 1: Freeze RED acceptance matrix and evidence

**Files:**
- Modify: `backend/tests/test_demo_abc_runtime_bundle.py`
- Modify: `backend/tests/test_demo_abc_local_runner.py`
- Modify: `backend/tests/test_demo_v6_grant_official_fee.py`

- [ ] **Step 1: Initialize atomic evidence with the exact task and nine non-artifact allowlist paths.**

Run before any product/test edit:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B --task-file tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B.md --allowlist tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B.md --allowlist docs/superpowers/specs/2026-08-25-fpms-demo-v6-runtime-official-source-design.md --allowlist docs/superpowers/plans/2026-08-25-fpms-demo-v6-runtime-official-source.md --allowlist backend/app/core/demo_bundle.py --allowlist backend/app/modules/grant_fees/demo_official_fee.py --allowlist backend/scripts/run_local_demo_abc.py --allowlist backend/tests/test_demo_abc_runtime_bundle.py --allowlist backend/tests/test_demo_abc_local_runner.py --allowlist backend/tests/test_demo_v6_grant_official_fee.py
```

Expected: task snapshot created and initial worktree recorded clean.

- [ ] **Step 2: Add a canonical synthetic source fixture.**

Build canonical `CNIPA_RATE_SOURCE_V1` JSON using the indexed trusted HTTPS CNIPA reference, a
synthetic content digest, published/retrieved metadata, one book effective from `2026-03-30`, and two
fixed non-reducible GOV/CNY rows effective through `2026-11-24`. Compute book and row digests from
actual content; never use repeated-character placeholder hashes.

- [ ] **Step 3: Add loader RED cases.**

Assert a valid V2 bundle exposes immutable `official_fee_source` and due date. Parametrize one-field
drifts for missing/extra source, noncanonical snapshot/hash, untrusted reference, selector book or
row digest mismatch, row set/order mismatch, source/version/reference mismatch, non-GOV/CNY,
nonpositive amount, non-fixed/reducible row, and book/row interval not covering the replacement
grant due date. Each must fail with `DemoBundleError` before database access.

- [ ] **Step 4: Add runner RED cases.**

Create a V6-specific bundle helper. Assert fresh bootstrap produces exactly one approved/active
book and two selected rows; local reviewer IDs and identical non-null approval/activation times;
current identity and digests match the immutable bundle. Inject an activation/materialization
failure and assert the unserved run root no longer exists. Wrap the activation service with a spy
that observes a `PENDING/INACTIVE` candidate, exact reviewer ID, and identical command timestamps.
For the failure path, suppress only physical `rmtree` after recording its exact target so the test
can reopen the disposed SQLite database and prove book/row counts rolled back to zero; separately
assert engine `dispose()` ran.

- [ ] **Step 5: Add the task-due-date RED case.**

In `test_demo_v6_grant_official_fee.py`, keep a valid source/book but change only the persisted grant
task `due_date` away from the bundle's frozen replacement-notice date. Calling preview must fail with
the existing `DEMO_GOV_RATE_SOURCE_CONFLICT` 409 before returning amounts or writing business rows.

- [ ] **Step 6: Run the exact RED tranche through evidence.**

Run:

```bash
backend/.venv/bin/python -m pytest -q backend/tests/test_demo_abc_runtime_bundle.py backend/tests/test_demo_abc_local_runner.py backend/tests/test_demo_v6_grant_official_fee.py -k 'v6_official_fee_source or v6_bootstrap or rejects_task_due_date_drift'
```

Expected: FAIL only because `official_fee_source`, immutable source snapshot, and runner
materialization do not exist. Preserve the diagnostic RED log; do not classify it as canonical
`test` evidence.

### Task 2: Add immutable source contract and one digest implementation

**Files:**
- Modify: `backend/app/core/demo_bundle.py`
- Modify: `backend/app/modules/grant_fees/demo_official_fee.py`
- Test: `backend/tests/test_demo_abc_runtime_bundle.py`

- [ ] **Step 1: Add frozen source dataclasses.**

Add exact dataclasses for the rate-book fields and digest-covered fee-row fields, plus
`DemoOfficialFeeSource`. Add `official_fee_source` and `official_fee_due_date` to
`DemoBundleSnapshot`; set both to `None` for V1 schemas.

- [ ] **Step 2: Move canonical row hashing to core.**

Implement one public helper in `demo_bundle.py` that serializes
`FPMS_DEMO_RATE_ROW_DIGEST_V1` with the existing sorted, compact, non-NaN JSON rules. Change the
preview's private helper to call/import it; do not change its payload, decisions, amounts, or error
codes.

- [ ] **Step 3: Bind preview to the frozen due date.**

Immediately after loading the bundle snapshot and before rate-book selection, require
`task.due_date == snapshot.official_fee_due_date`; otherwise use the existing source-conflict 409.
This is a provenance equality check, not deadline generation or a new status.

- [ ] **Step 4: Strictly parse and cross-bind the V2 source.**

Add `official_fee_source` to exact V2 top keys. Validate exact keys/types/lengths, canonical source
JSON and SHA-256, trusted `https://www.cnipa.gov.cn` URLs without query/fragment, source versions and
references, exact selector row identity/order/digests, fixed GOV/CNY positive two-place amounts,
inactive reduction, active row status, and coverage of replacement notice `official_due_date`.
Return only frozen dataclasses.

- [ ] **Step 5: Run loader/preview GREEN and compatibility.**

Run focused bundle tests, then existing V1/Integrated V1 cases in the same file. Expected: PASS with
no changed legacy snapshot values.

### Task 3: Materialize and activate exact facts in fresh runs

**Files:**
- Modify: `backend/scripts/run_local_demo_abc.py`
- Test: `backend/tests/test_demo_abc_local_runner.py`

- [ ] **Step 1: Add the V6-only materializer.**

After identity seed, query the configured reviewer, capture one `datetime.now(Asia/Shanghai)` with
timezone removed, insert one PENDING/INACTIVE book and exact source rows, and call
`activate_official_rate_book` with the same reviewer/time for approval and activation and
`expected_current_rate_book_id=None`.

- [ ] **Step 2: Verify before committing.**

Flush and assert `APPROVED/ACTIVE`, `CNIPA|book_code`, actor/time tuple, snapshot hash, exact row set,
book linkage, and shared row digests. Raise on any difference so the dedicated transaction rolls
back.

- [ ] **Step 3: Close the run-root failure path.**

Wrap every action after `run_root.mkdir()` through metadata write. On exception, dispose any created
engine and recursively remove only the exact validated `run_root`, then re-raise. Preserve the
existing preflight rule that never touches an existing/symlinked run root.

- [ ] **Step 4: Run runner GREEN.**

Run focused local-runner tests serially. Expected: V1 remains empty of fee rates; V6 has one book/two
rows; injected failure leaves no root.

### Task 4: Restore affected preview fixture and run focused acceptance

**Files:**
- Modify: `backend/tests/test_demo_v6_grant_official_fee.py`
- Test: all three task-owned test files

- [ ] **Step 1: Align the preview test fixture only.**

Replace its noncanonical `{"fixture":"demo-v6"...}` source with the same canonical source values
required by the loader. Keep its private `OfficialRateBook/FeeRate` seed because it tests the preview
service independently; remove no preview assertions.

- [ ] **Step 2: Run task-owned focused tests through canonical evidence step `test`.**

```bash
backend/.venv/bin/python -m pytest -q backend/tests/test_demo_abc_runtime_bundle.py backend/tests/test_demo_abc_local_runner.py backend/tests/test_demo_v6_grant_official_fee.py
```

Expected: all PASS.

- [ ] **Step 3: Run compatibility tests.**

```bash
backend/.venv/bin/python -m pytest -q backend/tests/test_demo_integrated_a_runner.py backend/tests/test_v8_official_rate_book_activation.py
```

Expected: all PASS without modifying either test file.

- [ ] **Step 4: Run scoped Ruff and exact diff check.**

Use the task's six Python code/test paths. Then run:

```bash
git diff --check 1c75591e5072b545c062f78512cdb4e11f11d584..HEAD -- backend/app/core/demo_bundle.py backend/app/modules/grant_fees/demo_official_fee.py backend/scripts/run_local_demo_abc.py backend/tests/test_demo_abc_runtime_bundle.py backend/tests/test_demo_abc_local_runner.py backend/tests/test_demo_v6_grant_official_fee.py
```

Expected: Ruff rc 0 and exact diff check empty.

### Task 5: Canonical rehearsal, independent review, and close

**Files:**
- Evidence only: `artifacts/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B/**`

- [ ] **Step 1: Commit the exact implementation candidate.**

Commit only task/plan/spec and six code/test paths. Record HEAD/tree and baseline-subtracted patch
SHA-256.

- [ ] **Step 2: Run two canonical V6 rehearsals from the exact controller invocation.**

```bash
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py --profile TECHNICAL_REHEARSAL --runs 2 --headless --artifact artifacts/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B/rehearsal
```

Expected: both ordinals reach stages 01 through 11 PASS; stage 07 reads the materialized book;
run/database/business IDs differ while manifest/authority/book/row digests match. Preserve failure
evidence and stop if any different closure appears.

- [ ] **Step 3: Obtain independent HIGH review.**

Reviewer binds exact candidate, task/spec/plan hashes, patch hash, focused results, and both rehearsal
receipts; must report one final `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.

- [ ] **Step 4: Record scope, task gate, finalize, and validate evidence.**

Only after independent approval, run canonical `scope`, `independent_review`, `task_gate`, and
`atomic_evidence` steps, finalize PASS, and validate. Resume parent Task06 only after this task is
terminal PASS.
