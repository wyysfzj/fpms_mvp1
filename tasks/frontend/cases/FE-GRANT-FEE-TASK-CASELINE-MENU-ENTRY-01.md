# FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low

## chosen_runbook

P0-single-lane-story

## Exact Closure Slice

Add one case-lifecycle sidebar shortcut for the existing grant-fee task page so the runbook step "左侧菜单点击授权费任务" is easy to follow during a customer demo.

This closure includes exactly:

- add a visible Simplified Chinese `授权费任务` menu entry under the existing `业务实体` group near case lifecycle entries;
- point it to the existing route `/grant-fee/tasks`;
- keep the existing finance-group grant-fee task entry intact;
- preserve the existing route and grant-fee task page behavior.

## Explicit Non-Closure

This task does not:

- change grant-fee task page behavior;
- change router definitions;
- change backend APIs, permissions, data, schema, or migrations;
- modify Skeleton Pack assets;
- fix unrelated menu/page labels or demo runbook wording.

## Allowed Files

- `frontend/src/constants/menu.ts`
- `tasks/frontend/cases/FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01.md`
- `artifacts/FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01 test /bin/zsh -lc 'rg -n "grant_fee_tasks_case_lifecycle|授权费任务|/grant-fee/tasks" frontend/src/constants/menu.ts && cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- --fix src/constants/menu.ts && npm run lint -- src/constants/menu.ts'
```

```bash
./scripts/evidence_run.sh FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01 task_gate ./scripts/task_validate.sh FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01
```

## Evidence Path

- `artifacts/FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01/results.jsonl`
- `artifacts/FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01/summary.md`
- `artifacts/FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01/git/diff.patch`
- `artifacts/FE-GRANT-FEE-TASK-CASELINE-MENU-ENTRY-01/screenshots/**`

## Remaining Follow-Up Task IDs

- None.
