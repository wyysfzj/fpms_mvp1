# Independent Review — Generic Fee-Draft Obligation API

- Review class: `PROTECTED`
- Product commit: `d494e95`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified one nullable `obligation_id` and exact pass-through
to the accepted service. Omitted or null input retains the historical service-owned
transaction. Linked success invokes the service once, then commits and refreshes once at
the API boundary.

Missing obligation preserves its business code, message and details while remapping
`404` to the frozen `409`. Non-actionable and mismatched linkage remain `409`. Every
business or unexpected failure rolls back, with no refresh, partial draft/link/activity or
duplicate activity append. Route, `201`, direct response, permission and envelope behavior
remain unchanged.

Focused GREEN passed `9/9`; scoped Ruff and diff checks passed. The reviewer matched the
three exact candidate hashes without repeating serialized SQLite testing. A read-only
successor attestation approved the fee-reduction approval API, fee-obligation HTTP/FE and
fee-estimate preview stories sharing these source files.

The exact product/test tree fingerprint is
`cc345e2d6801574f39ee0d4ff00ce070f7a9e146fa4547778cbd7a979b3e9554`.
The complete product commit patch SHA-256 is
`a99244a5a423e799e27dd52e200c751b7679176054db7b5a75421769f33618d3`.
