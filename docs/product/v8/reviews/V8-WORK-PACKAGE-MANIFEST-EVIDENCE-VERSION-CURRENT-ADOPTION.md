# Independent Review — Work-Package Manifest Evidence Version

- Review class: `PROTECTED`
- Product commit: `749eb1d`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The first independent review found one P1: the candidate persisted
`evidence_version_id`, but the output schema and projection did not return it. The current
story card froze the minimum schema/service/test correction required by the existing
“writes/reads evidence-version identity” closure.

The corrected implementation binds exactly one attachment-scoped evidence version,
returns that same identity, preserves null identity for legacy attachment-only rows, and
fails `409` before ambiguous selection when more than one version exists. It introduces no
fallback or adjacent evidence policy.

The focused RED failed exactly at the missing identity. Final focused GREEN passed `1/1`;
scoped Ruff and diff checks passed. Independent High re-review approved the three exact
candidate hashes and confirmed the shared service left accepted row-70 lifecycle and
row-71 receipt-derived reply-date behavior untouched.

The exact product/test tree fingerprint is
`af35586a8f9706953df0e003f90ff425b5ab7e29603f8074677c9e3bd65541cc`.
The complete product commit patch SHA-256 is
`4935ea4bfe4a83fbda4a757fe8ad8265442c956cef1f5d961f3e5489ca630982`.
