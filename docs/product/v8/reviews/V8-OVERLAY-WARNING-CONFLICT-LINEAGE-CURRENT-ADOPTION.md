# Independent Review — V8 Overlay Warning Conflict Lineage

- Review class: `PROTECTED`.
- Contract commits: `21509b1`, `0b88da6`, `98d741c`, `931983b`.
- Product commits: `850422a`, `afb7bd6`, `2896860`, `edf47dc`, `40ed8ed`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

Independent review required four correction rounds. The accepted result now reads attestation
columns directly from persistent storage under `no_autoflush`, covers stale and dirty identity-map
states, closes SQL NULL/check-shape ambiguity, and proves each material migration near-miss. The
warning axis proves all 29 unresolved gates, shared `ALL-22` carrier provenance, historical and
internal-only classification, needs-review and non-legacy conflicts, page-local replacement, and
the complete corruption matrix.

The final legacy boundary additionally requires canonical string status, the exact immutable
import shape and the first lifecycle event in the full frozen ledger even when that event lies
outside the requested page. Malformed and later look-alikes retain ordinary warning visibility but
never acquire legacy-conflict authority.

Fresh independent focused runs passed 11 tests and 8 tests respectively. Scoped Ruff and full
candidate diff checks passed. Exact final tree fingerprint:
`61ffc0954f72f1932b43b39d9a15de9af8c175e8554e1afbf58bb7a65565c96a`.

The fingerprint includes the reviewed successor contract and its exact authoritative
`domain-contract.md` clauses, closing the former ledger omission without changing those bytes.
