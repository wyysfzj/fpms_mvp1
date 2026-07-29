# Independent Review — V8 Official Fee Category Correction Current Adoption

- Review class: `PROTECTED`
- Exact range:
  `bd1b60344dc2cc65da593f2fddb7f2ffcf18fcf7..bca7de8f05505ee4eb3103ee95161a627436efa1`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High lane verified frozen catalog row `158` against its exact task
contract. The reviewed range is one story-only commit. The seed and focused-test files are
unchanged from the base and archive checkpoint:

- seed blob `82a58ec0035cb97116a4303f9d14e956972ac841`, SHA-256
  `b9867318c9e24742a56bd3607ef7048f07153672446876e8d85b6c4de48ae928`;
- test blob `a217312c52de64d5105372fd998b2119bd57ca4c`, SHA-256
  `fa10d9f37cca9f6a4113b27f09624a1706b6c2f81f6d148628b572051b1c0c16`.

The current seed preserves the established `CN_PUBLICATION_PRINT_FEE` code, row identity,
`created_at`, and history while applying only the frozen classification: `公布印刷费`,
`仅发明专利`, `不可费减`, and `allow_reduction=False`. It does not absorb row `88`, another
dataset, API/UI behavior, schema/migration, source activation, adjacent fee logic, or a
broader fee-reduction rule.

The controller and independent reviewer each ran the focused test once; both observed
`1 passed` with only the existing third-party passlib `crypt` deprecation warning. Scoped
Ruff, exact-range diff-check, seed/test zero-diff checks, and worktree cleanliness passed.
The exact-range patch SHA-256 is
`c5e0f9531494c00ef471a2eda7ebe991e24e09687995b58056d59659953b9927`.
