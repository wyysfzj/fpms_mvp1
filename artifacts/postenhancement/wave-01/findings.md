# Wave 01 Findings

## 2026-02-28 Reviewer Findings (Actionable)

1. `HIGH` Gate schema mismatch:
   - Update each task `artifacts/<TASK-ID>/results.jsonl` to include validator-expected entries:
     - `{"step":"lint","rc":0,...}`
     - `{"step":"test","rc":0,...}`
   - Re-run and record:
     - `./scripts/task_validate.sh PE-BE-00-01`
     - `./scripts/task_validate.sh PE-BE-00-03`
     - `./scripts/task_validate.sh PE-FE-00-01`
     - `./scripts/task_validate.sh PE-FE-00-03`

2. `MEDIUM` Backend quality gate completeness:
   - Run and capture evidence for:
     - `cd backend && ruff check --fix .`
     - `cd backend && ruff format .`
     - `cd backend && ruff check .`
     - `cd backend && pytest -q`
   - Update wave `test_report.md` command outcomes with exact results.

3. `LOW` Permission contract drift:
   - Resolve `Dashboard.Read` frontend constant vs backend RBAC absence by either:
     - removing/avoiding use of `Dashboard.Read`, or
     - adding backend permission definition and seed coverage if dashboard auth is intended.

## Remediation Update (2026-02-28)

1. `HIGH` Gate schema mismatch: FIXED
   - Added validator-compatible result entries with `"step":"lint"` and `"step":"test"` and `rc=0` for:
     - `PE-BE-00-01`
     - `PE-BE-00-03`
     - `PE-FE-00-01`
     - `PE-FE-00-03`
   - Re-run results:
     - `./scripts/task_validate.sh PE-BE-00-01` -> PASS
     - `./scripts/task_validate.sh PE-BE-00-03` -> PASS
     - `./scripts/task_validate.sh PE-FE-00-01` -> PASS
     - `./scripts/task_validate.sh PE-FE-00-03` -> PASS

2. `MEDIUM` Backend quality gate completeness: FIXED
   - Executed and recorded:
     - `cd backend && ruff check --fix .` -> `rc=0`
     - `cd backend && ruff format .` -> `rc=0`
     - `cd backend && ruff check .` -> `rc=0`
     - `cd backend && pytest -q` -> `rc=0` (`141 passed, 3 warnings`)

3. `LOW` Permission contract drift: FIXED
   - `DASHBOARD_READ` is no longer present in `frontend/src/constants/perms.ts`.
   - Verification:
     - `rg -n "DASHBOARD_READ" frontend/src -S` -> no matches.

## Re-Review Confirmation (2026-02-28)

- All three previously reported findings are now closed:
  - `HIGH` Gate schema mismatch: CLOSED
  - `MEDIUM` Backend lint-discipline evidence gap: CLOSED
  - `LOW` `DASHBOARD_READ` permission drift: CLOSED
- Reviewer final verdict updated to PASS in `review_report.md`.
