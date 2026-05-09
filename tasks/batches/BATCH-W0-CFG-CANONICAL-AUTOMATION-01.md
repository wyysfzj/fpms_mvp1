# BATCH-W0-CFG-CANONICAL-AUTOMATION-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

P0-prereq-heavy-story

## Batch Goal

Complete the promoted W0 parameter-configuration automation scope after `TC-W0-CFG-001` through `TC-W0-CFG-015` have been merged into canonical W0 assets.

This batch exists because the remaining goal spans pytest handlers, Playwright handlers, backend/frontend gap closure, and a migration decision. It must not be implemented as one broad task.

## Current Completed Slices

| Task File | Status | Closure |
|---|---:|---|
| `tasks/automation/W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01.md` | PASS | Created supplemental parameter-configuration test cases, seed data, and supplemental manifest. |
| `tasks/automation/W0-CFG-CANON-DATA-01.md` | PASS | Promoted 15 supplemental cases into canonical W0 assets and updated asset integrity counts to 170. |

## Execution Manifest

| Wave | Exact Task File Path | Owner Role | Allowed Ownership | Closure Slice | Non-Closure Boundary | Required Verification | Dependency |
|---:|---|---|---|---|---|---|---|
| 0 | `tasks/automation/W0-CFG-MIGRATION-DECISION-01.md` | default / explorer | docs/task/evidence only unless schema gap is proven | Decide whether any DB migration is actually required for the 15 promoted cases. If no schema change is required, document why existing tables are sufficient. | Does not create migrations or modify product code. If schema change is required, stop and create a separate approved DB task. | `./scripts/task_validate.sh W0-CFG-MIGRATION-DECISION-01` | completed canonical data promotion |
| 1 | `tasks/postenhancement/backend/W0-CFG-BE-SYSTEM-PARAM-METADATA-01.md` | worker | system API/schemas/service/tests | Close backend gap for system parameter list metadata needed by `TC-W0-CFG-001`. | Does not alter unrelated system settings or frontend. | scoped ruff, targeted pytest, task gate | migration decision complete |
| 1 | `tasks/postenhancement/backend/W0-CFG-BE-SEED-READINESS-01.md` | worker | seed/readiness API or test helper only | Provide backend/readiness support for detecting missing fee/commission/template/letterhead/country/department config for `TC-W0-CFG-014`. | Does not seed production data silently and does not change business transactions. | scoped ruff, targeted pytest, task gate | migration decision complete |
| 2 | `tasks/postenhancement/frontend/W0-CFG-FE-SYSTEM-PARAMS-01.md` | worker | `frontend/src/api/system.ts`, `SystemParams.vue`, tests if present | Show full system parameter metadata and secret masking behavior in the existing minimal UI for `TC-W0-CFG-001`. | Does not redesign settings navigation. | npm lint/typecheck targeted where supported, task gate | backend metadata task |
| 2 | `tasks/postenhancement/frontend/W0-CFG-FE-TEMPLATE-ROUTE-01.md` | worker | frontend router/menu/template page only | Expose existing template repository UI route and ensure visible Chinese text for `TC-W0-CFG-010`. | Does not implement real binary upload unless backend task explicitly adds it. | npm lint/typecheck targeted where supported, task gate | migration decision complete |
| 3 | `tasks/automation/W0-CFG-PY-SYSTEM-PARAMS-01.md` | worker | `wave_w0.py`, pytest tests | Implement pytest handlers for `TC-W0-CFG-001` and `TC-W0-CFG-002`. | Does not implement fee, commission, template, RBAC, or UI cases. | asset validation, targeted pytest, scoped ruff, task gate | backend/frontend prerequisites as needed |
| 3 | `tasks/automation/W0-CFG-PY-FEE-RATES-01.md` | worker | `wave_w0.py`, pytest tests | Implement pytest handlers for `TC-W0-CFG-003` and `TC-W0-CFG-004`. | Does not implement commission or templates. | asset validation, targeted pytest, scoped ruff, task gate | migration decision complete |
| 3 | `tasks/automation/W0-CFG-PY-COMMISSION-01.md` | worker | `wave_w0.py`, pytest tests | Implement pytest handlers for `TC-W0-CFG-005` through `TC-W0-CFG-007`. | Does not implement settlement export or reports. | asset validation, targeted pytest, scoped ruff, task gate | migration decision complete |
| 4 | `tasks/automation/W0-CFG-PY-TEMPLATES-01.md` | worker | `wave_w0.py`, pytest tests | Implement pytest handlers for `TC-W0-CFG-008` through `TC-W0-CFG-011`. | Does not implement product backend/frontend gaps beyond test usage. | asset validation, targeted pytest, scoped ruff, task gate | backend/frontend template prerequisites as needed |
| 4 | `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md` | worker | `wave_w0.py`, pytest tests | Implement pytest handlers for `TC-W0-CFG-012` through `TC-W0-CFG-015` where API/DB assertions are appropriate. | Does not implement Playwright UI assertions. | asset validation, targeted pytest, scoped ruff, task gate | frontend/backend prerequisite tasks |
| 5 | `tasks/automation/W0-CFG-PW-CONFIG-PAGES-01.md` | worker | Playwright W0 handler/spec/page helpers | Implement Playwright coverage for configuration page visibility, menu access, Chinese UI text, empty/loading/error states, and real API binding for promoted W0-CFG cases. | Does not duplicate API-only assertions already covered by pytest handlers. | Playwright targeted spec, TypeScript check if configured, task gate | relevant frontend tasks |
| 6 | `tasks/automation/W0-CFG-QA-CLOSE-01.md` | monitor / default | evidence/audit only | Final close audit for all 15 promoted cases, mapping each case to pytest/Playwright/backend/frontend evidence. | Does not add new product behavior. | all task gates, Pack asset validation, targeted pytest, targeted Playwright, release decision | all implementation tasks PASS |

## Shared Ownership / Serialization

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py` is a shared file and must be edited in serialized waves only.
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/waveW0.ts` is a shared file and must be edited after pytest handler waves or in a non-overlapping serialized slot.
- `frontend/src/api/system.ts`, router/menu files, and settings pages are shared frontend ownership files and must not be edited concurrently.
- DB migration work is blocked unless `W0-CFG-MIGRATION-DECISION-01` proves an unavoidable schema gap and creates a separate DB task.

## Batch Done Definition

- All listed task files exist and have PASS evidence.
- Every promoted case `TC-W0-CFG-001` through `TC-W0-CFG-015` has concrete pytest and/or Playwright execution coverage.
- Backend/frontend gaps identified by the promoted cases are either closed or explicitly documented as non-required for the case assertion.
- Migration decision is documented; if a migration is required, the batch cannot close until the separate migration task passes.
- `python3 FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py` passes with 170 canonical cases.
- Relevant pytest and Playwright targeted suites pass.
- `W0-CFG-QA-CLOSE-01` maps every case to evidence and reports no residual gap.
