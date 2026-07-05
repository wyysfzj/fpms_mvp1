# PD-P1-DEMO-V6-RUNBOOK-PROD-SOURCES-20260705-01

## Exact Closure Slice

Add an appendix to the V6 UI E2E demo runbook explaining where each enrichment-backed demo object should come from in production.

## Explicit Non-Closure

Do not change product code, seed scripts, tests, UI behavior, demo data, or workflow rules. Do not rerun cleanup or enrichment.

## Remaining Follow-Up Task IDs

None

## Allowed Files

- tasks/postdemo/PD-P1-DEMO-V6-RUNBOOK-PROD-SOURCES-20260705-01.md
- docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md
- artifacts/PD-P1-DEMO-V6-RUNBOOK-PROD-SOURCES-20260705-01/**

## Verification Commands

- rg -n "附件 A|生产环境数据来源|enrichment|新申请工作包|年费任务" docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md
- git diff --check
- ./scripts/task_validate.sh PD-P1-DEMO-V6-RUNBOOK-PROD-SOURCES-20260705-01

## Evidence Path

- artifacts/PD-P1-DEMO-V6-RUNBOOK-PROD-SOURCES-20260705-01/**
