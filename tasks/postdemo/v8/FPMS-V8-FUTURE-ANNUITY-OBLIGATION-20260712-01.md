# FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `133`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `575`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Annuity task becomes a sourced yearly obligation with type/year/due, scoped reduction/payable amount and instruction state.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): recognize, annuity payable amount

### Shared ownership serialization

- `backend/app/modules/annuity/service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01.md`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_future_annuity_obligation.py`
- `artifacts/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_obligation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_obligation.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_future_annuity_obligation.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_future_annuity_obligation.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_future_annuity_obligation.py`
- `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_future_annuity_obligation.py tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 595–642, with the exact D4-10 rate text at lines 525–555 and D4-11 lineage carrier at lines 560–576.
- Supplemental authority: row `25 / M4-G / H4-5` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work and evidence remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact source, rate, amount, lineage, replay, transaction and dependency contract below; every other inherited byte and the existing allowlist remain unchanged history.

### Exact public seam and source evidence

- Public seam is exact `recognize_future_annuity_obligation(command: RecognizeFutureAnnuityObligationCommand, transaction: Session) -> RecognizeFutureAnnuityObligationResult`.
- Command exact fields are `annuity_task_id`, `source_activity_id`, `source_document_id`, `source_evidence_version_id`, `source_evidence_content_hash`, `grant_fee_year_key`, `rate_effective_on`, `reduction_input`, `reduction_approval_id`, `actor_id`, `idempotency_key`.
- Source activity must be same-case exact `GRANT_ANNOUNCEMENT_CONFIRMED`, `lane=LIFECYCLE`, `confirmation_status=CONFIRMED`, with exactly one `DOCUMENT_EVIDENCE_VERSION / DocumentEvidenceVersion` reference matching the command version ID/hash and captured at the activity's naive effective time. Zero, multiple, extra or unknown links fail 409.
- For fresh recognition, the version and document are same-case and match `source_document_id`; version role is exact `OFFICIAL_FINAL_PDF`, state `FINAL`, review `APPROVED`, naive non-null `reviewed_at`, nonblank reviewer distinct from creator, exact stored hash, and exact current identity `f"{case_id}|{lineage_key}"`.
- Event link, version and carrier must agree byte-for-byte, and the case must be in an accepted grant/post-grant projection. Never infer source from a latest row, `first_annuity_year`, filename, mutable replacement or wall clock.

### Exact six-field lineage, obligation and amount

- The task carrier's six fields are exact `source_activity_id`, `source_document_id`, `source_evidence_version_id`, `source_evidence_content_hash`, `fee_obligation_id`, `grant_fee_year_key`; fresh writes require all six non-null, hash full-match `sha256:[0-9a-f]{64}`, and `grant_fee_year_key >= 1`.
- Supplied source, grant-year and due values must match task facts. Category maps to exact `CN_ANNUITY_FEE_INV`, `CN_ANNUITY_FEE_UM` or `CN_ANNUITY_FEE_DES`; obligation type is `FUTURE_ANNUITY`, fee year key is the task year number, due date is the task due date, and currency is `CNY`.
- The effective obligation-line identity remains exact `lowercase_hex_sha256(utf8(case_id + "|" + source_activity_id + "|" + fee_code + "|" + str(fee_year_key)))`; do not normalize, alias or infer any component.
- Require exactly one active, approved and `rate_effective_on`-effective `CNIPA_PATENT_ANNUITY_20260330` book and exactly one linked category rate; select the full tier by `grant_fee_year_key` through the strict canonical parser, never a permissive legacy `TIER` helper or customer/Tianyue fallback.
- Validate reduction through `validate_annuity_fee_reduction()` with exact approval coverage. Payable amount is the finite full annual amount times the validated payable ratio, quantized once to `Decimal("0.01")` with `ROUND_HALF_UP`; preserve the unreduced full annual amount as official amount and late-fee base.
- Initial instruction stays pending; never copy legacy `PAY`, `ABANDON` or `DEFER`, and do not create a draft/letter or mutate a legacy instruction.

### Exact active-rate `calc_params`

- Each selected `FeeRate.calc_params` is exact UTF-8 sorted-key compact JSON with no ASCII escaping or trailing newline; accept top-level keys exactly `schema`, `tiers`, schema exact `CNIPA_ANNUITY_TIER_V1`, tier keys exactly `amount`, `from`, `to`, positive non-bool contiguous inclusive years starting at 1, and positive two-place decimal amounts.

```text
CN_ANNUITY_FEE_INV={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"900.00","from":1,"to":3},{"amount":"1200.00","from":4,"to":6},{"amount":"2000.00","from":7,"to":9},{"amount":"4000.00","from":10,"to":12},{"amount":"6000.00","from":13,"to":15},{"amount":"8000.00","from":16,"to":20}]}
CN_ANNUITY_FEE_UM={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"600.00","from":1,"to":3},{"amount":"900.00","from":4,"to":5},{"amount":"1200.00","from":6,"to":8},{"amount":"2000.00","from":9,"to":10}]}
CN_ANNUITY_FEE_DES={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"600.00","from":1,"to":3},{"amount":"900.00","from":4,"to":5},{"amount":"1200.00","from":6,"to":8},{"amount":"2000.00","from":9,"to":10},{"amount":"3000.00","from":11,"to":15}]}
```

- Unknown, missing, extra or reordered keys/text, malformed amount, non-contiguous/overlapping/gapped tiers, out-of-range year, absent/multiple/inactive/unapproved/ineffective book or linked rate fails closed with 409 and selects no rate.

### Replay, transaction, dependencies and non-closure

- Resolve and compare an exact existing idempotent obligation/task-carrier replay before the fresh-current guard, so a later reviewed replacement cannot invalidate immutable replay. Changed source, hash, carrier, rate, link or idempotency truth under the same key fails 409.
- Delegate exactly once to `recognize_obligation()`, then atomically set or reuse all six lineage fields. The caller owns the transaction; no internal commit/rollback and no partial obligation, activity or carrier state survives failure.
- D4-10 `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01` and D4-11 `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01` require independently accepted PASS; D4-10 also requires explicit accountable activation before selection. Accepted recognize-obligation and annuity-payable rules remain prerequisites.
- Shared `backend/app/modules/annuity/service.py` order is D4-11 PASS → row 25 / Task 133 → row 24 / Task 121; each owner releases it only after independent acceptance, with SQLite verification serialized.
- Keep the existing Allowed Files list exact. Do not implement or alter D4-10/D4-11, activate a candidate, add rate/schema/migration/API/UI paths, infer missing lineage/source/rate/approval, or absorb Task 121.
- This Ultra materialization performs no product/test edit or evidence initialization and runs only the repository atomic task check.
