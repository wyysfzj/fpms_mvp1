# Independent Review — Grant Evidence Candidate Read Service

- Review class: `PROTECTED`.
- Reviewed story range: `8311c87..7212683`.
- Implementation commit: `72126838a8032863bc445a5dcb2612fbb6e42815`.
- Task SHA-256:
  `38391da6529742b3cbd10c94a9bd45304e39bbefba2a9836e1df5493956cfd38`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path read projection requires the confirmed source decision at read time, distinguishes
a missing document from an existing document with no candidates, and orders rows deterministically.
It recomputes exact V2/V1 canonical bytes and hashes, binds acquisition and candidate snapshots to
their persisted columns, validates terminal and role identities, preserves raw ordered facts and
conflicts, and fails closed on any invalid review tuple or divergent persisted state.

The service uses a clean caller Session under `no_autoflush` and performs no flush, commit or
rollback. It does not query a current source, substitute historical authority, infer legal status,
choose a conflicting value or change any product fact.

Fresh verification passed: focused read-service pytest `7 passed`, ingestion/source regressions
`73 passed`, scoped Ruff and the exact two-path diff-check passed. Independent High review approved
`P0/P1/P2 = 0/0/0`. The exact Git tree fingerprint is
`a1315485bdba67d3d3d9881e4d15de9f85ffeb0e680fa104e1bf47c23db3c15d`.
