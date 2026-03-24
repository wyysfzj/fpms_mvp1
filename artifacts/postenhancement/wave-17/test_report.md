# Wave 17 Test Report

Date: 2026-02-28
Role: Tester
Task: `PE-BE-AN-07`

## Pass/Fail Matrix

| Check | Result | Notes |
|---|---|---|
| Evidence presence (`results.jsonl`, `summary.md`, `git/diff.patch`) | PASS | All required files present under `artifacts/PE-BE-AN-07/`. |
| Task gate (`./scripts/task_validate.sh PE-BE-AN-07`) | PASS | Initial FAIL due schema mismatch; remediated via `scripts/evidence_run.sh`; re-run PASS. |
| Required verify: `cd backend && pytest -q` | PASS | `141 passed, 3 warnings in 30.27s`. |
| Allowlist spot-check | PASS | `artifacts/PE-BE-AN-07/git/diff.patch` touched only `backend/app/modules/annuity/api.py` and `backend/app/modules/annuity/service.py` (within allowlist). |

## Key Command Outputs

- `./scripts/task_validate.sh PE-BE-AN-07` (after remediation): `Task Gate PASS`
- `cd backend && pytest -q`:
  - `141 passed, 3 warnings in 30.27s`

## Final Status

- `PE-BE-AN-07`: PASS
