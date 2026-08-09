# Story V8 Overlay Live Fixture Current Adoption

- Risk: `PROTECTED`.
- Product commits: `89375d9`, `fbf87f6`, `b07a4ac`.
- Catalog owner: `FPMS-V8-LIVE-FIXTURE-20260712-01`.

The dedicated dev/test/demo SQLite seed owns one deterministic `V8OVL-LIVE` namespace,
uses the sole global fixture lock, and leaves the shared P1 fixture untouched. It creates a
namespaced inactive actor, 401 ordered activities across lifecycle, document and fee lanes,
durable legacy conflicts and unverified facts, and the exact 29-entry decision-gate matrix.
Direct and `ALL-22` fallback provenance remain distinct; unresolved rows fail independently;
historical and internal-only rows remain reference-only and never activate customer policy.

The seed fails before mutation for unsafe environments, non-SQLite binds, disabled foreign keys,
foreign current-identity ownership and lock contention. Cleanup is namespace-limited, failures
roll back atomically, sessions close before lock release, and reruns are logically idempotent.

The original RED proved the missing dedicated fixture. Final focused verification passed four
tests, scoped Ruff and exact diff checks passed, and independent High review approved the exact
candidate with P0/P1/P2 all zero.
