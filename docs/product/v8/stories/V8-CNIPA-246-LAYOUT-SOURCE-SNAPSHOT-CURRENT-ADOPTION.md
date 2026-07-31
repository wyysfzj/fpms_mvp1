# Story V8-CNIPA-246-LAYOUT-SOURCE-SNAPSHOT-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Initial implementation base: `02c38d59ebfa29185ed1dfbea4fcd4c7164fe9e9`.
- Current integration parent for final review:
  `0516701da7834ea0ca12e8c3119173da314d1096`.
- Outcome: current-adopt the exact hash-locked CNIPA Announcement 246 normalized source
  snapshot and provenance carrier required by frozen D4-09, without creating, approving,
  activating or exposing any rate-book candidate.
- Authority: the locked-source requirements of
  `FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01`, Delta-4 D4-09, the source
  precedence and fail-closed rules in `docs/product/v8/source-decision-registry.md` and
  `docs/product/v8/domain-contract.md`, and the explicit adoption dispositions for these
  two source paths. This story is also the first-reliance recorder for its exact active
  source-metadata record.
- Change mode: exact source-byte adoption from archive checkpoint
  `6b2ef89da447353380b99853168d4d38aaf9210a`; the archive is adoption input, not current
  acceptance.

## Dependency split

Preflight for `V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-CURRENT-ADOPTION` confirmed that the
current accepted official-rate-book carrier can represent every frozen D4-09 field, but
the lean base lacks the two locked source files consumed by the archived materializer.
The candidate story is therefore parked with zero changes until this smaller prerequisite
is independently accepted and integrated.

This story closes only the missing source-snapshot prerequisite. It does not claim the
D4-09 candidate, its canonical rate-data file or its materializer.

## Independent review response

Independent review of initial range
`02c38d59ebfa29185ed1dfbea4fcd4c7164fe9e9..278377cfd35cba865ad855440f0ce2af0272217f`
found two P1 authority gaps:

1. the two Announcement 246 source paths remained assigned to the broad
   `V8-ADOPT-ANNUITY-RATE-SOURCES` disposition owner; and
2. the source registry lacked the first-reliance active record required by its own update
   rule.

The correction reassigns only those two disposition entries, updates the two exact owner
counts, and adds one source-metadata-reviewed/not-activated registry record. The adopted
source bytes remain unchanged. The implementer does not approve this response; the full
corrected range requires fresh independent review.

## Exact paths and bytes

- `reference/cnipa/announcement_246_20170630.normalized.txt`
  - archive Git blob: `e5650920f94194aa381d224c51df20db19e78e5d`;
  - SHA-256: `13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8`.
- `reference/cnipa/announcement_246_20170630.provenance.json`
  - archive Git blob: `c9ad7be2693c5db57d9c735dff6d84f30169872c`;
  - SHA-256: `2ff9eb7e84253359b2075e972bdd955313b95955f0ebad5e3d1b9fe9ec642377`.
- `docs/product/v8/cutover-dirty-path-disposition.json`
  - only the two source-path owners change;
  - `V8-ADOPT-ANNUITY-RATE-SOURCES` changes from `36` to `34`; and
  - `V8-CNIPA-246-LAYOUT-SOURCE-SNAPSHOT-CURRENT-ADOPTION` is added with count `2`.
- `docs/product/v8/source-decision-registry.md`
  - adds only active source record `SRC-CNIPA-LAYOUT-246-20170630`.
- `docs/product/v8/stories/V8-CNIPA-246-LAYOUT-SOURCE-SNAPSHOT-CURRENT-ADOPTION.md`

The normalized source is preserved byte-for-byte. The provenance JSON remains canonical,
single-line UTF-8 JSON with a trailing newline.

## Exact source identity and coherence

The source identity is:

- URL:
  `https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html`;
- title: `关于执行新的集成电路布图设计保护费收费标准的公告（第246号）`;
- document number: `第二四六号`;
- published on: `2017-06-30`;
- effective from: `2017-07-01`;
- retrieval method: `normalized-primary-page-excerpt`;
- retrieved at: `2026-07-18T08:39:40Z`; and
- issuer: `国家知识产权局`.

The provenance `content_sha256` exactly equals the normalized source SHA-256. Its URL,
title, document number, publication date, effective date, retrieval method and retrieval
time exactly match the corresponding normalized fields.

The normalized source contains
`IC_LAYOUT_REGISTRATION_FEE=1000.00` with `currency=CNY`, matching the frozen D4-09
source fact. Other Announcement 246 lines remain preserved source evidence only; this
story does not activate, materialize, interpret or claim them as current product rates.

## Verification and independent acceptance

No pytest applies because this story changes only non-executable source-evidence bytes and
no schema, model, migration, seed, canonical rate data or test byte.

Verification is limited to:

- exact current/archive Git-blob identity for both source paths;
- exact SHA-256 checks for both files;
- canonical provenance JSON and field-by-field normalized/provenance coherence;
- content-aware secret and personal-data inspection;
- valid disposition JSON, exact entry inventory and exact `34`/`2` story counts;
- the exact active source record, decision value, authority, effective boundary and
  rollback boundary;
- exact five-path scope and full/fix-range diff checks; and
- one independent `PROTECTED` review of the exact commit.

The implementer does not approve this story. D4-09 may resume only after this exact source
story reaches terminal independent acceptance and is integrated.

## Non-goals and rollback

No registry edit beyond the one exact active source record, no disposition edit beyond
the two exact source owners and two owner counts, and no source activation, source
promotion, candidate materializer, canonical rate data, rate-book or fee-rate write,
schema, migration, seed, customer data, API, UI, calculation, billing, payment, lifecycle,
deadline, other CNIPA candidate, annuity-source path, ledger, review receipt, old evidence
or task-control mutation is included.

Rollback reverts the two source files, their exact disposition ownership/count correction,
the one active source record and this story card. It leaves all current carrier,
activation, rate, customer and application bytes unchanged and returns D4-09 to
`PARKED_DEPENDENCY`.
