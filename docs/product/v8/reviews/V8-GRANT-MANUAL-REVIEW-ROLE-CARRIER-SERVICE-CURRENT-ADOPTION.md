# Independent Review — Grant Manual-review Role Carrier Service

- Review class: `PROTECTED`.
- Reviewed story range: `0fe4fd5^..017fef8`.
- Final correction commit: `017fef85af1792bcc6c57d881498b02eb7bbc535`.
- Task SHA-256:
  `14610c29a8803365b403e0003af4c994340c638be663254e7985bc6d310b270c`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path candidate publishes, resolves and revokes only the five institution-configured
Scheme A duty roles. It creates no role, user, membership, permission, seed, default or fallback.
Publication and its replay require the exact current customer gate at `published_at`, a canonical
predecessor chain, five usable role bindings and feasible distinct actual-user pairs. Resolution
revalidates those conditions at `as_of`; a missing, future, expired, revoked, corrupt or
personnel-incomplete configuration fails closed without an older-row fallback.

Revocation copies all five role IDs from the exact active predecessor and remains available when
memberships have become unusable. Both write operations use expected-current CAS and one nested
savepoint, while the caller retains commit, rollback and close ownership. The service records no
operational evidence and changes no legal state, lifecycle, deadline, document, fee or payment
fact.

Fresh independent verification passed: focused pytest `24 passed`, exact role-schema and
decision-gate regressions `55 passed`, scoped Ruff passed, and exact range diff-check passed. The
exact two-path Git tree fingerprint is
`6262f36bc68c044b0c2367209b35c087c5975606a479e4f81478ea689a7e5475`.
