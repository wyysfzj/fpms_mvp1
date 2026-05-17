# AD-FE-CASE-DETAIL-ID-DISPLAY-01 - case detail visible ID cleanup

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

Remove visible raw internal ID displays from the case detail page.

This closes only:

1. `CaseDetail.vue` no longer renders `foreign_agent_id` as the visible external agent fallback.
2. `CaseDetail.vue` no longer labels or renders `doc_address_id` / `bill_address_id` as visible address IDs.
3. `CaseDetail.vue` no longer labels or renders `original_case_id` as a visible original case ID.
4. `CaseDetail.vue` no longer renders `invalid_client_id` as the visible invalid-case client fallback.
5. `CaseDetail.vue` no longer renders `primary_agent_id`, `second_agent_id`, `draftor_id`, or `agent_splits[*].agent_id` as visible assignee/agent text.
6. The page uses existing readable fields where available and otherwise uses minimal Chinese business placeholders.
7. `CaseDetail.vue` unknown enum/status-like display fallbacks in the same detail surface use Chinese placeholders instead of rendering raw technical codes.

## Explicit Non-Closure

This task does not:

- modify backend code, case API wrappers/types, route params, permissions, response envelopes, or fetch behavior.
- add agent/address/original-case lookup APIs or any new cross-module data contract.
- change case create/edit/filter pages, case report pages, or agent split editor inputs.
- change relationship tabs, deadline/task/fee subcomponents, status transitions, validation, save behavior, navigation, or breadcrumbs beyond avoiding a visible raw route fallback where already possible.
- close raw-ID display issues outside `CaseDetail.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01`
- `AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01`
- `AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-DETAIL-ID-DISPLAY-01.md`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `artifacts/AD-FE-CASE-DETAIL-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-DETAIL-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/pages/CaseDetail.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-DETAIL-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-DETAIL-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "\\{\\{ caseData\\.foreign_agent_name \\|\\| caseData\\.foreign_agent_id|\\{\\{ caseData\\.doc_address_id \\|\\||\\{\\{ caseData\\.bill_address_id \\|\\||\\{\\{ caseData\\.original_case_id \\|\\||\\{\\{ caseData\\.invalid_client_name \\|\\| caseData\\.invalid_client_id|\\{\\{ caseData\\.primary_agent_id \\|\\||\\{\\{ caseData\\.second_agent_id \\|\\||\\{\\{ caseData\\.draftor_id \\|\\||\\{\\{ agentSplit\\.agent_id \\|\\||公文地址 ID|账单地址 ID|原案 ID|\\|\\| caseData\\.value\\.(fee_reduction|applicant_kind|case_type|patent_category|flow_dir)|return role \\|\\| " frontend/src/modules/cases/pages/CaseDetail.vue && rg -n "formatForeignAgentDisplay|formatAddressConfiguredDisplay|formatOriginalCaseDisplay|formatInvalidClientDisplay|formatAgentAssignmentDisplay|formatAgentSplitDisplay|formatUnknownCode" frontend/src/modules/cases/pages/CaseDetail.vue'
./scripts/evidence_run.sh AD-FE-CASE-DETAIL-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-DETAIL-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-DETAIL-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-CASE-DETAIL-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-CASE-DETAIL-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-CASE-DETAIL-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-DETAIL-ID-DISPLAY-01/baseline_external_files.txt`
