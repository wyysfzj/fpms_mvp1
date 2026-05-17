# DEMO-RUNBOOK-TERM-CONSISTENCY-01

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

Audit and update the project-root demo runbook/checklist so the terms used by demo operators match the current product UI labels for the end-to-end visible flow.

This closes only:

1. Align `demo/customer_demo_runbook_v2.md` terminology with current UI labels for case number, incoming/outgoing file registration, batch filing, bill creation, payment registration, allocation, and commission settlement.
2. Align `demo/demo_quick_checklist_v2.md` key button labels with current UI labels for the same visible flow.
3. Preserve the existing demo business sequence and demo data values.

## Explicit Non-Closure

This task does not modify product frontend code, backend code, API contracts, database schema, permissions, automation skeleton assets, seed data, runtime demo data, or historical artifact contents under `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/`.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/demo/DEMO-RUNBOOK-TERM-CONSISTENCY-01.md`
- `demo/customer_demo_runbook_v2.md`
- `demo/demo_quick_checklist_v2.md`
- `artifacts/DEMO-RUNBOOK-TERM-CONSISTENCY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh DEMO-RUNBOOK-TERM-CONSISTENCY-01 lint /bin/zsh -lc 'test -s demo/customer_demo_runbook_v2.md && test -s demo/demo_quick_checklist_v2.md && rg -n "案号|方向|文件类型|文件模板|标题|案件批件递交|查询案件|执行递交|从费用草稿生成|登记回款|收款日期|收款编号 / 交易参考号|创建核销|查询报表" demo/customer_demo_runbook_v2.md demo/demo_quick_checklist_v2.md'
```

```bash
./scripts/evidence_run.sh DEMO-RUNBOOK-TERM-CONSISTENCY-01 test /bin/zsh -lc '! rg -n "文档名称|文档方向|文档类型/模板|回款日期|回款编号|创建回款/保存|批量递交/确认|查询提成报表|创建账单/从草稿创建账单/提交" demo/customer_demo_runbook_v2.md demo/demo_quick_checklist_v2.md'
```

```bash
./scripts/task_validate.sh DEMO-RUNBOOK-TERM-CONSISTENCY-01
```

## Evidence Path

- `artifacts/DEMO-RUNBOOK-TERM-CONSISTENCY-01/results.jsonl`
- `artifacts/DEMO-RUNBOOK-TERM-CONSISTENCY-01/summary.md`
- `artifacts/DEMO-RUNBOOK-TERM-CONSISTENCY-01/git/diff.patch`
- `artifacts/DEMO-RUNBOOK-TERM-CONSISTENCY-01/baseline_allowlist.diff`
- `artifacts/DEMO-RUNBOOK-TERM-CONSISTENCY-01/baseline_external_files.txt`

## Done Definition

- The root demo runbook/checklist no longer use stale UI terms found during the audit.
- The updated docs use current visible UI terms where the operator clicks, fills, filters, or observes a field/button.
- Business data, lifecycle order, and non-demo files remain unchanged.
- Task evidence and task gate pass.
