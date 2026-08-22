# Independent Review — V8 Overlay Document Join

- Review class: `PROTECTED`
- Product commit: `0ea0d143549fadfd57cfcf6fd44b8e78f1f8bac1`.
- Test correction: `0cb1cd76d2c7c8216aba2a7ef90495c65b1a1138`.
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High reviewer verified exact activity-rooted associations, deterministic
projection, once-per-package evaluation, no writes and no fee/decision/pagination absorption.
The correction proves 409 fail-closed behavior for cross-case selected versions, direct and
receipt-owned packages, manifest-selected packages, derivation endpoints and corrupt evidence
roles. The service bytes did not change during the correction.

Fresh document plus center verification passed `24` tests. Scoped Ruff, format and complete
range diff checks passed.

The exact final product/test tree fingerprint is
`a1a1eb124b48e0d48a9a68353f77fe7b6ad0e32f7519d4586ec3bdf99618b261`.
The complete product-range patch SHA-256 is
`e1c946a58c7e2acb23bc23b328639b3448e0ec73d401be2adeecd91f38550da5`.
