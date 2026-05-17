# AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01 - commission rule visible ID and raw code cleanup

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

Remove visible internal commission-rule ID and raw code examples/fallbacks from the commission rule page.

This closes only:

1. `CommissionRuleList.vue` no longer renders the internal `id` column as a visible rule number.
2. Unknown case type / fee type display on this page uses Chinese placeholders rather than raw technical codes.
3. The rule dialog placeholders no longer show English technical code examples as user-facing helper text.

## Explicit Non-Closure

This task does not:

- modify backend code, commission API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- change rule create/update/toggle payloads, validation, filters, pagination, or table actions.
- convert text inputs to selectors or add shared display constants.
- close commission display issues outside `CommissionRuleList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-REPORT-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01.md`
- `frontend/src/modules/commission/pages/CommissionRuleList.vue`
- `artifacts/AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/commission/pages/CommissionRuleList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "prop=\"id\" label=\"编号\"|例如：(NORMAL|SERVICE|INBOUND|INV)|getCaseTypeText\\(row\\.case_type\\)|getFeeTypeText\\(row\\.fee_type\\)" frontend/src/modules/commission/pages/CommissionRuleList.vue && rg -n "formatCaseTypeText|formatFeeTypeText|未知案件类型|未知费用类型|请输入案件类型代码|请输入费用类型代码|请输入流程方向代码|请输入专利类别代码" frontend/src/modules/commission/pages/CommissionRuleList.vue'
./scripts/evidence_run.sh AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01/baseline_external_files.txt`
