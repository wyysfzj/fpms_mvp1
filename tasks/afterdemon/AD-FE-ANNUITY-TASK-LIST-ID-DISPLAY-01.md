# AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01 — annuity task list visible ID cleanup

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

Remove visible raw task/case/client/draft internal ID displays and raw status fallback text from the annuity task list page.

This closes only:

1. `AnnuityTaskList.vue` no longer renders the internal task `id` column.
2. `AnnuityTaskList.vue` case links use `case_no` or a Chinese fallback instead of `case_id`.
3. `AnnuityTaskList.vue` client cells use a Chinese association placeholder instead of `client_id`.
4. `AnnuityTaskList.vue` draft generation receipt tables do not render raw source task IDs, task IDs, or draft IDs.
5. `AnnuityTaskList.vue` unknown task/notice status fallback text is Chinese instead of the raw enum value.

## Explicit Non-Closure

This task does not:

- modify backend code, annuity API wrappers/types, route params, permissions, response envelopes, or task generation/draft payload contracts.
- add client-name, case-name, task-number, or draft-number resolution beyond fields already returned to this page.
- change filters, selection, instruction dialog behavior, generation dialog behavior, batch draft generation, date/money formatting, pagination, export, or print behavior.
- close raw-ID display issues outside `AnnuityTaskList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01`
- `AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01`
- `AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- `artifacts/AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/annuity/pages/AnnuityTaskList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "prop=\"id\" label=\"任务编号\"|row\\.case_no \\|\\| row\\.case_id|prop=\"client_id\" label=\"客户编号\"|prop=\"(source_task_id|task_id|draft_id)\" label=\"(来源任务编号|任务编号|草单编号)\"|\\{\\{ row\\.task_id \\?\\?|return status \\|\\| '未知'|return status \\|\\| '未知'" frontend/src/modules/annuity/pages/AnnuityTaskList.vue && rg -n "formatCaseDisplay|formatClientDisplay|formatGeneratedTaskDisplay|formatDraftDisplay|未知状态|已生成草单" frontend/src/modules/annuity/pages/AnnuityTaskList.vue'
./scripts/evidence_run.sh AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01/baseline_external_files.txt`
