# FE-MENU-PERMISSION-ALIGNMENT-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Align PayList and Commission frontend menu permissions with backend
`require_perm` strings.

## Explicit Non-Closure

Do not change backend permission enforcement, RBAC seed data, routes, or page
behavior.

## Remaining Follow-Up Task IDs

- BATCH-FE-COMPLETENESS-REMEDIATION-01-CLOSE-AUDIT

## Allowed Files

- tasks/frontend/FE-MENU-PERMISSION-ALIGNMENT-01.md
- frontend/src/constants/menu.ts
- frontend/src/constants/perms.ts
- artifacts/FE-MENU-PERMISSION-ALIGNMENT-01/**

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh FE-MENU-PERMISSION-ALIGNMENT-01
```

## Evidence Path

- artifacts/FE-MENU-PERMISSION-ALIGNMENT-01/results.jsonl
- artifacts/FE-MENU-PERMISSION-ALIGNMENT-01/summary.md
- artifacts/FE-MENU-PERMISSION-ALIGNMENT-01/git/diff.patch
