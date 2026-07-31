# Independent Review — Legacy Fee-Reduction Import

- Review class: `PROTECTED`
- Product commit: `897eee8`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified the exact public seam and byte-exact `0`, `0.7`,
`0.85` grammar; approved-manifest hash, actor and naive-time authority; deterministic
case ordering, canonical hashes, classifications and all nine count keys; and a write-free
dry run.

Apply recomputes and validates the exact plan before mutation and performs no internal
commit, rollback or savepoint. It changes only the case projection and immutable
provenance. Explicit zero forbids approval, while a nonzero value requires exactly one
fully matching confirmed current-evidence approval and never creates one. Exact replay
remains unchanged and changed same-identity provenance fails closed with `409`.

The focused GREEN passed `14/14`; scoped Ruff format and check passed. The reviewer did not
repeat the serialized SQLite test. Both reviewed files matched their assigned hashes.

The exact product/test tree fingerprint is
`804e5bea5f352005c583378d79044075b0d78840cdbd937ea11b298e56a218f3`.
The complete product commit patch SHA-256 is
`4d79e764430a7f4f3c87e1dd20cd5eceea1d5111241ccd311b0598e82f74220b`.
