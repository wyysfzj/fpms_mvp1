# FPMS V8 Final-Matrix Remediation Current Adoption

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Adopt the exact current bytes produced after the Row282 ledger adoption while repairing the one
attempted Final matrix. Bind the cumulative range from `e6a0440c2823b4ce4a49cfd8e155b5746083775b`
through the adoption candidate: exactly 84 pre-existing changed paths plus this task, its focused
contract and current-adoption story, for 87 exact fingerprinted paths.

## Authority and closure

Every behavioral/test-alignment commit in the cumulative range has its own atomic task and
independent High review. This adoption adds no behavior. It gives the latest accepted integrated
bytes one current ledger owner so lean inventory can pass before Row283. The exact 84-path sorted
manifest SHA-256 is `3261ce65b64a2cc44855daa7be907c8434e10c755460d5205f77c5cd180b3c29`.

## Non-closure

No existing product/test/design/plan/task byte change; no schema/migration/seed/catalog/matrix/
Final report/Row283 row change; no broad matrix rerun or release claim. Row283 remains the only
PENDING catalog row. Production inputs remain CONFIG_REQUIRED/PENDING with 409/NO WRITE and
TEST_ONLY isolation.

## Exact allowlist

- the 84 exact paths in `git diff --name-only e6a0440c2823b4ce4a49cfd8e155b5746083775b..3f3177c4d234207ca4b752c3807e4ed933ff1fb6` are fingerprint inputs only and remain unchanged;
- `tasks/postdemo/v8/FPMS-V8-FINAL-MATRIX-REMEDIATION-CURRENT-ADOPTION-20260813-01.md`;
- `backend/tests/test_v8_final_matrix_remediation_adoption.py`;
- `docs/product/v8/stories/V8-FINAL-MATRIX-REMEDIATION-CURRENT-ADOPTION.md`;
- reviewer-owned `docs/product/v8/reviews/V8-FINAL-MATRIX-REMEDIATION-CURRENT-ADOPTION.md`;
- sole later adoption patch `docs/product/v8/coverage-ledger.json`.

## Verification and adoption order

Run the focused contract, scoped Ruff, JSON parse, exact diff and lean inventory at the candidate.
Independent High review audits the cumulative 84-path range, exact 87-path fingerprint and sole
ledger patch, then commits only its receipt. Controller commits only the reviewed ledger patch.
Independent acceptance requires P0/P1/P2 `0/0/0` before Row283 resumes.
