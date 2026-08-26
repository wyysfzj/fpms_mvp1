# FPMS-DEMO-V6-UI-PARITY-SESSION-STOP-20260826-02S

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["data", "lineage", "security", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-STOP-20260826-02S.md
Chosen runbook: `P0-prereq-heavy-story`

## Approval And Fixed References

- User approval: `批准 02R terminal STOP host + 03R findings-only 最小整改边界`.
- Accepted Ordinal 02R HEAD: `c4230a48e356764b956bbd51d34ce589969c88fa`.
- Rejected 03R candidate: `885f353b39d9da230ea0377e0a743d546b630ebf`.
- Approved design/plan remain exact commits
  `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d` and
  `80bd46829eaf5f798dda9422550a583c7fa12fde` under the active lean overlay.

## Exact Closure Slice

Add one authenticated terminal STOP operation to the accepted 02R local observer host so a frontend
failure after partial evidence upload can durably record the final STOP ledger, wake the runner, and
preserve the exact run. Do not change successful finalization or any business/backend API.

## Exact Behavior

1. `POST /stop` uses the same unguessable capability and exact six-field run tuple as `/revalidate`,
   `/observer-artifact`, and `/finalize`.
2. Its request contains only that tuple plus one redacted ledger whose schema/session match the host
   and whose final event is exactly `{"kind":"STOP","reason":<nonempty code>}`.
3. The host writes exactly one `observer-stop-ledger.json` under the observer root using exclusive,
   non-symlink creation. It accepts no filename/path input and no raw payload/credential fields.
4. After the 200 `{"status":"STOPPED"}` response is successfully sent, the host sets a dedicated
   stopped event. The runner returns `STOPPED`, preserves the run root/artifacts, and writes the
   existing terminal session status. A failed response or I/O error sets FAILED instead.
5. Missing/wrong capability is 401 without unauthenticated denial of service; tuple drift is 409;
   malformed/non-STOP/duplicate stop evidence is 400/409 and fail-closed. `/finalize` behavior and
   the required success evidence set remain unchanged.

## Explicit Non-Closure

- No frontend change, generic event bus, retry framework, overwrite/update endpoint, business API,
  schema/migration, source/fee/lifecycle decision, dependency, remote host, release, or Ordinal 04.
- No relaxation of initial zero-count activation, PNG validation, successful evidence completeness,
  exact cleanup, or existing Integrated A behavior.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-STOP-20260826-02S.md`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_v6_ui_session.py`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-SESSION-STOP-20260826-02S/**`

## Verification Commands

```bash
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python \
  -m pytest tests/test_demo_v6_ui_session.py -q)
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python \
  -m ruff check scripts/run_demo_integrated_a_rehearsal.py \
  backend/tests/test_demo_v6_ui_session.py
git diff --check
```

GREEN must prove authenticated STOP after zero or partial evidence, exact ledger persistence, runner
wakeup/preservation, response-before-event ordering, 401/409/400/duplicate rejection, error
preservation, unchanged successful finalize, and Integrated A compatibility. Independent review binds
the exact task range.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-SESSION-STOP-20260826-02S/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-OBSERVER-REPAIR-20260826-03R`, blocked until 02S is accepted.
- `FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04`, blocked until repaired Ordinal 03 is accepted.

## Done Definition

The exact browser session can durably terminate as STOP after any partial observer export, the runner
wakes without long polling or terminal input, the run remains recoverable, and focused tests, Ruff,
scope, independent zero-finding review, and evidence gate pass.

## Rollback

Run `git revert --no-edit <accepted-02S-task-range>`. Accepted 02R remains intact; 03R and Ordinal 04
remain blocked.
