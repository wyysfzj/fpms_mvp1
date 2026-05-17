# AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01 - document wizard reply source ID wording cleanup

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

Normalize visible reply-source file ID wording in the document wizard edit step.

This closes only:

1. `DocumentWizard.vue` no longer shows `回复来源文件 ID` in the step hint or field label.
2. Internal `reply_to_id` field remains unchanged for API compatibility.

## Explicit Non-Closure

This task does not:

- modify backend code, document API wrappers/types, route params, permissions, response envelopes, or wizard submission behavior.
- add reply-source file lookup APIs or any new readable reply-source display contract.
- change parsing, row IDs, payload mapping, validation, file upload, task/fee generation, or any other wizard step.

## Remaining Follow-Up Task IDs

- `AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01.md`
- `frontend/src/modules/documents/pages/DocumentWizard.vue`
- `artifacts/AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/documents/pages/DocumentWizard.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "回复来源文件 ID" frontend/src/modules/documents/pages/DocumentWizard.vue && rg -n "回复来源文件和补充说明|step2-field-label\">回复来源文件" frontend/src/modules/documents/pages/DocumentWizard.vue'
./scripts/evidence_run.sh AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DOCUMENT-WIZARD-REPLY-ID-LABELS-01/baseline_external_files.txt`
