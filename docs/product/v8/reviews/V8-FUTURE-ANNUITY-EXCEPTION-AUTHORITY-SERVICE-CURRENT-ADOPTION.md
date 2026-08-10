# Independent Review — Future-Annuity Exception Authority Service Current Adoption

- Review class: `PROTECTED`.
- Frozen task commit: `e49313f`.
- Product range: `e49313f..88016f0` (product commits `088f62f`, `893489d`, `88016f0`).
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The service publishes, revokes and resolves only explicit client- or case-scoped future-annuity
draft exceptions with mandatory half-open time bounds. The default remains instruction-first. The
exact current GLOBAL Scheme A gate and `SystemParam.Edit` permission are mandatory; no missing,
historical, wildcard or inferred authority is accepted.

Independent review found two concurrency gaps in succession. First, overlap checks could run before
SQLite write serialization. Second, the decision gate could change after its initial read but before
serialization. Commits `893489d` and `88016f0` close both gaps: mutation serializes before authority
carrier reads and re-runs the exact gate resolver at the same time after the lock. Deterministic
two-session tests prove overlapping publication cannot double-write and concurrent gate revocation
cannot authorize a stale write. Accepted decision-gate errors remain unwrapped.

Fresh focused verification passed 11 tests. The inherited carrier, gate-read and system-parameter
tranche passed 62 tests; one carrier test was excluded because its pre-existing migration-head
assertion still names `v8_future_annuity_exception_01` although accepted later migrations place the
repository at `v8_grant_official_copy_01`. This story changes neither migration nor inherited test.
Scoped Ruff and exact two-path diff checks passed.

Exact fingerprints:

- cumulative product patch SHA-256:
  `cbbdc979862f82f2c031f4154da4ec91e31b4fe95e180b30f51d635c0d984f20`;
- two-path Git tree SHA-256:
  `57a3e5e2851d5d51b3d3d8fc3ed0c71e27ff2236acb87d8b381c6c5061ec52c1`.

The pre-existing untracked `backend/uv.lock` is outside this story and remains untouched.
