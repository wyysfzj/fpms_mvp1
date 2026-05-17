# AD-FE-COMMISSION-LIST-ID-DISPLAY-01 — commission list visible ID cleanup

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Remove visible raw commission/case/agent internal ID displays and raw status fallback text from the commission list page.

This closes only:

1. `CommissionList.vue` no longer renders the internal commission `id` column.
2. `CommissionList.vue` case display uses `case_no` or a Chinese fallback instead of `case_id`.
3. `CommissionList.vue` agent display uses a Chinese assignment placeholder instead of `agent_id`.
4. `CommissionList.vue` unknown status fallback text is Chinese instead of the raw enum value.

## Explicit Non-Closure

This task does not:

- modify backend code, commission API wrappers/types, commission settlement page, route params, permissions, response envelopes, or commission fetch behavior.
- add agent-name resolution, user selector behavior, case-name resolution, or any new API join.
- change filters, query params, amount/date formatting, stage tags, pagination, export, or print behavior.
- close raw-ID display issues outside `CommissionList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01`
- `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-COMMISSION-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/commission/pages/CommissionList.vue`
- `artifacts/AD-FE-COMMISSION-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/commission/pages/CommissionList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "prop=\"id\" label=\"编号\"|row\\.case_no \\|\\| row\\.case_id|\\{\\{ row\\.agent_id \\|\\| '—' \\}\\}|return map\\[status\\] \\|\\| status" frontend/src/modules/commission/pages/CommissionList.vue && rg -n "formatCaseDisplay|formatAgentDisplay|未命名案件|已分配|未知状态" frontend/src/modules/commission/pages/CommissionList.vue'
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-COMMISSION-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-COMMISSION-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-COMMISSION-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-COMMISSION-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-COMMISSION-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-COMMISSION-LIST-ID-DISPLAY-01/baseline_external_files.txt`
