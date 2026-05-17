# DEMO-RUNBOOK-PUBLISH-UI-NAV-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: frontend-doc-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: frontend-doc-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Publish the previously generated customer demo runbook from `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/` into a new project-root `demo/` folder and update the published runbook/checklist to match the current product sidebar navigation UI.

This closes only:

1. Create project-root `demo/` with the v2 customer runbook and quick checklist copied from the existing batch artifact.
2. Update visible navigation instructions to use the current sidebar terms: `工作导航`, `模块导航`, `我的工作`, `案件生命周期`, `费用到回款`, `授权后运营`, and `管理入口`.
3. Keep the business demo data and lifecycle sequence unchanged.

## Explicit Non-Closure

This task does not modify product frontend code, backend code, API contracts, database schema, permissions, automation skeleton assets, test data, or existing historical artifact contents under `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/`.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/demo/DEMO-RUNBOOK-PUBLISH-UI-NAV-01.md`
- `demo/**`
- `demo/customer_demo_runbook_v2.md`
- `demo/demo_quick_checklist_v2.md`
- `artifacts/DEMO-RUNBOOK-PUBLISH-UI-NAV-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh DEMO-RUNBOOK-PUBLISH-UI-NAV-01 lint /bin/zsh -lc 'test -s demo/customer_demo_runbook_v2.md && test -s demo/demo_quick_checklist_v2.md && rg -n "工作导航|案件生命周期|费用到回款|授权后运营|管理入口" demo/customer_demo_runbook_v2.md demo/demo_quick_checklist_v2.md'
```

```bash
./scripts/evidence_run.sh DEMO-RUNBOOK-PUBLISH-UI-NAV-01 test /bin/zsh -lc 'rg -n "进入方式|字段与数据|点击按钮|可观察关键状态|继续条件|业务状态变更" demo/customer_demo_runbook_v2.md && ! rg -n "左侧菜单点击“案件管理”|左侧菜单点击“授权费任务”|左侧菜单点击“费用草稿”|左侧菜单点击“账单管理”|左侧菜单点击“回款与核销”|左侧菜单点击“年费任务”|左侧菜单点击“提成记录”|左侧菜单点击“提成结算”" demo/customer_demo_runbook_v2.md demo/demo_quick_checklist_v2.md'
```

```bash
./scripts/task_validate.sh DEMO-RUNBOOK-PUBLISH-UI-NAV-01
```

## Evidence Path

- `artifacts/DEMO-RUNBOOK-PUBLISH-UI-NAV-01/results.jsonl`
- `artifacts/DEMO-RUNBOOK-PUBLISH-UI-NAV-01/summary.md`
- `artifacts/DEMO-RUNBOOK-PUBLISH-UI-NAV-01/git/diff.patch`
- `artifacts/DEMO-RUNBOOK-PUBLISH-UI-NAV-01/baseline_allowlist.diff`
- `artifacts/DEMO-RUNBOOK-PUBLISH-UI-NAV-01/baseline_external_files.txt`

## Done Definition

- The root `demo/` folder contains the published v2 runbook and quick checklist.
- The published runbook/checklist use the current sidebar navigation labels and group names.
- Historical batch artifact files remain unchanged.
- Task evidence and task gate pass.
