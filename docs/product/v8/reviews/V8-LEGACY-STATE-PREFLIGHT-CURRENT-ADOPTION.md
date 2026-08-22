# Independent Review — Legacy State Preflight Current Adoption

- Review class: `PROTECTED`
- Contract commit: `1b16956e72a23515651d18361fe86ce6c9e1ea8a`
- Product/test commits: `71b219f6c90ee968aa16fcc0be0a320b78d1216b`,
  `1d219f5ad465ee45ce904c6adadcadf84ed02411`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified the exact public DTOs and keyword-only synchronous
service, one-way lifecycle projection, per-row invalid-carrier handling, legacy `GRANTED`
fail-closed boundary, row-254 dry-run attachment classifications, stable ordering/counts,
canonical report hash and caller-owned read-only transaction behavior.

The review confirmed that only confirmed LIFECYCLE activity can supply the latest event
type and OA sequence. The focused correction adds a higher-sequence confirmed FEE activity
alongside the existing DOCUMENT and unconfirmed-LIFECYCLE distractors and proves that none
can alter the selected lifecycle fact or the resulting `OA2` projection.

The final focused test passed `18` tests with one inherited passlib `crypt` deprecation
warning. Scoped Ruff passed. The implementation opens no engine/session and performs no
add, delete, flush, commit, rollback, close, reverse mapping, status assignment, activity
append or evidence import.

Exact current path fingerprints:

- `backend/scripts/audit_v8_legacy_state.py` SHA-256:
  `ee2f3e8237bdfa4f67ac683993dda3955c044a3569b1d15452d22ec0f4742911`
- `backend/tests/test_v8_legacy_state_preflight.py` SHA-256:
  `563ab0c1b82c5f9edc9ff92f0eaef0cc4794dae319f79f0cb59ca94be822d3ba`
- Git tree fingerprint for both owned paths at `1d219f5`:
  `c1472baee38609663b399e6fd31115cfe0d61f7ae88f2287623bfbb4925338cd`
