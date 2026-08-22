# Independent Review — V8 Case Fees Instruction UI

- Review class: `PROTECTED`
- Product commit: `1420fb8`.
- Verdict: `APPROVED`
- P0/P1/P2: `0/0/0`

Independent High review verified that actions exist only for persisted obligations, the request
body is exactly `{ instruction, idempotency_key }`, transport retries reuse the same key, terminal
responses retire it, and different instructions create separate attempts. Results and normalized
errors remain distinct from overlay truth. Only a returned `PAY` result exposes an explicit draft
link using the returned obligation ID; no automatic retry, navigation or adjacent mutation occurs.

Fresh verification passed the three focused tests, five Row267 regression tests and all eight in a
combined serial run. Scoped ESLint and diff checks passed; typecheck retained only five unrelated
baseline diagnostics.

Exact final tree fingerprint:
`55d865421d48f0cab4e3e3546dc0c54f033e644e06b878dca367428072ca2ac8`.
