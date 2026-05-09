# SKELE2E-HARNESS-AUTHME-01 — Skeleton auth/me envelope user id helper

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack wave X auth helper path so `TC-X-017` can read the current user id from the current backend `/auth/me` response envelope `{ user: { id }, roles, permissions }` while preserving compatibility with the older top-level `{ id }` shape.

## Explicit Non-Closure

No product backend changes. No change to `/auth/me` backend contract. No frontend changes. No changes to task creation, task filtering, permissions, browser-use runtime, or unrelated wave handlers.

## Remaining Follow-Up Task IDs

- `SKELE2E-HARNESS-RUNID-01`
- `SKELE2E-FEERATE-CALCMODE-01`
- `SKELE2E-CASEPRIORITY-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-GRANTED-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. The task touches one shared wave handler file and one focused test file. |
| prereq_dependency_density | High. This unblocks one remaining backend clean-wave failure after DB assertion fixes. |
| be_fe_coupling | Low. This is backend automation harness only and does not change frontend behavior. |
| evidence_cost | Medium. Requires focused unit tests, lint, and task gates. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-AUTHME-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_task_log_handler.py`
- `artifacts/SKELE2E-HARNESS-AUTHME-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_x_task_log_handler.py::test_required_current_user_id_accepts_auth_me_envelope tests/test_x_task_log_handler.py::test_required_current_user_id_preserves_top_level_compatibility tests/test_x_task_log_handler.py::test_required_current_user_id_rejects_missing_id`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_task_log_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-AUTHME-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-AUTHME-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-AUTHME-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-AUTHME-01/`

## Done Definition

- A focused failing test proves current envelope-shaped `/auth/me` payloads can provide the user id.
- Compatibility with top-level `{ id }` payloads is preserved.
- Missing user id still raises a clear assertion.
- `TC-X-017` uses the helper instead of directly reading top-level `id`.
- Required evidence files exist and task gates pass.
