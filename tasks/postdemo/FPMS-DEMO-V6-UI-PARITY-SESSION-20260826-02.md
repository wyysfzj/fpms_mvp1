# FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["auth", "data", "source-authority", "sqlite"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02.md
Chosen runbook: `P0-prereq-heavy-story`

## Design References

- Approved design:
  `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`, exact commit
  `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved plan:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`, exact commit
  `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Active lean overlay:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`.
- Accepted Ordinal 01 HEAD: `97fcc7569c7cdf994910fde73e9f3a82c4fe66f4`.

## Exact Closure Slice

Add one setup-only persistent UI-session branch to the existing Integrated A rehearsal controller
and extend the read-only demo preflight with exact session identity and a complete automatically
derived zero-business-table projection. The branch reuses existing run-root, bundle, environment,
credential, service lifecycle, and cleanup owners; it creates no business object.

## Fixed Scope Decision

- `shared_file_density=MEDIUM`
- `prereq_dependency_density=HIGH`
- `be_fe_coupling=NONE`
- `evidence_cost=MEDIUM`
- `chosen_runbook=P0-prereq-heavy-story`
- SQLite-writing verification is serialized. Scope expansion is denied.

## Exact Behavior

1. Add only `--ui-session --actor HUMAN|CODEX --artifact <absolute>`; invalid/missing combinations
   fail before a run is created. Existing default A CLI, stdout contract, two-run behavior, and
   timeout remain compatible.
2. A UI session creates a unique run root and SQLite database, migrates, seeds only approved
   system/runtime facts, launches normal services and one headed browser, prints only redacted
   credentials, and pre-registers one passive finalize binding limited to observer artifacts.
3. STOP/failure preserves the exact run and artifact. Cleanup occurs only after explicit successful
   finalization and only for the exact validated run root.
4. Preflight adds only run id, candidate commit/tree, authority SHA, contract version, and complete
   business-table counts; existing response semantics are preserved.
5. `SYSTEM_RUNTIME_TABLE_ALLOWLIST` is exactly `t_user`, `t_role`, `t_role_perm`, `t_user_role`,
   `t_doc_template`, `t_task_template`, `t_fee_rate_book`, `t_fee_rate`.
6. Every sorted `Base.metadata.tables` name outside that exact allowlist is automatically business,
   including `T_GrantFeeTask` and every OfficialWorkPackage checklist/manifest/receipt child table.
   Preflight queries every derived table and fails if any count is nonzero.
7. The test proves the derived keys equal
   `sorted(Base.metadata.tables - SYSTEM_RUNTIME_TABLE_ALLOWLIST)` so new tables cannot be silently
   omitted. Task 03 will require this exact complete key set.

## Explicit Non-Closure

- No business object creation, demo automation, UI banner/observer, frontend change, API permission
  change, schema, migration, seed fact, fee/lifecycle rule, customer authorization, release, or
  Ordinal 03 behavior.
- No second runner, generic session framework, duplicated environment/credential/service owner,
  adjacent refactor, or broad test run.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02.md`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/app/modules/fees/demo_service.py`
- `backend/app/modules/fees/demo_service_schemas.py`
- `backend/tests/test_demo_v6_ui_session.py`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02/**`

## Verification Commands

Set `FPMS_PYTHON` to a Python 3.11 environment containing the backend dependencies, then run:

```bash
"$FPMS_PYTHON" -m pytest -q \
  backend/tests/test_demo_v6_ui_session.py backend/tests/test_demo_integrated_a_runner.py
"$FPMS_PYTHON" -m ruff check \
  scripts/run_demo_integrated_a_rehearsal.py backend/app/modules/fees/demo_service.py \
  backend/app/modules/fees/demo_service_schemas.py backend/tests/test_demo_v6_ui_session.py
git diff --check
```

GREEN must prove every derived business count is zero, the derived key set is complete, STOP
preserves the exact run, explicit successful finalization alone cleans it, credentials are redacted,
and default A remains compatible. Independent review binds the exact task range.

Expected HTTP status codes: existing read-only preflight status/envelope unchanged.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03`, blocked until this task is independently accepted.

## Done Definition

The setup-only branch and complete zero-business-table preflight pass focused tests and scoped lint;
default A remains compatible; one independent HIGH review and evidence gate pass with zero findings;
all non-closure boundaries remain intact.

## Rollback

Run `git revert --no-edit <accepted-task-range>`. Existing Integrated A remains the fallback.
