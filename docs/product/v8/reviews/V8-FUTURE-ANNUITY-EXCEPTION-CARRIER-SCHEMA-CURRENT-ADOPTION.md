# Independent Review — Future-annuity Exception Carrier Schema

- Review class: `PROTECTED`.
- Reviewed commit: `af6113df03e809475f22c05f36cf9c5b4ccf33e0`.
- Task SHA-256:
  `2f29ec9e4815467cb6281cea1c5519c2e62b880e9d8b70c3915dcca813abd1b8`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact three-path candidate adds only the empty, append-only future-annuity draft-exception
publication/revocation carrier authorized by Scheme A. It preserves the default rule that client
instruction is required: there is no default, wildcard, open-ended or production exception, and
no service, API, draft, fee, payment or legal-state behavior.

Migration and ORM expose the exact 19 ordered columns, three uniques, four `ON DELETE RESTRICT`
foreign keys, three fail-closed checks and three interval/target indexes. `PUBLISHED` and `REVOKED`
shapes are exclusive, the snapshot hash is lowercase hexadecimal, and ORM update/delete attempts
raise the exact append-only error.

Fresh independent verification passed: focused schema pytest `4 passed`, scoped Ruff passed,
Alembic reported exactly `v8_future_annuity_exception_01 (head)`, a clean temporary SQLite
upgrade/current reached that exact head with zero carrier rows, and exact diff checks passed. The
exact three-path Git tree fingerprint is
`e085c1154718aa666ed6b801e4ce9d7517ba86a2db6bf634ba3c3da1b8963fbd`.
