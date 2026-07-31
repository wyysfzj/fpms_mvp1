# Independent Review — V8 Prepare OA Reply Seam

- Review class: `PROTECTED`
- Full exact range:
  `434378756fe02a937b32127dbbe5605b8fad7c3d..bfa42b9a5a4b0393837345a48f9d199c0891fd86`
- Fix range:
  `f27a1da5d80c1ab79d203559659dbdc8b153b741..bfa42b9a5a4b0393837345a48f9d199c0891fd86`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The initial independent review rejected the candidate because lineage-version and
preparation-derivation queries filtered on the requested case before evaluating all exact
lineage, parent and child carriers. Cross-case rows could therefore be hidden from fresh
or replay cardinality.

The reviewed fix loads the complete exact lineage set and the complete exact parent/type
and child/type derivation sets before checking wrong-case identity, multiple closure,
cardinality and same-row identity. Public-seam regressions cover fresh and replay
cross-case versions and both cross-case derivation edges. No schema, model, API, router,
fee, lifecycle transition or external-submission behavior entered the closure.

The independent re-review ran the focused row-48 file once: `41 passed, 1 warning in
10.65s`. It then ran the exact six-file predecessor/policy tranche once: `269 passed, 1
warning in 64.89s`. Both warnings were the inherited passlib `crypt` deprecation. Scoped
Ruff, format-check, full/fix diff-check and worktree cleanliness passed.

The exact four-path Git tree fingerprint is
`ac40c207fce7391c2f99aee4989397eefd8b160832399a97cabcfa064c6f0967`.
The full binary patch SHA-256 is
`865d432d1b90b4577bf5d8e3c57a565385cb106ea24e3109a4fd797a3ca8e000`;
the fix-only patch SHA-256 is
`f43dd8fd76ca82de2f93c219d7c0393ac05a369850471a1cbd1438cc5f038e83`.
