# AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01 - case agent split editor ID wording cleanup

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Normalize visible internal-ID wording in the shared case agent split editor.

This closes only:

1. `CaseAgentSplitEditor.vue` no longer shows `代理人 ID` or `内部代理人 ID` as visible form text.
2. The component helper text no longer exposes implementation-style `[]` wording.
3. Internal `agent_id` model fields remain unchanged for API compatibility.

## Explicit Non-Closure

This task does not:

- modify backend code, case API wrappers/types, route params, permissions, response envelopes, or save behavior.
- add agent selector APIs or any new readable agent display contract.
- change case create/edit page labels outside this shared component.
- change row add/remove/update behavior, role values, validation rules, or emitted payload shape.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-CREATE-ID-LABELS-01`
- `AD-FE-CASE-EDIT-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01.md`
- `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
- `artifacts/AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/components/CaseAgentSplitEditor.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "代理人 ID|内部代理人 ID|清空为 \\[\\]" frontend/src/modules/cases/components/CaseAgentSplitEditor.vue && rg -n "请填写代理人、角色和分摊比例|label=\"代理人\"|placeholder=\"请输入代理人\"" frontend/src/modules/cases/components/CaseAgentSplitEditor.vue'
./scripts/evidence_run.sh AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-AGENT-SPLIT-EDITOR-ID-LABELS-01/baseline_external_files.txt`
