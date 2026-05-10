# BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: medium

## chosen_runbook

P0-frontend-heavy-story

## Exact Closure Slice

Create a v2 customer demo runbook in operation-manual form for the verified FPMS full-case-lifecycle UI flow.

The v2 runbook must be organized as actionable steps. Each major step must state:

- where to enter from, including page/menu/button;
- which fields to input/select and what demo data to use;
- which button to click to submit/confirm;
- which visible state proves the step succeeded;
- what condition must be satisfied before continuing;
- whether the step mutates business state.

This closes only the documentation conversion from the previously verified E2E flow into a customer-understandable operation manual.

## Explicit Non-Closure

This task does not:

- run a new UI E2E test;
- modify frontend or backend product code;
- modify FPMS Automation Skeleton Pack assets;
- create or mutate business state through API;
- use real customer PII, real accounts, real cases, passwords, tokens, Authorization headers, or access tokens;
- replace product user documentation beyond this customer demo runbook.

## Allowed Files

- `tasks/batches/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01 test /bin/zsh -lc 'test -s artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/customer_demo_runbook_v2.md && test -s artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/demo_quick_checklist_v2.md && rg -n "进入方式|字段与数据|点击按钮|可观察关键状态|继续条件|业务状态变更" artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/customer_demo_runbook_v2.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01.md && test -f artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/customer_demo_runbook_v2.md && test -f artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/demo_quick_checklist_v2.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01 secret_scan /bin/zsh -lc 'p1=admin"123"; p2="Authorization: ""Bearer"; p3=access"_token"; p4="ey""J[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"; ! rg -n "$p1|$p2|$p3|$p4" artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/customer_demo_runbook_v2.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/demo_quick_checklist_v2.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/results.jsonl`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/summary.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-RUNBOOK-V2-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None.
