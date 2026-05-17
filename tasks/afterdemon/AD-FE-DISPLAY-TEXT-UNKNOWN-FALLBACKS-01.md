# AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01 - shared display text unknown fallback cleanup

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: high
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Normalize unknown enum/code display fallbacks in the shared frontend display text helpers.

This closes only:

1. `displayText.ts` no longer returns raw unknown case/bill/fee/task/document/payment code values from shared user-facing helper functions.
2. Unknown display fallbacks use concise Simplified Chinese placeholders.
3. Existing known mappings and function signatures remain unchanged.

## Explicit Non-Closure

This task does not:

- modify backend code, API wrappers/types, route params, permissions, response envelopes, or enum contracts.
- add new enum values or change known mapped labels.
- change module-specific helper functions outside `displayText.ts`.
- change currency codes, protocol values, API payload values, logs, or debug context.

## Remaining Follow-Up Task IDs

- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01.md`
- `frontend/src/constants/displayText.ts`
- `artifacts/AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/constants/displayText.ts --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01 ux_check /bin/zsh -lc '! rg -n "\\|\\| (status|type|priority|direction|docType|method|actionName)$|\\|\\| (status|type|priority|direction|docType|method|actionName)$" frontend/src/constants/displayText.ts && rg -n "未知案件状态|未知账单状态|未知草单状态|未知草单类型|未知案件类型|未知费用类型|未知任务状态|未知优先级|未知文书方向|未知文书类型|未知账单方向|未知付款方式|未知操作" frontend/src/constants/displayText.ts'
./scripts/evidence_run.sh AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01 task_gate ./scripts/task_validate.sh AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01
```

## Evidence Path

- `artifacts/AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01/results.jsonl`
- `artifacts/AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01/summary.md`
- `artifacts/AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01/git/diff.patch`
- `artifacts/AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DISPLAY-TEXT-UNKNOWN-FALLBACKS-01/baseline_external_files.txt`
