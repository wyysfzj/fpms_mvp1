# Independent Review — Patent Register Evidence Adapter

- Review class: `PROTECTED`.
- Product commits: `5cc1127c047e182845e941c02eae2483c05a0184`,
  `ae2869851184b98c711de4fe44f73947c9cb9bcb`, and
  `69b61a0a72d8109da2ed5b6f042f5a4d0ac3fb8b`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The adapter accepts only a previously approved, source-bound patent-register candidate whose
proposer and second reviewer are distinct active users under the exact Scheme A role and source
configuration. `PATENT_IN_FORCE` is sent to the generic register event for same-status
verification or the deep rule's restoration-required conflict. `PATENT_TERMINATED` and
`PATENT_EXPIRED` are sent only to their dedicated legal events with the register evidence.
`PATENT_INVALIDATED` fails `409` before dispatch because this candidate does not contain the
separately required effective invalidation-decision evidence; the adapter never fabricates it.

The final independent High review approved the cumulative two-path candidate with zero findings.
Fresh verification passed 18 focused adapter/direct-status tests, scoped Ruff and the exact
cumulative diff check. Authority absence, revocation, future activation and scope mismatch all
produce `409` with no lifecycle dispatch. The cumulative patch SHA-256 is
`e374259935c4da636da04ea09db74b6b5522bfff88c2a7da9c5e47078b2a6b0f`; its exact two-path Git
tree fingerprint is
`5aa899afddfd5f464635998e851517337a4aacb29170d36f69d2c3c17ee03f75`.
