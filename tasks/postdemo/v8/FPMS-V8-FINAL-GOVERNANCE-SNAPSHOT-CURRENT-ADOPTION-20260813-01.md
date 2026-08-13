# FPMS V8 Final Governance Snapshot Current Adoption

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Exact Closure Slice

Adopt the exact independently approved three-path governance snapshot alignment commit
`b77c743e2f83883ecf97ff5111e5179aabd3af0f`. Bind those three paths plus this task,
focused contract and adoption story, exactly six fingerprinted paths.

## Explicit Non-Closure

No existing product/test/task/report/Row283 candidate byte change; no schema/migration/seed/ledger
row/release claim. Row283 remains the sole PENDING row and retains ownership of its separate five
candidate paths. Production remains `CONFIG_REQUIRED / PENDING / 409 NO WRITE`; TEST_ONLY is
isolated.

## Allowed Files

- the exact three paths in commit `b77c743e2f83883ecf97ff5111e5179aabd3af0f` are fingerprint inputs only;
- `tasks/postdemo/v8/FPMS-V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION-20260813-01.md`;
- `backend/tests/test_v8_final_governance_snapshot_adoption.py`;
- `docs/product/v8/stories/V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION.md`;
- reviewer-owned `docs/product/v8/reviews/V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION.md`;
- sole later adoption patch `docs/product/v8/coverage-ledger.json`.

## Verification Commands

- `cd backend && .venv/bin/pytest -q tests/test_v8_final_governance_snapshot_adoption.py`
- `cd backend && .venv/bin/ruff check tests/test_v8_final_governance_snapshot_adoption.py`
- `cd backend && .venv/bin/ruff format --check tests/test_v8_final_governance_snapshot_adoption.py`
- JSON parse, exact diff, six-path tree fingerprint and sole-ledger binary patch hash.

Independent High review commits only its receipt; controller then commits only the unchanged
reviewed ledger patch.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FINAL-CLOSE-20260712-01`

## Evidence Path

- `artifacts/FPMS-V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION-20260813-01/`
