# Independent Review — Legacy Fee-Truth Link

- Review class: `PROTECTED`
- Product commit: `f7ee133`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified deterministic dry-run and exact-plan apply, exact
case/source/fee/year/domain authority, caller-owned transactions, idempotent draft/payment
linking and the absolute prohibition on manufacturing an obligation.

The review found three defects before approval. Apply originally skipped unresolved rows
and could partially migrate a mixed plan; payment order lacked an identity tie-break; and
one fee item could resolve to different obligation lines within one batch. The final
candidate rejects any unresolved plan before writes, canonicalizes multi-payment ordering
and hashes, and reserves exactly one obligation-line authority per fee item. Conflicting
source/payment authority becomes `AMBIGUOUS` and fails the whole apply.

Focused final GREEN passed `9/9`; scoped Ruff and diff checks passed. Final read-only review
matched both exact blobs and approved with P0/P1/P2 all zero without repeating SQLite.

The exact product/test tree fingerprint is
`6c496477e43cc77d1f71da8ee651b5810d182b717d5f4b10ed91746d9ae29e9e`.
The complete product commit patch SHA-256 is
`9e66935212cb82109cb41d51885ca8ee65002f9e796d13a17b88f6b0e9784ffc`.
