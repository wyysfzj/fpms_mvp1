# FE-SIDEBAR-GROUP-COLLAPSE-01 - sidebar navigation group collapse

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

Add vertical collapse behavior for large product sidebar navigation groups.

This closes only:

1. Expanded sidebar group headers are clickable controls for expanding/collapsing their group.
2. `工作导航` groups default to expanded.
3. `模块导航` groups default to collapsed except `我的工作` and the active route's group.
4. User group collapse choices persist by navigation mode and group key.
5. The active route's group remains expanded even if its saved state says collapsed.
6. Whole-sidebar collapsed mode continues to show icon links without group headers.

## Explicit Non-Closure

This task does not:

- modify backend code, API contracts, route definitions, permissions, database schema, or login behavior.
- change menu labels, business terminology, route strings, or permission mappings.
- add command palette, global search, mobile drawer behavior, or new product pages.
- change business workflows, dashboard data loading, or page-level forms.
- redesign page content outside the sidebar group collapse controls and related sidebar spacing.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `frontend/src/stores/ui.ts`
- `frontend/src/components/nav/SidebarNav.vue`
- `frontend/src/styles/layout.css`
- `docs/superpowers/specs/2026-05-17-sidebar-group-collapse-design.md`
- `docs/superpowers/plans/2026-05-17-sidebar-group-collapse.md`
- `tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md`
- `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/**`

## Verification Commands

Run from repo root:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init FE-SIDEBAR-GROUP-COLLAPSE-01 --task-file tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md --allowlist frontend/src/stores/ui.ts --allowlist frontend/src/components/nav/SidebarNav.vue --allowlist frontend/src/styles/layout.css --allowlist docs/superpowers/specs/2026-05-17-sidebar-group-collapse-design.md --allowlist docs/superpowers/plans/2026-05-17-sidebar-group-collapse.md --allowlist tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-SIDEBAR-GROUP-COLLAPSE-01 lint -- npx eslint src --max-warnings 0
./scripts/evidence_run.sh FE-SIDEBAR-GROUP-COLLAPSE-01 lint bash -lc 'cd frontend && npx eslint src --max-warnings 0'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-SIDEBAR-GROUP-COLLAPSE-01 test -- bash -lc 'npm run typecheck && npm run build'
./scripts/evidence_run.sh FE-SIDEBAR-GROUP-COLLAPSE-01 test bash -lc 'cd frontend && npm run typecheck && npm run build'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize FE-SIDEBAR-GROUP-COLLAPSE-01 --status PASS --summary-file artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/summary.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FE-SIDEBAR-GROUP-COLLAPSE-01
./scripts/task_validate.sh FE-SIDEBAR-GROUP-COLLAPSE-01
```

Browser verification:

```bash
# Verify the worktree frontend at http://127.0.0.1:5174/.
# Check work/module group defaults, manual expand/collapse, reload persistence, active group visibility, and icon-only sidebar behavior.
```

## Evidence Path

- `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/results.jsonl`
- `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/summary.md`
- `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/git/diff.patch`
- `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/baseline_allowlist.diff`
- `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/baseline_external_files.txt`
