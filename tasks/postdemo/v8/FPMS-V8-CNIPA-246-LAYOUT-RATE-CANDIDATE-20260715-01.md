# FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED

- Risk: `HIGH`
- Priority / lane: `P0-prereq-heavy-story`

## Frozen authority

- Contract delta: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, D4-09 and lines 486-559.
- This task implements exactly one frozen closure. Any conflict, missing source fact, or changed dependency fails closed and requires contract review; it is not resolved in code.

## Exact Closure Slice

Materialize or reuse exactly one `CNIPA_LAYOUT_246` candidate with version `2017-07-01` and effective interval `[2017-07-01, None)`, plus exactly one linked `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY` rate. The rate is `GOV/FIXED`, `allow_reduction=False`, enabled, exactly source/hash linked, and retains `source_status=PENDING_CONFIRMATION`.

The candidate remains `PENDING/INACTIVE`; approval, activation, and current identity are null. The canonical data and `CNIPA_RATE_SOURCE_V1` snapshot are hash-locked. Exact replay reuses without mutation; changed replay returns 409. The caller owns the transaction: the materializer never commits and no failure leaves a partial write.

## Explicit Non-Closure

- Do not activate or promote the candidate, create a customer seed, or change any active rate book, fee calculation, billing, payment, deadline, lifecycle, UI, API, schema, migration, or customer data.
- Do not add a customer, legacy, internal-workbook, cached, inferred, hard-coded, or current-rate fallback.
- Do not reinterpret `source_status=PENDING_CONFIRMATION`, infer source facts, or replace the exact frozen amount, version, effective interval, status, or hash linkage.
- Do not broaden to another CNIPA item, another rate candidate, shared refactors, or release/Foundation/Full closure.

## Dependency and readiness

