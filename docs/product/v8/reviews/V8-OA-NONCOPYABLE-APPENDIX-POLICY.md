# Independent Review — OA Noncopyable Appendix Policy

- Review class: `PROTECTED`
- Effective range:
  `e1957b3d77e4f54f20a695823b857bc25790ba82..d7150cafd4d0dc4ccd19d1abeab78ec0798b9f01`
- Rejected implementation commit: `d66ab96cee2878215d3a9ac81d7390b75ab6e5b1`
- Accepted correction commit: `d7150cafd4d0dc4ccd19d1abeab78ec0798b9f01`
- Supersedes the shared-file owner for catalog row 72 and closes row 73.
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The first independent review rejected the implementation because its nominally valid
fixture used non-current carriers and a forbidden `GENERATED_ATTACHMENT/FINAL` parent,
while the policy omitted version/current, state and review-tuple validation. The correction
retains that rejected commit as durable history and closes the exact finding.

The accepted policy now requires positive version ordinals and exact current identities,
a `GENERATED_ATTACHMENT/DRAFT` parent with no final submission, and an
`OA_STRUCTURED_ATTACHMENT` child in `DRAFT|FINAL`. Coherent `PENDING`, `APPROVED` and
`REJECTED` review tuples are accepted; malformed and self-reviewed tuples fail closed.
It deliberately does not require approval, preserving row-72 and prepare-seam ownership.
All existing error surfaces and the no-mutation boundary remain unchanged.

The reviewer reconstructed the correction RED at 41 failed and 110 passed, then
independently observed 151 row-73, 34 row-72, 20 derivation and 40 D4-08 tests pass.
Scoped Ruff and both correction/effective-range diff checks passed. The row-72 function
remains byte-identical and the worktree was clean.
