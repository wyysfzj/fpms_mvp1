# FPMS-DEMO-ABC-LOCAL-BOOT-DEPENDENCY-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "deployment-packaging", "declared-dependency"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-LOCAL-BOOT-DEPENDENCY-20260816-01.md

## Story shape

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: none
- evidence_cost: low
- chosen_runbook: P0-prereq-heavy-story

## Design references

- `AGENTS.md`
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`
- `docs/superpowers/plans/2026-08-16-fpms-local-demo-abc-fast-track.md`
- Audit finding `DEPLOY-PKG-002`

## Exact Closure Slice

Declare the `openpyxl` runtime dependency required by the unconditional `app.main` import graph,
keep tracked package metadata synchronized, and prove a fresh declared-dependency installation can
import `app.main`.

## Explicit Non-Closure

No Docker/Compose/entrypoint, seed, storage, runtime-bundle, application API, workbook behavior,
frontend, database/schema/migration, security or production deployment change. This task does not
claim the local container is runnable; it closes only the clean package import prerequisite.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01`
- `FPMS-DEMO-ABC-FRESH-LOCAL-RUNNER-20260816-01`
- `FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01`
- `FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01`
- `FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01`
- `FPMS-DEMO-ABC-FINANCE-UI-20260816-01`
- `FPMS-DEMO-ABC-LIVE-E2E-20260816-01`

## Allowed Files

- `backend/pyproject.toml`
- `backend/fpms_api.egg-info/requires.txt`
- `backend/tests/test_demo_declared_runtime_dependencies.py`
- `artifacts/FPMS-DEMO-ABC-LOCAL-BOOT-DEPENDENCY-20260816-01/**`

## Verification Commands

1. RED: the target test fails because `openpyxl` is absent from declared runtime metadata.
2. GREEN: `cd backend && python3 -m pytest tests/test_demo_declared_runtime_dependencies.py -q`.
3. Scoped lint: `cd backend && python3 -m ruff check tests/test_demo_declared_runtime_dependencies.py`.
4. Fresh install: create a temporary Python 3.11 environment, install `backend` from declared
   metadata, change outside the repository path and run `python -c 'import app.main'`.
5. `git diff --check` and evidence validation pass for the exact allowlist.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-LOCAL-BOOT-DEPENDENCY-20260816-01/`

## Rollback

Revert the atomic story commit. This removes only the dependency declaration, its synchronized
tracked metadata, focused test and task evidence.

## Done definition

The focused test, scoped lint, fresh-install import smoke and evidence validation return 0; only
allowed files changed; an independent High reviewer accepts the exact commit/range. No broader
demo or product readiness is claimed.
