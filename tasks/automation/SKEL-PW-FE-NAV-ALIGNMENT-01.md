# SKEL-PW-FE-NAV-ALIGNMENT-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend automation only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Task Plan Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend automation only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Align the Playwright TypeScript skeleton with the current product frontend sidebar and route surface.

This closes only:

1. Login page object uses the current Simplified Chinese username/password/button selectors.
2. Playwright local defaults point to the current Vite frontend port and API `/api/v1` path.
3. Task page object methods navigate to current task routes instead of stale `/tasks/my` or `/tasks/supervisor` paths.
4. A reusable app shell/sidebar page object covers the current product sidebar controls.
5. One targeted Playwright smoke verifies current product sidebar behavior: default work navigation visibility, module navigation switch, vertical group expand/collapse persistence, active route group visibility, and whole-sidebar icon-only collapse.

## Explicit Non-Closure

This task does not modify product frontend code, backend code, API contracts, route definitions, permissions, database schema, testcase IDs, structured YAML/JSON assets, or unrelated Playwright wave handlers. It does not add backend test data setup or broaden coverage beyond the current sidebar/login/task-route skeleton alignment slice.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/playwright.config.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/.env.example`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/README.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/clients/apiClient.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/fixtures/fpms.fixtures.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/waveW0.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/AppShellPage.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/LoginPage.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/TaskPage.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/current-product-sidebar.spec.ts`
- `docs/superpowers/specs/2026-05-17-skeleton-fe-nav-alignment-design.md`
- `docs/superpowers/plans/2026-05-17-skeleton-fe-nav-alignment.md`
- `tasks/automation/SKEL-PW-FE-NAV-ALIGNMENT-01.md`
- `artifacts/SKEL-PW-FE-NAV-ALIGNMENT-01/**`

## Verification Commands

Run from repo root:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/automation/SKEL-PW-FE-NAV-ALIGNMENT-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init SKEL-PW-FE-NAV-ALIGNMENT-01 --task-file tasks/automation/SKEL-PW-FE-NAV-ALIGNMENT-01.md --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/playwright.config.ts --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/.env.example --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/README.md --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/clients/apiClient.ts --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/fixtures/fpms.fixtures.ts --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/waveW0.ts --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/AppShellPage.ts --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/LoginPage.ts --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/TaskPage.ts --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/current-product-sidebar.spec.ts --allowlist docs/superpowers/specs/2026-05-17-skeleton-fe-nav-alignment-design.md --allowlist docs/superpowers/plans/2026-05-17-skeleton-fe-nav-alignment.md --allowlist tasks/automation/SKEL-PW-FE-NAV-ALIGNMENT-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd FPMS_Automation_Skeleton_Pack/playwright_ts SKEL-PW-FE-NAV-ALIGNMENT-01 typecheck -- npx tsc --noEmit
./scripts/evidence_run.sh SKEL-PW-FE-NAV-ALIGNMENT-01 typecheck bash -lc 'cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd FPMS_Automation_Skeleton_Pack SKEL-PW-FE-NAV-ALIGNMENT-01 assets -- python3 scripts/validate_assets.py
./scripts/evidence_run.sh SKEL-PW-FE-NAV-ALIGNMENT-01 assets bash -lc 'cd FPMS_Automation_Skeleton_Pack && python3 scripts/validate_assets.py'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd FPMS_Automation_Skeleton_Pack/playwright_ts SKEL-PW-FE-NAV-ALIGNMENT-01 playwright-list -- npx playwright test src/tests/current-product-sidebar.spec.ts --list
./scripts/evidence_run.sh SKEL-PW-FE-NAV-ALIGNMENT-01 playwright-list bash -lc 'cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/current-product-sidebar.spec.ts --list'
./scripts/task_validate.sh SKEL-PW-FE-NAV-ALIGNMENT-01
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize SKEL-PW-FE-NAV-ALIGNMENT-01 --status PASS --summary-file artifacts/SKEL-PW-FE-NAV-ALIGNMENT-01/summary.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKEL-PW-FE-NAV-ALIGNMENT-01
```

Optional live smoke, when frontend/backend services are reachable:

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/current-product-sidebar.spec.ts
```

## Evidence Path

- `artifacts/SKEL-PW-FE-NAV-ALIGNMENT-01/results.jsonl`
- `artifacts/SKEL-PW-FE-NAV-ALIGNMENT-01/summary.md`
- `artifacts/SKEL-PW-FE-NAV-ALIGNMENT-01/git/diff.patch`
- `artifacts/SKEL-PW-FE-NAV-ALIGNMENT-01/baseline_allowlist.diff`
- `artifacts/SKEL-PW-FE-NAV-ALIGNMENT-01/baseline_external_files.txt`

## Done Definition

- The Playwright skeleton compiles with the new page object and fixture.
- The product sidebar smoke is discoverable by Playwright and targets the current Chinese UI.
- Skeleton defaults and page objects no longer point at the stale frontend port, API path, or removed task routes.
- Required evidence exists and task gate passes.
