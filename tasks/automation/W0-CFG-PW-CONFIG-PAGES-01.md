# W0-CFG-PW-CONFIG-PAGES-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium

## chosen_runbook

P0-frontend-heavy-story

## Exact Closure Slice

Close only the Playwright Skeleton Pack handler for the system-params page portion of `TC-W0-CFG-015`: the canonical W0 Playwright spec must route `TC-W0-CFG-015` to a real handler that prepares data through the real `/system/params` API and verifies the existing `/system/params` UI renders that real API data without static route interception.

## Explicit Non-Closure Statement

This task does not implement Playwright coverage for fee rates, commission rules, task templates, doc templates, letterheads, master data pages, RBAC menu matrices, backend endpoints, frontend source changes, or pytest handlers.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-FEE-RATES-01.md`
- `tasks/automation/W0-CFG-PY-COMMISSION-01.md`
- `tasks/automation/W0-CFG-PY-TEMPLATES-01.md`
- `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PW-CONFIG-PAGES-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/waveW0.ts`
- `artifacts/W0-CFG-PW-CONFIG-PAGES-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm test -- --list --grep TC-W0-CFG-015
./scripts/task_validate.sh W0-CFG-PW-CONFIG-PAGES-01
```

## Evidence Path

- `artifacts/W0-CFG-PW-CONFIG-PAGES-01/results.jsonl`
- `artifacts/W0-CFG-PW-CONFIG-PAGES-01/summary.md`
- `artifacts/W0-CFG-PW-CONFIG-PAGES-01/git/diff.patch`
