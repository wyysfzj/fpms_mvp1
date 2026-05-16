# FE-DEMO-LAYOUT-SCROLLBARS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-single-lane-story

## Exact Closure Slice

Fix the main FPMS application shell so the left sidebar navigation and right content region are independently scrollable when their content exceeds the visible viewport height. The fix must allow demo users to see all menu items and all page content on the current local frontend without changing business workflows.

## Explicit Non-Closure

- Do not change backend behavior.
- Do not change business state transitions.
- Do not add, remove, or rename menu entries.
- Do not change router wiring or route behavior.
- Do not modify Skeleton Pack assets.
- Do not perform unrelated visual redesign or page-specific workflow changes.

## Allowed Files

- frontend/src/styles/layout.css
- tasks/frontend/DEMO-UI/FE-DEMO-LAYOUT-SCROLLBARS-01.md
- artifacts/FE-DEMO-LAYOUT-SCROLLBARS-01/**

## Verification Commands

```bash
./scripts/evidence_run.sh FE-DEMO-LAYOUT-SCROLLBARS-01 test /bin/zsh -lc 'rg -n "\.sidebar-nav|\.content-scroll|overflow-y: auto|min-height: 0|scrollbar-gutter" frontend/src/styles/layout.css && cd frontend && npm run typecheck'
./scripts/evidence_run.sh FE-DEMO-LAYOUT-SCROLLBARS-01 lint /bin/zsh -lc 'test -f tasks/frontend/DEMO-UI/FE-DEMO-LAYOUT-SCROLLBARS-01.md && test -f artifacts/FE-DEMO-LAYOUT-SCROLLBARS-01/summary.md'
./scripts/evidence_run.sh FE-DEMO-LAYOUT-SCROLLBARS-01 secret_scan /bin/zsh -lc 'p1=admin"123"; p2="Authorization: ""Bearer"; p3=access"_token"; p4="ey""J[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"; ! rg -n "$p1|$p2|$p3|$p4" artifacts/FE-DEMO-LAYOUT-SCROLLBARS-01'
./scripts/evidence_run.sh FE-DEMO-LAYOUT-SCROLLBARS-01 task_gate ./scripts/task_validate.sh FE-DEMO-LAYOUT-SCROLLBARS-01
```

## Evidence Path

artifacts/FE-DEMO-LAYOUT-SCROLLBARS-01/

## Remaining Follow-up Task IDs

None
