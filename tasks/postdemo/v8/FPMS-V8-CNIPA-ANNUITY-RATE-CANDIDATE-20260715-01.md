# FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED

## Task Identity

- Task ID: `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`
- Risk Tier: `HIGH`
- Contract State: `CONTRACT FROZEN`
- Execution Runbook: `P0-prereq-heavy-story`
- Atomic owner: exactly one implementing agent owns this task file and closure slice.

## Frozen Authority

- Canonical authority: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, primary-source table lines 486-508 and exact `D4-10` contract lines 524-559.
- This task freezes one inactive CNIPA annuity rate-candidate closure only.
- The approved rate-book carrier is a prerequisite dependency and remains the activation owner.
- Missing, conflicting, stale, or unverifiable authority fails closed; the implementer must not infer business values.

## Exact Closure Slice

Materialize or exactly reuse one inactive `CNIPA_PATENT_ANNUITY_20260330` candidate and exactly three linked annuity rates, plus the strict canonical `CNIPA_ANNUITY_TIER_V1` parser, so that:

1. the book, source snapshot/hash, three rates and byte-for-byte `calc_params` match the frozen contract;
2. malformed/noncanonical tiers and changed replay fail `409` before any selection or write;
3. exact replay reuses the complete persisted candidate without mutation; and
4. the candidate remains `PENDING/INACTIVE`; this task never activates or selects it.

## Explicit Non-Closure

- Do not activate, publish, select, seed, migrate, or promote the candidate; only the accepted `activate_official_rate_book()` service may later activate it.
- Do not change official-fee calculation, receivable truth, reduction semantics, deadlines, billing, UI, API, schema, or permissions.
- Do not guess or normalize missing tiers, rates, units, source facts, effective dates, versions, hashes, statuses, or provenance.
- Do not edit the rate-book carrier or any shared ownership file.
- Do not use `date.today()`, wall-clock-derived effective facts, auto approval/activation, customer/Tianyue/legacy fallback, compatibility aliases, network retrieval, speculative abstraction, or unrelated cleanup.

## Dependency

- Hard prerequisite: `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01` must have independently accepted PASS before implementation or verification begins.
- This task may create and validate only the inactive candidate; dependency absence or non-acceptance must never cause activation or inferred carrier behavior.

## Remaining Follow-Up Task IDs

- `None` — rate-book carrier activation remains a separate dependency-owned closure and is not absorbed here; its exact approved task ID must come from the frozen dependency manifest before activation.

## Exact Data Contract

### Candidate and source identity

- Materialize/reuse exactly series identity `("CNIPA", "CNIPA_PATENT_ANNUITY_20260330", "2026-03-30")`, with `version_code=source_version="2026-03-30"` and inclusive/open effective interval `[2026-03-30, None)`. The interval identifies use of this reviewed snapshot; it makes no unsupported historical claim.
- Primary source is exactly `https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf`, title `专利和集成电路布图设计缴费服务指南`, published/updated `2026-03-30`; no customer or commercial source may appear.
- `source_snapshot` is exact UTF-8 sorted-key compact JSON with no ASCII escaping or trailing newline, top-level keys exactly `schema_version`, `sources`, schema exact `CNIPA_RATE_SOURCE_V1`, and one source entry with keys exactly `content_sha256`, `document_no`, `published_on`, `retrieved_at`, `title`, `url`. It carries the frozen lowercase 64-hex PDF-byte hash, `document_no=null`, exact date/title/URL and the data file's exact UTC `retrieved_at` ending `Z`.
- `source_snapshot_hash` is the lowercase 64-hex SHA-256 of those exact canonical UTF-8 snapshot bytes. The explicit source reference/date, first snapshot entry and inner content hash must full-match; missing, extra, malformed, placeholder or mismatched provenance fails `409`.
- Candidate state is exactly `approval_status=PENDING`, `activation_status=INACTIVE`, with `approved_by`, `approved_at`, `activated_by`, `activated_at` and `current_identity_key` all null.

