# SKELE2E-HARNESS-READINESSSTATE-01 — Skeleton readiness audit accepts full-wave state

Task ID: `SKELE2E-HARNESS-READINESSSTATE-01`

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack `TC-W0-CFG-014` readiness assertion so it remains valid when the full backend wave has already created configuration rows before the readiness audit runs.

This task closes only:

1. `TC-W0-CFG-014` continues to verify readiness response shape, counts, `BLOCKED` status, `hard_blocked=true`, and missing-entry metadata.
2. Seed-only payloads still require the expected seed-only hard blocker keys.
3. Full-wave stateful payloads may omit a seed-only blocker when the corresponding readiness count shows that configuration has already been created.

## Explicit Non-Closure

No product backend changes. No database schema or migration changes. No frontend changes.
Do not change readiness endpoint response shape, readiness service rules, seed data, W0 setup order, batch filing gate behavior, or pay-list behavior.

## Remaining Follow-Up Task IDs

- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one W0 handler assertion and one focused handler test. |
| prereq_dependency_density | Medium. It removes a stateful W0 audit blocker before remaining backend E2E failures can be measured cleanly. |
| be_fe_coupling | Low. This is backend E2E harness-only and has no frontend surface. |
| evidence_cost | Medium. Requires RED/GREEN focused tests, lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-READINESSSTATE-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_seed_readiness_handler.py`
- `artifacts/SKELE2E-HARNESS-READINESSSTATE-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-READINESSSTATE-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_w0_seed_readiness_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_seed_readiness_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-READINESSSTATE-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-READINESSSTATE-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-READINESSSTATE-01/`

## Done Definition

- Focused tests prove seed-only readiness still enforces expected hard blockers.
- Focused tests prove stateful full-wave readiness with positive configuration counts and only remaining system-param blockers is accepted.
- No product files are modified.
- Required evidence files exist and task gates pass.
