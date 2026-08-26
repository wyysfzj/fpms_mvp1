# FPMS-DEMO-V6-UI-PARITY-TERMINAL-HARDENING-20260826-02U-03U

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["data", "lineage", "security", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-TERMINAL-HARDENING-20260826-02U-03U.md
Chosen runbook: `P0-prereq-heavy-story`

## Approval And Fixed Findings

- User approval:
  `批准 02S Unicode-safe STOP + 03R console/race 最小修复边界`.
- Demo-critical risk decision:
  `批准 4a03e3d 作为 Demo-critical 条件通过；将 post-STOP console capability/Error.cause 降为 Demo 后 P2 安全整改，继续 Ordinal 04`.
- User also requested a concurrent over-engineering audit.
- Base HEAD: `2a60669df4333128f756de3e22103916d01508c9`.
- Controlling review: final 03R re-review at that HEAD, exactly three remaining P1 findings.
- Accepted 02S task boundary: `8b07b5f671d238b39cee11c81d4ecf857499ffa5`.
- Approved design/plan remain exact commits
  `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d` and
  `80bd46829eaf5f798dda9422550a583c7fa12fde` under the active lean overlay.

## Exact Closure Slice

Close only the three final integration findings: Unicode-safe secret comparison in the accepted
terminal STOP host, console redaction before the original sink, and immutable old-run STOP completion
that cannot clear a newly activated run. This is one atomic cross-layer repair because all three are
required by the same real frontend-to-host terminal path.

## Exact Behavior

1. Host secret scanning compares arbitrary Unicode ledger strings to the ASCII capability without
   raising. A valid Simplified-Chinese action/route/label plus terminal STOP returns exact 200
   `STOPPED`; the existing sensitive-field/capability rejection remains unchanged.
2. The browser console observer examines and redacts complete arguments before invoking the original
   console sink. Any value containing the exact capability reaches that sink only as a fixed redacted
   marker; the redacted failure digest and terminal STOP behavior remain intact.
3. A STOP export captures an immutable old-run tuple, redacted ledger snapshot, binding, storage, and
   storage value before awaiting the host. On completion it may clear only if that exact storage value
   still belongs to the old run. It cannot read, append to, or remove a genuinely new run's state.
4. All previously accepted 02S/03R behavior remains unchanged, including exact status/body checks,
   cold `/demo/abc`, terminal same-run guard, URL scrub, real capture ordering, eleven PNGs, disposer,
   Axios status, A compatibility, failure preservation, and successful finalization.

## Explicit Non-Closure

- No new endpoint, exported production API, store/database, storage key, component, page, route,
  dependency, class hierarchy, adapter/plugin system, generic concurrency primitive, retry, logging
  framework, business behavior, broad test, release, or Ordinal 04 work.
- Every production change must directly map to one of the three findings. Prefer local values and one
  bounded helper over new abstractions. Existing unrelated code is not renamed, reformatted, or moved.
- Final audit reports production/test line delta, new abstractions/dependencies, changed paths, and
  whether any line lacks a direct finding mapping.
- Post-STOP logging of a capability nested in `Error.cause` or another complete-argument edge case is
  explicitly deferred to `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`. The accepted demo path
  does not log capabilities, and this deferred security hardening does not block Demo-critical
  acceptance or Ordinal 04.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-TERMINAL-HARDENING-20260826-02U-03U.md`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_v6_ui_session.py`
- `frontend/src/modules/demo/demoUiSession.ts`
- `frontend/tests/demo-v6-ui-session-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-TERMINAL-HARDENING-20260826-02U-03U/**`

## Verification Commands

```bash
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python \
  -m pytest tests/test_demo_v6_ui_session.py -q)
node frontend/tests/demo-v6-ui-session-contract.mjs
node frontend/tests/demo-abc-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/demo/demoUiSession.ts)
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python \
  -m ruff check scripts/run_demo_integrated_a_rehearsal.py \
  backend/tests/test_demo_v6_ui_session.py
git diff --check
```

GREEN must include a real frontend-ledger-to-actual-host Chinese STOP probe, capture of the original
console sink arguments, and a deferred old-run STOP response racing a genuine new-run activation.
Independent review binds the exact task range and the over-engineering audit.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-TERMINAL-HARDENING-20260826-02U-03U/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04`, blocked until repaired Ordinal 03 is accepted.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, deferred until after the customer demo.

## Done Definition

All three Demo-critical counterexamples are closed without new architecture or scope, prior gates
remain green, independent review reports zero Demo-critical findings, the atomic evidence gate
passes, and the over-engineering audit finds no speculative or unmapped production change. The
explicit post-demo P2 remains non-closure and is not reported as task PASS work.

## Rollback

Run `git revert --no-edit <accepted-02U-03U-task-range>`. Accepted 02S and the rejected 03R candidate
remain diagnosable; Ordinal 04 stays blocked.