### Exact linked rates and tier strings

- Create exactly three linked rows, and no others: `CN_ANNUITY_FEE_INV`, `CN_ANNUITY_FEE_UM`, `CN_ANNUITY_FEE_DES`; each has `fee_type=GOV`, `currency=CNY`, `calc_mode=TIER`, `enabled=True`, `allow_reduction=True`, `source_status=PENDING_CONFIRMATION`, and `official_rate_book_id` linking the exact candidate/source/hash tuple.
- Each `FeeRate.calc_params` is exactly the following UTF-8 text, byte-for-byte, with no trailing newline:

```text
CN_ANNUITY_FEE_INV={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"900.00","from":1,"to":3},{"amount":"1200.00","from":4,"to":6},{"amount":"2000.00","from":7,"to":9},{"amount":"4000.00","from":10,"to":12},{"amount":"6000.00","from":13,"to":15},{"amount":"8000.00","from":16,"to":20}]}
CN_ANNUITY_FEE_UM={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"600.00","from":1,"to":3},{"amount":"900.00","from":4,"to":5},{"amount":"1200.00","from":6,"to":8},{"amount":"2000.00","from":9,"to":10}]}
CN_ANNUITY_FEE_DES={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"600.00","from":1,"to":3},{"amount":"900.00","from":4,"to":5},{"amount":"1200.00","from":6,"to":8},{"amount":"2000.00","from":9,"to":10},{"amount":"3000.00","from":11,"to":15}]}
```

- Thus INV is exactly years `1-3/900.00`, `4-6/1200.00`, `7-9/2000.00`, `10-12/4000.00`, `13-15/6000.00`, `16-20/8000.00`; UM is `1-3/600.00`, `4-5/900.00`, `6-8/1200.00`, `9-10/2000.00`; DES is those UM tiers plus `11-15/3000.00`.

### Strict parser, replay, activation and transaction