- Required dependency: the accepted rate-book carrier contract and implementation must be present before this candidate is implemented or verified.
- If the carrier cannot represent every required source/version/hash/status/amount/provenance field exactly, stop as `BLOCKED`; do not extend the closure silently.
- No customer decision or customer-source fallback is authorized by this task.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01.md`
- `backend/app/modules/fees/cnipa_layout_rate_candidate.py`
- `backend/app/modules/fees/data/cnipa_246_layout_rate.json`
- `backend/tests/test_v8_cnipa_246_layout_rate_candidate.py`
- `artifacts/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01/**`

Every tracked or untracked change outside this allowlist is out of scope. Shared ownership, an overlapping writer, or a required extra path blocks execution until the contract is amended and independently accepted.

## Frozen semantics

### Candidate state

- Materialize or exactly reuse one `CNIPA_LAYOUT_246`; code, version `2017-07-01`, and interval `[2017-07-01, None)` are immutable replay identity.
- Its state is exactly `PENDING/INACTIVE`, with approval, activation, and current identity null; it is never selected by runtime lookup.
- The linked rate is enabled but remains non-consumable because the linked book is not approved/active. Strict consumers use that book state as authority and never reinterpret the legacy safety field.

### Source identity, version, and hash

- The canonical JSON data and `CNIPA_RATE_SOURCE_V1` snapshot each use the carrier's exact locked hash; the candidate and linked rate preserve exact source/snapshot/hash linkage.
- Missing, blank, malformed, placeholder, unsupported, changed, or mismatched source identity or hash fails closed before any write.
- A URL, filename, publication date, customer source, or cached extraction cannot substitute for the locked snapshot.

### Amount

- Materialize exactly one linked `IC_LAYOUT_REGISTRATION_FEE` amount `1000.00` in `CNY`, represented without float conversion, rounding, or normalization drift.
- The rate is exactly `GOV/FIXED`, `allow_reduction=False`, enabled, and `source_status=PENDING_CONFIRMATION`.
- Any changed item, amount, currency, rate class/type, reduction flag, enabled flag, or source status is a changed replay and returns 409; no fallback is permitted.

### Provenance

- Preserve the exact graph from `CNIPA_LAYOUT_246` through its linked rate to `CNIPA_RATE_SOURCE_V1` and both locked hashes.
- Canonical data, persisted values, and carrier output must agree exactly; missing, partial, contradictory, unverifiable, or substituted provenance fails closed.

### Error behavior

- An exact replay returns the existing candidate/rate identities with no insert, update, timestamp churn, or other mutation.
- Any changed replay returns deterministic 409 before mutation; validation failure and database failure leave no partial candidate/rate graph.
- The caller owns commit/rollback. The materializer performs no internal commit and does not activate, promote, seed, coerce, skip, or fall back.

## Observable acceptance

1. On an empty caller transaction, the public materializer creates exactly one `CNIPA_LAYOUT_246`, version `2017-07-01`, interval `[2017-07-01, None)`, in `PENDING/INACTIVE`, with null approval/activation/current identity.
2. It creates exactly one linked `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY`, `GOV/FIXED`, `allow_reduction=False`, enabled, `source_status=PENDING_CONFIRMATION` rate.
3. Candidate and rate exactly link the hash-locked canonical data and `CNIPA_RATE_SOURCE_V1` snapshot; a missing or mismatched source/hash is rejected before writes.
4. Exact replay returns the same identities and proves zero inserts, updates, timestamp changes, or other mutation.
5. Every changed-field or changed-hash replay returns 409 and proves no partial write; the same transaction observes its pre-call state.
6. A transaction spy proves the materializer never commits; caller commit persists the complete graph and caller rollback persists none.
7. Runtime consumption remains blocked by the linked book's inactive/unapproved state; no activation, customer seed/promotion, or fallback path exists.

## Done Definition

- Exactly one frozen candidate/rate graph is materialized or reused with every value and locked hash above, while remaining inactive/unapproved.
- Targeted tests prove exact no-mutation replay, changed-replay 409, caller-owned commit/rollback, and zero partial writes.
- The scoped diff contains no outside-allowlist path, and all required evidence and independent-review gates pass.
- No activation, customer fallback, adjacent rate, or second closure slice is introduced.

## Atomic TDD

### RED

- Add a public-interface test asserting the exact candidate identity/version/interval/state/null fields and exact linked-rate item/amount/currency/class/type/reduction/enabled/source-status fields.
- Add tests asserting both locked hashes and the exact candidate/rate/source linkage.
- Add an exact-replay test asserting stable identities and zero mutation, then changed-field/hash replay tests asserting 409 and unchanged transaction state.
- Add caller commit/rollback tests with a no-internal-commit spy and a failure test proving no partial write.
- Add a test proving inactive/unapproved non-consumption and no activation, customer seed/promotion, or fallback.
- Capture the expected RED result in task-local evidence before implementation.

### GREEN

- Add the minimum carrier and canonical JSON needed to satisfy one failing behavior at a time; reuse the frozen rate-book carrier transaction and snapshot contracts.
- Keep validation deterministic and fail closed; add no unrelated abstraction or configuration.
- Run the targeted test after each behavior and capture the final GREEN result.

### REFACTOR

- Refactor only within the allowlist, only while targeted tests remain green, and only when required to remove duplication introduced by this task.

## Remaining Follow-Up Task IDs

- None. Any newly discovered closure, dependency, shared-owner change, activation work, or customer decision requires a separately frozen task ID.

## Verification Commands

Implementation must record exact commands and exit codes. At minimum:

```bash
pytest -q backend/tests/test_v8_cnipa_246_layout_rate_candidate.py
./scripts/check_task.sh tasks/postdemo/v8/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01.md
./scripts/task_validate.sh FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01
python scripts/atomic_evidence_validate.py FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01
```

Do not run broad SQLite-writing, full-repository, Playwright, release, Foundation, or Full gates unless a later frozen controller explicitly grants and serializes them.

## Evidence Path

- `artifacts/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01/`

## Evidence requirements

Initialize through:

```bash
./scripts/evidence_init.sh FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01 \
  --task-file tasks/postdemo/v8/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01.md \
  --allowlist tasks/postdemo/v8/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01.md \
  --allowlist backend/app/modules/fees/cnipa_layout_rate_candidate.py \
  --allowlist backend/app/modules/fees/data/cnipa_246_layout_rate.json \
  --allowlist backend/tests/test_v8_cnipa_246_layout_rate_candidate.py \
  --allowlist artifacts/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01
```

Task evidence must include task-local `results.jsonl`, `summary.md`, scoped `git/diff.patch`, dirty-baseline artifacts when applicable, RED/GREEN logs, exact source/version/hash/amount/provenance verification, scope validation, repository task-gate output, atomic evidence validation, and an independent review verdict.

## Review and completion gates

- One independent HIGH reviewer must issue a task-local, evidence-backed `APPROVED` verdict with zero unresolved findings; the implementer cannot self-approve.
- PASS requires the latest required results/logs, PASS summary, exact baseline-subtracted scoped diff, no outside-allowlist path, independent approval, repository task validation, and atomic evidence validation.
- Any missing authority, dependency, exact source fact, version, digest, amount, provenance, review, evidence, or gate result is `BLOCKED` or `FAIL`, never guessed or waived.
- Completion reports only evidence-backed modified files, commands and exit codes, evidence path, closure satisfied, non-closure respected, and final `PASS`/`FAIL`/`BLOCKED`.
