# Independent Review — Grant Official-copy Verification Service

- Review class: `PROTECTED`.
- Reviewed story range: `1d24915..3338a6e`.
- Implementation commit: `3338a6e4883cddbcc9e989c07211794d72bb003d`.
- Task SHA-256:
  `c9908546bf05cf4fb7c508f16c556201018eff969c00e1d2dc8aaace7441fc80`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path story records only the official-copy acquisition, first-verification and
second-verification lineage. Every action resolves the accepted CNIPA source and institution duty
configuration, requires an active actor in the exact configured stage role, and binds canonical
source, evidence, role, actor, time, reason and predecessor bytes. The first and second verifiers
must be different actual users; no additional separation rule is invented.

The service requires one current immutable FINAL raw-attachment evidence version, preserves the
acquisition source across the chain, allows audited role configuration to resolve per stage, and
uses expected-current CAS plus a nested savepoint. Exact replay is fail-closed and caller-owned
rollback remains effective. It creates no candidate and changes no evidence/document, case legal
status/lifecycle, deadline, fee or payment fact; terminal second verification is not grant
confirmation.

Fresh independent verification passed: focused service pytest `20 passed`, scoped Ruff passed and
exact range diff-check passed. The controller additionally observed `73 passed` across the source
resolver, role resolver and carrier-schema regressions. The exact two-path Git tree fingerprint is
`ab52d8537c70bd103e9676c6048b8281436227c152f9bbf661839dbf080fa912`.
