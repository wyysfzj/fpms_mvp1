# Story V8 Grant Draft Obligation Adapter Current Adoption

- Risk: `PROTECTED`.
- Catalog owner: Row120
  `FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`.
- Product commits: `6f17cae`, `5d84f8a`, `b91f37f`.
- Prerequisite: `V8-GRANT-OFFICIAL-FEE-MANUAL-REVIEW-CURRENT-ADOPTION`.

The typed service adapter resolves one explicitly named grant task and confirmed grant-notice
activity through the exact current manual-review lineage, then delegates once to the accepted
generic draft writer. It returns the generic draft, link, activity, replay and idempotency
identities without creating substitutes or mutating the legacy task.

The adapter-owned savepoint validates every resolved obligation line against the complete
persisted draft-link set, items, canonical activity payload, explicit PAY instruction and exact
activity key. It preserves caller rollback on SQLite, treats post-delegation identity drift as a
409 lineage conflict, supports exact multi-line and replay paths, and does not create a PayList,
payment, fee fact, lifecycle transition or second activity.

Final focused verification passed 7 tests. The exact inherited grant, generic draft, annuity
draft, obligation-detail and overlay tranche passed 198 tests. Scoped Ruff and diff checks passed.
The first independent review found four P1 gaps; the correction review confirmed all four closed
and approved the final commit with P0/P1/P2 all zero.
