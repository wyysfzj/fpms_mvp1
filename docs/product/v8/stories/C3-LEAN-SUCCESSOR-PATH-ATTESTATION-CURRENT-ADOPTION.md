# Story C3-LEAN-SUCCESSOR-PATH-ATTESTATION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: preserve every story's immutable reviewed snapshot while validating each current
  shared path against its unique latest accepted owner.
- Contract:
  `docs/product/v8/stories/C3-LEAN-SUCCESSOR-PATH-ATTESTATION-CONTRACT.md`.
- Product commits: `6e6b1e8dc4a61c5b65129d1fb55ae511968b8d4a` and exact
  commit-reference canonicalization correction
  `5965e1fb6533d75f2adb7d8af4a6042413abf0d3`.
- Catalog IDs: none; this is a correction to the C3 stateless milestone checker.

## Observable contract

Every current-verified story still requires reachable commits, required independent review
and an exact whole-story fingerprint at its final reviewed commit. For a path shared by
multiple accepted stories, Git ancestry identifies the unique latest reviewed owner and
the integration tree must match that owner's exact Git entry. Linear reviewed successors
therefore remain valid, while unreviewed later drift, incomparable owners, absent paths,
unreachable commits and incorrect historical fingerprints fail closed.

No catalog disposition, review class, milestone rule, dirty-path quarantine or release
ordering changed.

## Verification and review

The focused RED produced two failures: the checker rejected a valid linear reviewed
successor and reported the earlier owner instead of the unreviewed post-successor drift.
The minimum implementation made the full checker suite pass `11` tests. Scoped Ruff,
format and exact diff checks passed.

Independent High review inspected the exact algorithm, review/reachability preservation,
unique maximal-owner rule, incomparable-owner failure and present boundedness. A real-ledger
probe then exposed full and abbreviated names of the same commit; the minimum correction
canonicalizes both with Git before owner grouping and adds an exact regression. Independent
re-review passed all `12` tests and approved the final candidate with
`P0/P1/P2 = 0/0/0`.

## Non-goals and rollback

No product, catalog row, customer/source decision, acceptance receipt or milestone was
changed by the implementation. Rollback reverts the exact checker/test commit and this
adoption record.
