# Independent Review — Filing XML Derivation Gate

- Review class: `PROTECTED`
- Product commit: `ef938aa`
- Ownership correction: `c11ac99`
- Final reviewed range: `7fbbc4b..c11ac99`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified the exact six-argument policy, both frozen lineage
paths, ordered fail-closed error precedence, read-only behavior and non-goals. The
reviewer's decisive focused run passed all `196` tests with one inherited warning. The
controller's serialized focused plus noncopyable-OA-appendix regression passed all `347`
tests; scoped Ruff and diff checks passed.

The initial review found one P1 ownership-accounting defect: the two disposition entries
had moved but the aggregate story counts were stale. The exact successor correction
changes only those counts and the story's recorded disposition hash. Mechanical re-review
proved all `474` paths remain unique and the aggregate counts exactly match the entries.

The exact product/test tree fingerprint is
`99726ebb0c6cf31a3c6353262b71f05a461fb560f70c8b732123bebfa5b28865`.
The final binary patch SHA-256 is
`9a342668e91d87cc05faf005b441e73184b637dddfc774c7715ac0298bcda383`.
The disposition SHA-256 is
`328467f45b5b1e15ff3ee5cc41ab635b1c5ae9d4c299a9d06216c3b1b3c552d0`.
