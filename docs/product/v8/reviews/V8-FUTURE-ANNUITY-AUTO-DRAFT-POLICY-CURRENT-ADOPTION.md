# Independent Review — Future-Annuity Auto-Draft Policy Current Adoption

- Review class: `PROTECTED`.
- Frozen authority range: `bf820da..a532744`.
- Product range: `a532744..77e32f5` (product commits `4d71dbf`, `3133d60`,
  `77e32f5`).
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The implementation preserves instruction-first as the default and creates one pending, unpaid
internal future-annuity draft only when the exact Scheme A GLOBAL gate and one current, audited
client- or case-scoped exception are both usable. It binds the exact annuity task, obligation,
year, due date, official fee code, source activity, document, approved current evidence and
canonical recognition activity. No PayList, GovPayment, payment evidence or inferred client
instruction is created.

The deep service independently validates the exact task key, complete graph, canonical
`sha256:<64 lowercase hex>` evidence hash, gate/publication snapshot and exception applicability.
Fresh SQLite creation acquires `BEGIN IMMEDIATE` before current-authority reads. Missing nodes
preserve 404; corrupt, ambiguous, mismatched or partial state is 409. Historical replay uses the
persisted attestation after later expiry or revocation, while later explicit `PAY` reuses the same
draft and `HOLD`/`ABANDON` remain fail-closed.

Fresh controller and independent verification passed 27 focused/contract tests and 150 affected
regressions. Scoped Ruff, both exact range diff checks and the five-path allowlist passed. The
independent final review specifically closed fake-task deep binding, missing-recognition status,
mutually corrupted evidence hashes, malformed historical timestamps and the complete protected
acceptance matrix.

Exact fingerprints:

- cumulative product patch SHA-256:
  `ec4ec003702945009290eb5b26c90685acf29b48c1be96751e952af223eab8e8`;
- five-path Git tree SHA-256:
  `96619820fdce09d753796bb0a47295b90bc2c89dcef27c16426bc2a9a7179da6`.

The pre-existing untracked `backend/uv.lock` is outside this story and remains untouched.
