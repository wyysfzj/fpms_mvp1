# FPMS-DEMO-V6-UI-PARITY-SESSION-REPAIR-20260826-02R

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["data", "lineage", "security", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-REPAIR-20260826-02R.md
Chosen runbook: `P0-prereq-heavy-story`

## Approval And Fixed References

- User approval: `批准 Ordinal 02R/03R 最小重划边界，修复后恢复 Ordinal 03 并继续后续计划`.
- Findings-only extension approval:
  `批准 02R PNG 非零尺寸 + IDAT 最小修复边界，修复并复核后恢复 03R`.
- Approved design: `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`,
  exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved plan: `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`,
  exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Active lean overlay:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`.
- Accepted Ordinal 02 HEAD: `1971f62e2f3a489158ae83aec62c0ef42c72f8f2`.
- Rejected Ordinal 03 candidate: `54074a764ddd176f826711928453a6dc9ff4b236`.

## Exact Closure Slice

Repair only the local headed-session host contract that Ordinal 03 consumes. Replace the tokenless,
arbitrary loopback upload and terminal-input completion seam with one unguessable per-run capability,
exact tuple revalidation that remains valid after business mutations, and an evidence-complete browser
finalization handshake. Preserve the initial 77-count zero-data preflight and existing Integrated A.

## Exact Behavior

1. Generate one unguessable token per UI run. The loopback host accepts requests only with that token
   and the exact contract version, run ID, candidate commit/tree, authority SHA, and actor captured for
   the run. Wrong/missing token or tuple fails closed.
2. Expose an authenticated tuple-only revalidation operation. It does not rerun the zero-count
   freshness rule and therefore remains valid after Stage 01 or later mutations. The existing backend
   preflight remains the sole initial activation check and still requires all 77 business counts zero.
3. Accept only the named observer JSON and PNG evidence files directly under the exact observer root.
   Reject unknown names, duplicates, path escape, symlinks, malformed encodings, and oversized bodies.
   A PNG must have one legal `IHDR` with nonzero dimensions and at least one structurally valid `IDAT`
   before the terminal `IEND`; a signature/chunk envelope without image data is not evidence.
4. Accept browser finalization only after the required observer ledger and screenshot set is present
   and validates against the same tuple. Successful finalization signals the waiting runner without
   terminal input; STOP/failure preserves the exact run and artifacts.
5. The runner removes the exact validated run root only after successful browser finalization. Browser
   exit, timeout, malformed evidence, wrong binding, or any host error records failure/STOP and
   preserves the run for diagnosis.
6. The browser launch carries the exact capability once for activation. Ordinal 03R owns durable
   sessionStorage persistence, normal-route reuse, STOP behavior, and frontend observer emission.

## Explicit Non-Closure

- No business API, business state machine, backend schema/migration, seed data, source authority,
  permissions model, generic authentication service, remote observer, retry framework, or release.
- No frontend production change in 02R. No Ordinal 04 behavior. No redesign of Integrated A.
- No relaxation of the initial all-zero preflight and no customer/production activation.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-REPAIR-20260826-02R.md`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_v6_ui_session.py`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-SESSION-REPAIR-20260826-02R/**`

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

GREEN must prove token and tuple rejection, post-mutation tuple revalidation, exact observer-file
allowlisting, path/duplicate/encoding rejection, evidence-complete browser finalization without
terminal input, preservation on STOP/failure, exact cleanup on success, and unchanged Integrated A
CLI/preflight compatibility. Independent review binds the exact task range.

Expected loopback status semantics: `200` valid revalidation/finalization, `201` accepted artifact,
`400` malformed artifact/request, `401` missing/wrong capability, `409` tuple/evidence conflict, and
`404` unknown operation. Existing backend API status semantics are unchanged.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-SESSION-REPAIR-20260826-02R/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-OBSERVER-REPAIR-20260826-03R`, blocked until this task is accepted.
- `FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04`, blocked until repaired Ordinal 03 is accepted.

## Done Definition

The local UI-session host authenticates and revalidates the exact immutable run tuple after business
mutations, admits only the required observer evidence, and completes or preserves the run solely from
validated browser state. Focused tests, Ruff, diff check, independent review, and evidence gate pass
with zero findings.

## Rollback

Run `git revert --no-edit <accepted-02R-task-range>`. The rejected Ordinal 03 candidate remains
non-accepted until 03R closes its findings.
