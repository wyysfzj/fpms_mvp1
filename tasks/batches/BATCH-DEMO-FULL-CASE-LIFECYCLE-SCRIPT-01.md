# BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: medium

## chosen_runbook

P0-frontend-heavy-story

## Exact Closure Slice

Create a customer-facing FPMS full-case-lifecycle demo script from the already optimized and verified TRUE UI-interaction E2E flow.

The script must:

1. Describe demo prerequisites and fictional demo data.
2. Convert the verified UI-only lifecycle into a smoother customer demo route.
3. Provide step-by-step visible UI actions for every business state mutation.
4. Explain required preconditions before each next step can continue.
5. Include risk handling and customer-safe backup talking points.
6. Map the demo flow back to the FPMS Automation Skeleton Pack lifecycle checkpoints where useful.

This is a documentation-only close slice.

## Explicit Non-Closure

This task does not:

- execute another browser E2E run;
- modify frontend or backend product code;
- modify Skeleton Pack YAML/JSON/schema/source assets;
- create, update, or mutate business data through API;
- use real customer PII, real customer accounts, real case data, passwords, tokens, Authorization headers, or access tokens;
- claim that deferred or unsupported product behavior is implemented.

## Allowed Files

- `tasks/batches/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01 test /bin/zsh -lc 'test -s artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/demo_script.md && test -s artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/demo_data.md && test -s artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/runbook_summary.md && rg -n "创建目标批次|按目标案件号生成|材料 gate|账单与收款|回款与核销" artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/demo_script.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01.md && test -f artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/demo_script.md && test -f artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/demo_data.md && test -f artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/runbook_summary.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01 secret_scan /bin/zsh -lc 'p1=admin"123"; p2="Authorization: ""Bearer"; p3=access"_token"; p4="ey""J[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"; ! rg -n "$p1|$p2|$p3|$p4" artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/demo_script.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/demo_data.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/runbook_summary.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/results.jsonl`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/summary.md`
- `artifacts/BATCH-DEMO-FULL-CASE-LIFECYCLE-SCRIPT-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None.
