# AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01 — commission settlement visible ID cleanup

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

Remove visible raw settlement/commission/case/agent internal ID displays and raw status fallback text from the commission settlement page.

This closes only:

1. `CommissionSettlement.vue` result/report tables no longer render raw `settlement_id`, `commission_id`, `case_id`, or `agent_id` as visible text.
2. `CommissionSettlement.vue` recent settlement table no longer renders raw batch IDs or agent IDs.
3. `CommissionSettlement.vue` creation/generation success UI no longer echoes generated internal batch IDs.
4. `CommissionSettlement.vue` unknown settlement/line status fallback text is Chinese instead of the raw enum value.

## Explicit Non-Closure

This task does not:

- modify backend code, commission API wrappers/types, commission list page, route params, permissions, response envelopes, or report/generation payload contracts.
- add agent-name, case-name, settlement-number, or commission-number resolution.
- change create/generate/report/export behavior, request parameters, filters, target-case generation, amount/date formatting, pagination, or permissions.
- close raw-ID display issues outside `CommissionSettlement.vue`.

## Remaining Follow-Up Task IDs

- `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01`
- `PRODUCT-FE-COMMISSION-BUSINESS-NUMBER-CONTRACT-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01.md`
- `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- `artifacts/AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/commission/pages/CommissionSettlement.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "\\{\\{ (lastGenerate\\.settlement_id|row\\.agent_id|row\\.case_id|row\\.settlement_id|row\\.commission_id) [^}]*\\}\\}|prop=\"(id|agent_id|case_id|settlement_id|commission_id)\" label=\"(编号|代理人编号|案件标识|批次编号|提成编号)\"|编号: \\$\\{settlement\\.id\\}|return map\\[status \\|\\| ''\\] \\|\\| status" frontend/src/modules/commission/pages/CommissionSettlement.vue && rg -n "formatAgentDisplay|formatCaseDisplay|formatBatchDisplay|formatCommissionDisplay|未知状态|已选择批次" frontend/src/modules/commission/pages/CommissionSettlement.vue'
./scripts/evidence_run.sh AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01/baseline_external_files.txt`
