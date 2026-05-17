# AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01 - consulting fee draft visible ID cleanup

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

Remove visible raw internal draft/item IDs from the consulting fee draft creation page.

This closes only:

1. `ConsultingFeeDraftCreate.vue` no longer renders `result.draft_id` as the visible draft number.
2. `ConsultingFeeDraftCreate.vue` no longer renders `result.items[*].item_id` as a visible table column.
3. `ConsultingFeeDraftCreate.vue` no longer includes backend `draft_id` in the user-facing conflict error message.
4. Unknown fee type display on this page uses a Chinese placeholder rather than rendering the raw technical code.

## Explicit Non-Closure

This task does not:

- modify backend code, consulting API contracts, route params, permissions, response envelopes, or create behavior.
- add fee draft lookup/navigation or any new readable draft/item identifier contract.
- change the request payload, amount calculation, line validation, mode behavior, currency behavior, trace keys, or table data mapping except for display-only item ID visibility.
- close consulting case creation, consulting profitability, case form/filter, or other consulting display issues.

## Remaining Follow-Up Task IDs

- `AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01`
- `AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01`
- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01.md`
- `frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue`
- `artifacts/AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/consulting/pages/ConsultingFeeDraftCreate.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "\\{\\{ result\\.draft_id \\}\\}|prop=\"item_id\"|label=\"费用项编号\"|details\\?\\.draft_id|\\$\\{draftId\\}|return type$" frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue && rg -n "生成状态|formatDraftDisplay|lineDisplayText|未识别费用类型" frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue'
./scripts/evidence_run.sh AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CONSULTING-FEE-DRAFT-ID-DISPLAY-01/baseline_external_files.txt`
