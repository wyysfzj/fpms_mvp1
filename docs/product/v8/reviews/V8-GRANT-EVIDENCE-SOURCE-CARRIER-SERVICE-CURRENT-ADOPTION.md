# Independent Review — Grant-evidence Source Carrier Service

- Review class: `PROTECTED`.
- Reviewed range:
  `7955b90bf5fb9fd6355fcf07337e45422d597572..18e9e2ef6ede30f0436a83513458290fb867a074`.
- Task SHA-256:
  `954960141ba75465176b01ab262a257d9b9128ab70303453173db7483429c502`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path candidate implements only the frozen publish, revoke and current/effective
resolution service for the institution-configured CNIPA grant-evidence source carrier. It keeps
Scheme A configuration-required: no source, source version, institution configuration, role,
user or fallback is seeded or inferred. Missing, stale, revoked, future, malformed, ambiguous or
lineage-inconsistent authority fails closed before any legal-state or lifecycle change.

The final independent High re-review confirmed that revoke replay revalidates the exact linked
source and predecessor canonical lineage and that the complete frozen proof matrix remains
confined to the two owned paths. Fresh independent verification passed: focused service pytest
`45 passed`, decision-gate regression pytest `51 passed`, scoped Ruff passed and the exact
two-path cumulative diff check passed. The exact two-path Git tree fingerprint is
`706ee61d41f9c627ae56993c66e812ab21dd377e454467b9a8bdc95d54e639b5`.
