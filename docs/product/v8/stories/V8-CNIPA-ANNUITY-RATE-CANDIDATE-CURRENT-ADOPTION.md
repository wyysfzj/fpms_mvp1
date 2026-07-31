# Story V8-CNIPA-ANNUITY-RATE-CANDIDATE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `cb34955`
- Product/test commits: `fe5edf1`, `c5a7cf4`
- Outcome: current-adopt frozen D4-10 as exactly one inactive, unapproved
  `CNIPA_PATENT_ANNUITY_20260330` candidate and exactly three linked annuity rates.
- Authority: frozen task
  `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`, Delta-4 D4-10, the approved
  latest-wins annuity source correction, `docs/product/v8/domain-contract.md`, and the
  current `SRC-CNIPA-ANNUITY-20260330` record in
  `docs/product/v8/source-decision-registry.md`.
- Change mode: exact product, canonical-data and focused-test byte adoption from archive
  checkpoint `6b2ef89da447353380b99853168d4d38aaf9210a`, followed by fresh current-tree TDD,
  one focused independent-review correction, carrier regressions and scoped verification.
  The archive is implementation input, not current acceptance.

## Dependency and exact scope

The independently accepted current official-rate-book carrier represents every frozen
candidate, source, status, interval, amount and lineage field without schema or migration
changes. The current source record supplies the reviewed 32-page official CNIPA PDF and
supersedes only the original D4-10 source identity; the immutable Delta-4 contract remains
unchanged for all other semantics.

This story changes exactly:

- `backend/app/modules/fees/cnipa_annuity_rate_candidate.py`;
- `backend/app/modules/fees/data/cnipa_payment_guide_20260330_annuity_rates.json`;
- `backend/tests/test_v8_cnipa_annuity_rate_candidate.py`; and
- this story card.

No source-registry change is required because this story relies on the existing active
`SRC-CNIPA-ANNUITY-20260330` source-metadata record without changing its authority.

## Exact adopted bytes and source identity

- Materializer SHA-256:
  `24b831e6dc6b2e9d915d8c9ee8f50690a5befa8c278490e79fdd8c577e5e1cdc`.
- Canonical JSON SHA-256:
  `c2d43de97be37f6263a74e81ab19e525025b94ac937d8b6de6fd1d2f2e480ba3`.
- Focused test SHA-256:
  `c7ee4d278b19cba7006a23e5137793a64c42b60aa77d042f287b9e6b2c5a1274`.
- Official metadata article:
  `https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html`.
- Exact official PDF:
  `https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518`.
- PDF identity: 32 pages, 2478214 bytes, SHA-256
  `3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce`, retrieved
  `2026-07-19T03:55:57Z`.
- Canonical `CNIPA_RATE_SOURCE_V1` snapshot SHA-256:
  `e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544`.

The superseded 31-page direct attachment is not referenced by the product, canonical data
or focused test. The reviewed source identity does not activate a fee book or infer legal
effect before the explicit interval.

## Observable frozen behavior

- Fresh materialization creates one `CNIPA_PATENT_ANNUITY_20260330`, version
  `2026-03-30`, interval `[2026-03-30, None)`, in `PENDING/INACTIVE` state with null
  approval, activation and current identity fields.
- It creates exactly three linked `GOV/CNY/TIER` rates:
  `CN_ANNUITY_FEE_INV`, `CN_ANNUITY_FEE_UM` and `CN_ANNUITY_FEE_DES`. Each is enabled,
  reduction-eligible and remains `PENDING_CONFIRMATION`.
- Each `calc_params` string is byte-canonical `CNIPA_ANNUITY_TIER_V1`. The public parser
  requires exact keys, schema, types, ordering, contiguous positive inclusive years,
  positive two-place decimal amounts and category-specific final endpoints. Invalid input
  and out-of-range years fail deterministically with `409`.
- Candidate, rates and source snapshot retain exact version/hash/linkage. Missing or
  changed canonical data or persisted graph fails `409` without repair or partial reuse.
- Exact replay reuses stable identities without inserts, updates, timestamp churn or
  mutation.
- Replay lookup uses the complete series identity `(CNIPA, book_code, version_code)`.
  A different historical or future version with the same authority and book code remains
  untouched while the exact `2026-03-30` target is created or reused.
- The materializer never commits, rolls back or closes the caller session. Caller commit
  persists the complete graph, caller rollback persists none, and a rate-insert failure
  rolls back only the materializer savepoint.
- The module exposes no activation, seed, fallback or wall-clock path. The inactive
  candidate is not selected or consumed by this story.

## TDD and verification

The focused test was written first while both implementation paths were absent. The exact
serialized RED command exited `1` with `51 failed, 1 warning in 13.53s`; decisive failures
reported the missing public materializer, parser and selector and the absent module.

After the minimum two implementation bytes were added, the same focused command exited
`0` with `51 passed, 1 warning in 13.14s`. The directly affected layout-candidate and
official-rate-book activation regressions exited `0` with
`50 passed, 1 warning in 13.10s`.

Independent review found that the initial replay lookup omitted `version_code`, so a
different valid series version wrongly blocked the exact target. The correction test first
exited `1` with a deterministic `409` and `details={"field":"version_code"}`. Adding only
`OfficialRateBook.version_code == _VERSION` to the lookup made that test pass. The complete
focused suite then exited `0` with `52 passed, 1 warning in 13.41s`; the unchanged
layout-candidate and activation regressions exited `0` with
`50 passed, 1 warning in 13.09s`.

Scoped Ruff and diff/scope inspection passed. Independent `PROTECTED` re-review approved
the exact two-commit product/test result with P0/P1/P2 `0/0/0`; the implementer did not
approve this story.

## Non-goals and rollback

No activation, approval, publication, current-book selection, seed, migration, schema,
shared file, customer or Tianyue fallback, permissive legacy tier parser, fee obligation,
fee calculation, reduction decision, billing, payment, deadline, lifecycle, API, UI,
source-registry, coverage-ledger, disposition, review receipt, task or old evidence change
is included.

Rollback reverts the materializer, canonical JSON, focused test and this story card. It
leaves the accepted source record, official-rate-book carrier, activation service and all
active/current rate-book state unchanged.
