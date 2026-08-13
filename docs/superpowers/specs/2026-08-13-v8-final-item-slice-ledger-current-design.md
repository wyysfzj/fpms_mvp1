# V8 Final Item-to-Slice Ledger — Current C3 Design

## Decision

Close Row282 with one derived, read-only ledger over the immutable catalog and the nineteen
accepted external product nodes. The ledger contains exactly 302 effective graph nodes:

- 283 immutable catalog rows;
- 19 external product nodes introduced by Delta-1 through Delta-4;
- 216 effective Foundation requirements: the immutable 197 Foundation rows plus the same
  19 external product nodes;
- 86 immutable deferred catalog rows.

These are graph counts, not rewritten catalog or Foundation counts. Audit-only lineage is
recorded separately and never increments a product count.

## Item mapping

Every catalog entry retains its exact ordinal, task identity, closure, non-closure, phase,
deferred kind, test inputs and decision-gate requirements. It resolves through the current
coverage ledger to the exact current story, reachable commit, independent review and test
claims. Rows 1–281 must already resolve. Row282 resolves to the candidate adoption story.
Row283 remains an audit-only `FINAL_CLOSE_PENDING` entry and is not represented as product
completion.

Each external product node has a frozen explicit mapping to one or more current accepted C3
stories. The contract verifies that every mapped story exists, is `CURRENT_VERIFIED`, has a
reachable commit, has the required independent review and owns current product/test paths
that implement the external node. Representative catalog rows and name-based inference are
not accepted.

## Evidence and residuals

The output records exact current story references instead of copying mutable business facts.
Per-item evidence is therefore the story commit, tree fingerprint, review/verification ref,
test claims, catalog gate requirements and current residual.

The two customer-owned production inputs remain:

- `DG-PAYMENT-WORKBOOK:GLOBAL = CONFIG_REQUIRED`;
- `DG-SERVICE-RATE-VERSION:GLOBAL = CONFIG_REQUIRED`.

Their decision registry rows remain `PENDING`; production attempts remain `409 / NO WRITE`;
TEST_ONLY stays isolated. These are explicit configuration residuals, not product defects and
not blockers for capability or ledger closure.

## Historical overlay replacement

The four Delta controller/overlay families and historical G1/G2 gates remain audit lineage.
Their taskctl/atomic-artifact commands are not rerun or extended. Current acceptance instead
binds the immutable catalog hash, the reviewed terminal dependency overlay and hashes, the
current C3 coverage ledger, the Row281 inherited matrix, a candidate Git commit, independent
High review, focused tests, scoped Ruff and lean inventory validation.

## Files and acceptance

The Row282 closure owns only:

- the frozen Row282 task card;
- this design;
- `docs/product/v8/final-item-slice-ledger.json`;
- `docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md`;
- `backend/tests/test_v8_final_item_slice_ledger.py`;
- the reviewer receipt;
- the single coverage-ledger adoption.

No product source, migration, schema, customer registry, Row283 task, release command or
historical evidence machinery is edited. An independent High reviewer must approve exact
candidate bytes with P0/P1/P2 `0/0/0` before the Row282 ledger adoption is committed.
