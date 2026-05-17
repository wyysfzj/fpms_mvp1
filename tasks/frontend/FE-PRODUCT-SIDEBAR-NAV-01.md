# FE-PRODUCT-SIDEBAR-NAV-01 - product sidebar work/module navigation

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend-only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Task Plan Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend-only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Implement the approved product sidebar navigation shell from `docs/superpowers/specs/2026-05-17-product-sidebar-navigation-design.md`.

This closes only:

1. Sidebar defaults to product `工作导航` with sections for `我的工作`, `案件生命周期`, `费用到回款`, and `授权后运营`.
2. Sidebar provides a `模块导航` view for the complete module map using existing routes and permissions.
3. Sidebar can collapse and expand, with persisted collapse state and active route visibility.
4. Navigation mode persists between reloads.
5. Existing permission filtering hides unauthorized menu items and empty sections.

## Explicit Non-Closure

This task does not:

- modify backend code, API contracts, route definitions, permissions, database schema, or login behavior.
- add command palette, global search, mobile drawer behavior, or new product pages.
- change business workflows, dashboard data loading, or page-level forms.
- redesign page content outside the sidebar shell and its layout width.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `frontend/src/constants/menu.ts`
- `frontend/src/stores/ui.ts`
- `frontend/src/components/nav/SidebarNav.vue`
- `frontend/src/styles/layout.css`
- `frontend/src/constants/labels.zh.ts`
- `docs/superpowers/plans/2026-05-17-product-sidebar-navigation.md`
- `tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md`
- `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/**`

## Verification Commands

Run from repo root:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init FE-PRODUCT-SIDEBAR-NAV-01 --task-file tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md --allowlist frontend/src/constants/menu.ts --allowlist frontend/src/stores/ui.ts --allowlist frontend/src/components/nav/SidebarNav.vue --allowlist frontend/src/styles/layout.css --allowlist frontend/src/constants/labels.zh.ts --allowlist docs/superpowers/plans/2026-05-17-product-sidebar-navigation.md --allowlist tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-PRODUCT-SIDEBAR-NAV-01 lint -- npx eslint src --max-warnings 0
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-PRODUCT-SIDEBAR-NAV-01 test -- bash -lc 'npm run typecheck && npm run build'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize FE-PRODUCT-SIDEBAR-NAV-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FE-PRODUCT-SIDEBAR-NAV-01
./scripts/task_validate.sh FE-PRODUCT-SIDEBAR-NAV-01
```

Browser verification:

```bash
# Use the running local frontend.
# Verify the product sidebar after login. The worktree was browser-verified at http://127.0.0.1:5174/ with API proxying to http://localhost:8001/api/v1.
# Verify 工作导航 / 模块导航 switch, collapse persistence, active route highlight, and empty-section filtering.
```

## Evidence Path

- `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/results.jsonl`
- `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/summary.md`
- `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/git/diff.patch`
- `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/baseline_allowlist.diff`
- `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/baseline_external_files.txt`
