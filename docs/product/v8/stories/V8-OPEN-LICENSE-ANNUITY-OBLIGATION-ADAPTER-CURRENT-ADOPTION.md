# Story V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: current-adopt the frozen open-license implementation-period adapter on the
  lean integrated tree.
- Catalog ID: `FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01`
  (ordinal `155`).
- Authority: the exact frozen task contract, the current V8 domain/source contracts, and
  the independently adopted prerequisite stories named below.
- Historical product checkpoint: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Current prerequisites and exact paths

- Generic fee-obligation recognition is current-verified by
  `V8-FEE-OBLIGATION-CORE-CURRENT-VERIFICATION`.
- Future Annuity recognition and its durable reduction lineage are current-adopted by
  `V8-FUTURE-ANNUITY-OBLIGATION-CURRENT-ADOPTION`.
- The pure best-benefit, non-stacked open-license reduction rule is current-adopted by
  `V8-SPECIAL-OFFICIAL-FEE-RULES-CURRENT-ADOPTION`.
- The adjacent review-bound compensation-period adapter is current-adopted by
  `V8-SPECIAL-FEE-EVIDENCE-OBLIGATION-CHAIN-CURRENT-ADOPTION`.
- `backend/app/modules/documents/evidence_service.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_v8_open_license_annuity_obligation_adapter.py`

## Observable contract

Approval of current, independently reviewed official final evidence for
`open-license-implementation-period` records a canonical, hash-bound period snapshot on
the review activity. The typed adapter accepts only that same-case current evidence and
its exact confirmed review activity, and revalidates the live source against the captured
snapshot before recognition.

Inside the confirmed inclusive period, the adapter accepts only one existing sourced
ordinary `FUTURE_ANNUITY` obligation with its exact task, evidence, active official rate,
and immutable reduction lineage. It applies the pure greater-benefit comparison between
the existing accepted reduction and `15%`, constructs one replacement line, and delegates
once to `recognize_obligation` with the prior obligation as the superseded fact.

It never creates an ordinary annuity obligation. Missing, stale, cross-case, mutated,
non-current, non-canonical, out-of-period, wrong-category, unsupported-rate or invalid
reduction lineage conflicts fail closed with no write. The caller owns the transaction;
the adapter performs no commit or rollback, and generic recognition owns the sole fee
activity.

## TDD, verification and review

The focused eight-function test was restored byte-for-byte from the historical checkpoint;
its SHA-256 is
`28c921f1708ffd48f0f663318ca689dc8cbef7e1a71214f024bfb96f793ab8e9`.
The contract-complete RED exited `1` with `29 failed`, proving the missing adapter boundary
and review snapshot. The minimum current-tree port then passed the focused matrix with
`29 passed`.

The exact affected five-file regression tranche passed `130` tests and `16` subtests. Both
passing runs retained one inherited third-party passlib `crypt` deprecation warning.
Scoped Ruff check-only, Python parsing and exact diff checks are required before handoff.
Because this is protected fee/evidence-lineage work, an independent High reviewer must
review the exact candidate and rerun the decisive checks; the implementer does not approve
this story.

## Non-goals and rollback

No rate or source activation, underlying reduction-rule change, ordinary annuity creation,
schema/migration/seed, API/UI, payment, PayList, ledger/disposition/review receipt, old
task/evidence machinery, second entrypoint or adjacent cleanup is included.

Rollback removes only the open-license review-snapshot dispatch, adapter slice, focused
test and this story card. All prerequisite obligation, annuity, rate and evidence behavior
remains unchanged.
