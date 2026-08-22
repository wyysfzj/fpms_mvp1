# Story V8-OVERLAY-KEYSET-REVISION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Contract commit: `4902d7c`.
- Product/test commit: `82baf4f`.
- Catalog ID: `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01` (ordinal `264`).
- Outcome: paginate only overlay milestones with a stable sequence keyset at frozen revision `R`.

Full history remains validated through `R`; only the returned milestone slice applies
`after_sequence`, `sequence <= R` and `limit + 1`. The extra row determines `has_more`, and the
last returned sequence becomes `next_cursor` only for a nonterminal page. Rows appended after the
first page's `R` stay excluded. Every page independently retains its complete ordered 29-gate
snapshot.

The focused RED returned all 121 rows. GREEN traversed exactly three pages without gap/duplicate,
proved terminal/empty cursors and post-freeze exclusion, and preserved predecessor behavior after
the one authorized old-limit invocation migration. Final regression verification passed 66 tests;
scoped Ruff, format and diff passed; independent High review approved P0/P1/P2 all zero.

No alternate cursor, decision resolver, fee/document behavior, endpoint/UI, schema or adjacent
change is included. Rollback reverts the one product/test commit and this adoption.
