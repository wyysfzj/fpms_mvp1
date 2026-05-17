# AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01 - consulting case create visible ID cleanup

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

Remove visible raw internal IDs and ID-oriented result terms from the consulting case creation page.

This closes only:

1. `ConsultingCaseCreate.vue` no longer renders `createdCase.id` as a visible case identifier.
2. `ConsultingCaseCreate.vue` no longer renders `createdCase.client_id` or `createdCase.primary_agent_id` as visible result text.
3. `ConsultingCaseCreate.vue` normalizes visible customer/responsible-person form/result terminology away from internal-ID wording while preserving the existing payload fields.
4. Unknown created-case status display on this page uses a Chinese placeholder rather than rendering the raw technical code.

## Explicit Non-Closure

This task does not:

- modify backend code, consulting API contracts, route params, permissions, response envelopes, or create/navigation behavior.
- add customer/agent selector APIs or any new readable customer/agent display contract.
- change required fields, validation semantics, case type options, payload shape, or success routing.
- close consulting fee draft, consulting profitability, case form/filter, or other consulting display issues.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01.md`
- `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`
- `artifacts/AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/consulting/pages/ConsultingCaseCreate.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "案件标识|客户编号|负责人编号|\\{\\{ createdCase\\.id \\}\\}|\\{\\{ createdCase\\.client_id \\|\\||\\{\\{ createdCase\\.primary_agent_id \\|\\||getCaseStatusText\\(createdCase\\.status\\)" frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue && rg -n "创建状态|formatCreatedCaseDisplay|formatLinkedDisplay|createdStatusText|客户为必填项|负责人为必填项" frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue'
./scripts/evidence_run.sh AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01/baseline_external_files.txt`
