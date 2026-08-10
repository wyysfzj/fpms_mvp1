# Story V8 Full Batch Customer Decision Current Adoption

- Risk: `PROTECTED`.
- Status: `IMPLEMENTING`.
- Customer source:
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`.

## Exact closure

Preserve the customer's exact Scheme A approval, bind its content hash and decision version,
and update the V8 source/decision registry for exactly:

- `DG-FEE-APPLICATION-DRAFT:GLOBAL`;
- `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL`;
- `DG-FEE-FUTURE-ANNUITY:GLOBAL`;
- `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`;
- `DG-GRANT-MANUAL-REVIEW:GLOBAL`;
- `DG-LEGACY-FORM-CLASS:form-001` through `form-022`.

The first five identities become approved policy contracts. All 22 form identities receive the
exact classification `INTERNAL_ONLY`. Grant-source and grant-review runtime remain fail-closed
until an institution administrator publishes complete, current, independently reviewed source
and role configuration. Missing, stale, unreviewed or incomplete configuration is `409`, performs
no write and cannot change legal status.

## Explicit non-closure

- Do not confirm or activate `DG-PAYMENT-WORKBOOK:GLOBAL`.
- Do not confirm or activate `DG-SERVICE-RATE-VERSION:GLOBAL`.
- Do not select, invent or activate a concrete CNIPA grant source.
- Do not create production role defaults or test-role production seed data.
- Do not implement product, schema, migration, API, UI or runtime behavior in this story.
- Do not change the frozen catalog or run Full, Final or Release gates.

## Exact path ownership

- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`;
- `docs/postdemo/postdemo_v8_full_batch_decision_clarification_20260810.md`;
- `docs/product/v8/source-decision-registry.md`;
- `docs/product/v8/stories/V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION.md`;
- `docs/product/v8/reviews/V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION.md`;
- `docs/product/v8/coverage-ledger.json` only after independent approval.

## Acceptance

An independent High reviewer must verify the exact customer-source bytes and hash, all 27 exact
approved identities, the two still-pending identities, configurable-but-disabled grant runtime,
the separation-of-duties boundary and unchanged frozen catalog. The reviewer must return
`APPROVED` with `P0/P1/P2 = 0/0/0` before current-owner coverage adoption.