- Parser top-level keys are exactly `schema`, `tiers`, in canonical sorted-key compact text; schema is exactly `CNIPA_ANNUITY_TIER_V1`; every tier has keys exactly `amount`, `from`, `to` in canonical order. `from`/`to` are positive non-bool integers with inclusive endpoints; tiers start at 1, ascend, and are contiguous with no overlap/gap; amount is a positive exact two-place decimal string; final endpoints are INV `20`, UM `10`, DES `15`.
- Unknown/missing/extra/reordered keys or bytes, wrong types/schema/code/endpoint, duplicate/out-of-order/non-contiguous intervals, invalid amount, or an out-of-range year fails `409`, selects no rate and writes nothing. Task 133 must use this parser, never a permissive legacy `TIER` helper.
- Exact replay identity is the series identity plus exact effective/state/source snapshot/hash and the complete set of three linked rate tuples including byte-identical `calc_params`. A full match returns the existing candidate/rates without mutation; any missing/extra/changed book, source, hash, link, rate attribute or bytes under that identity fails `409` and does not repair or partially reuse it.
- Materialization validates before writing, writes the book and all three rates atomically in the caller's transaction, and may flush but never internally commits, rolls back or closes. Failure leaves no partial book/rate write.
- Enabled/PENDING_CONFIRMATION rates remain unusable through generic legacy selectors while the book is inactive. Only accepted `activate_official_rate_book()` with existing active accountable approval/activation actors and exact actor times may later produce `APPROVED/ACTIVE`; this materializer never calls it.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01.md`
- `backend/app/modules/fees/cnipa_annuity_rate_candidate.py`
- `backend/app/modules/fees/data/cnipa_payment_guide_20260330_annuity_rates.json`
- `backend/tests/test_v8_cnipa_annuity_rate_candidate.py`
- `artifacts/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01/**`

No other path is allowed.

## Implementation Requirements

- Implement the smallest strict parser/validator needed for this frozen candidate contract.
- Keep the JSON candidate explicitly inactive and traceable to the CNIPA payment guide dated `2026-03-30`.
- Validate exact field presence, types, canonical values, tier uniqueness/order/non-overlap, source/version/status/provenance consistency, and frozen hash integrity.
- Return immutable or non-mutating parsed data through the public module interface.
- Raise deterministic domain validation errors for every rejected candidate; do not partially accept data.
- Keep all rates and metadata sourced from frozen authority; any unavailable exact fact is `BLOCKED`, not a placeholder.

## Test Requirements

Write targeted tests through the public materializer/parser interfaces covering at least:

- exact book/version/interval, canonical source snapshot and both hashes, null actor/current fields, and `PENDING/INACTIVE` state;
- exactly three linked `GOV/CNY/TIER` rows with `enabled=True`, `allow_reduction=True`, `source_status=PENDING_CONFIRMATION`, the exact tiers/endpoints and all three byte-identical `calc_params` strings;
- parser acceptance of every valid tier and `409` for unknown/missing/extra/reordered keys/text, wrong schema/types, bool endpoints, bad decimals, gaps/overlaps/order, wrong final endpoints and out-of-range years, with no selection/write;
- exact replay returns the same complete candidate without mutation; changed/partial source/hash/link/rate replay fails `409` without repair;
- caller-owned transaction has no internal commit/rollback/close and any failure leaves no partial book/rate row; and
- no `date.today()`, auto approval/activation, permissive legacy parser, customer/Tianyue/legacy fallback, runtime selection or fee computation path is exposed.

## Verification Commands

Run only task-scoped checks authorized by this contract:

1. targeted RED/GREEN tests for `backend/tests/test_v8_cnipa_annuity_rate_candidate.py`;
2. targeted lint/type checks only if the repository task gate requires them for the allowed Python files;
3. repository task validation and atomic evidence validation for this task; and
4. allowlist and baseline-subtracted diff validation proving no outside-scope change.

SQLite-writing tests, broad backend suites, full-repository lint/test/build, broad Playwright, migrations, seeds, and release gates are outside this task.

## Evidence Path

- `artifacts/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01/**`

## Evidence Requirements

Evidence must remain under `artifacts/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01/**` and include:

- task-local `results.jsonl` containing the latest required command results and logs;
- `summary.md` with an evidence-backed PASS/FAIL/BLOCKED outcome;
- scoped `git/diff.patch` including tracked and untracked allowlist changes;
- dirty-baseline artifacts when applicable;
- scope validation, repository task gate, and atomic evidence validation results; and
- one independent reviewer verdict with zero unresolved findings before PASS.

The implementer cannot approve its own work. Missing evidence, source facts, dependency authority, or independent approval fails closed.

## Acceptance Criteria

- Exactly one inactive `CNIPA_PATENT_ANNUITY_20260330` candidate and the exact three linked rates exist from the allowed canonical JSON.
- The public parser validates the byte-frozen strings, exact tier schema/types/order/contiguity/endpoints/amounts and deterministic `409` failures.
- Source snapshot/hash, complete replay identity and caller-owned all-or-nothing transaction behavior are proven.
- Targeted tests prove no activation, selection, wall-clock, permissive-parser or customer-fallback side effect.
- No rate-book carrier, runtime official-fee truth, schema, shared file, or outside-allowlist path changes.
- Required task-local evidence is complete and the independent reviewer records an approved zero-finding verdict.

## Done Definition

This task is done only when the inactive candidate and strict fail-closed parser satisfy all acceptance criteria, targeted verification passes, the scoped diff contains only Allowed Files, required Evidence 1.1 artifacts validate, the repository task gate and atomic evidence validator pass, and an independent reviewer approves the exact closure with zero unresolved findings. Any activation, unresolved source fact, missing dependency authority, scope drift, or missing evidence yields `FAIL` or `BLOCKED`, never PASS.
