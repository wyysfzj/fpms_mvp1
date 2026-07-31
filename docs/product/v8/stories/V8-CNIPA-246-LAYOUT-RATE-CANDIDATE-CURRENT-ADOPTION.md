# Story V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Implementation base: `21b12ae9dc740f19686584978acbd2e22555dd06`.
- Current integration parent for independent review:
  `60c35213c67218ff4c2f1664bbdc832e3f976a6c`.
- Outcome: current-adopt frozen D4-09 as exactly one inactive, unapproved
  `CNIPA_LAYOUT_246` candidate and one linked
  `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY` rate.
- Authority: frozen task
  `FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01`, Delta-4 D4-09,
  `docs/product/v8/domain-contract.md`,
  `docs/product/v8/source-decision-registry.md`, and the accepted source prerequisite
  integrated at `65efb39`.
- Change mode: exact product, canonical-data and focused-test byte adoption from archive
  checkpoint `6b2ef89da447353380b99853168d4d38aaf9210a`, followed by fresh current-tree TDD,
  scoped verification and independent High review.

## Dependency and exact scope

The accepted current official-rate-book carrier represents every frozen candidate,
source, status, interval, amount and lineage field without schema or migration changes.
The accepted source prerequisite supplies exactly:

- `reference/cnipa/announcement_246_20170630.normalized.txt`, SHA-256
  `13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8`;
- `reference/cnipa/announcement_246_20170630.provenance.json`, SHA-256
  `2ff9eb7e84253359b2075e972bdd955313b95955f0ebad5e3d1b9fe9ec642377`.

This story changes exactly:

- `backend/app/modules/fees/cnipa_layout_rate_candidate.py`;
- `backend/app/modules/fees/data/cnipa_246_layout_rate.json`;
- `backend/tests/test_v8_cnipa_246_layout_rate_candidate.py`;
- `docs/product/v8/cutover-dirty-path-disposition.json`; and
- this story card.

The source files are accepted dependencies and remain byte-unchanged. No source-registry
change is required because this story relies on the existing active
`SRC-CNIPA-LAYOUT-246-20170630` source-metadata record without changing its authority.

## Exact adopted bytes

- Materializer:
  - archive Git blob `b9cd94da9cdc72f5a7c9b8336e9be2b6ff902611`;
  - SHA-256 `908f2234686e0bf8949e0cbe62d40ca603e589779939b1d889ba046ec6068182`.
- Canonical JSON:
  - archive Git blob `4ad10f67278987ff66d3e200126f44472d123cb3`;
  - SHA-256 `4d7756b3656db9b9184903f794002fd73396105b9392fbcf61c977ec71337d40`.
- Focused test:
  - archive Git blob `0b7b4d679acf5cd5fadc96c0de39063fcf4c1abe`;
  - SHA-256 `846c9de62396956da1b37a9fb54d54248d1da91ca4c3f238e133ed332c4b1afd`.

The canonical `CNIPA_RATE_SOURCE_V1` snapshot hash is
`f05e0f4200ce89a7cb1a8b5fb5d81508f76040a9a008b55969049460298cbfc4`.

## Observable frozen behavior

- Fresh materialization creates one `CNIPA_LAYOUT_246`, version `2017-07-01`,
  interval `[2017-07-01, None)`, in `PENDING/INACTIVE` state with null approval,
  activation and current identity.
- It creates one linked `IC_LAYOUT_REGISTRATION_FEE` rate with exact amount
  `1000.00 CNY`, `GOV/FIXED`, `allow_reduction=False`, enabled and
  `source_status=PENDING_CONFIRMATION`.
- Candidate and rate retain the exact source/version/hash linkage. Missing or changed
  canonical data, normalized source, provenance or persisted graph returns 409.
- Exact replay reuses stable identities without inserts, updates, timestamp churn or
  mutation. Changed replay preserves the caller's pre-call transaction state.
- The materializer never commits. Caller commit persists the complete graph, caller
  rollback persists none, and a rate-insert failure rolls back only the materializer
  savepoint.
- The candidate remains non-consumable because its book is unapproved and inactive.
  The module exposes no activation, seed, promotion or fallback surface.

## TDD and verification

The focused test was adopted first while both implementation paths were absent. The exact
serialized RED command exited `1` with `17 failed`; the decisive failures were
`public CNIPA layout 246 materializer is missing` and
`ModuleNotFoundError: No module named 'app.modules.fees.cnipa_layout_rate_candidate'`.

After the two exact implementation bytes were adopted, the exact serialized focused GREEN
exited `0` with `17 passed, 1 warning in 4.94s`; scoped Ruff also passed. An independent
High reviewer must rerun the decisive check and review the exact commit. The implementer
does not approve this story.

## Disposition, non-goals and rollback

The three exact adopted paths move from `V8-ADOPT-ANNUITY-RATE-SOURCES` to this story.
The broad owner count changes `34 -> 31`, and this story owns exactly `3`; all other
entries and counts remain unchanged.

No registry edit, source activation, approval, promotion, current-book identity, customer
seed, API, UI, schema, migration, fee calculation, billing, payment, deadline, lifecycle,
customer data, other rate, annuity rate, release or milestone closure is included.

Rollback reverts the materializer, canonical JSON, focused test, their three exact
disposition assignments/counts and this story card. It leaves the accepted source
prerequisite and all active/current rate-book state unchanged.
