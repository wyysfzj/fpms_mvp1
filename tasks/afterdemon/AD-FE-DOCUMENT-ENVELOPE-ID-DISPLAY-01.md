# AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01 - document envelope visible ID cleanup

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

Remove visible route document ID and raw address-source fallback from the document envelope print page.

This closes only:

1. `DocumentEnvelopePrint.vue` no longer renders `documentId` as `文档编号`.
2. Unknown address source display on this page uses a Chinese placeholder rather than rendering the raw technical code.

## Explicit Non-Closure

This task does not:

- modify backend code, document API wrappers/types, route params, permissions, response envelopes, or envelope preview fetch behavior.
- change print behavior, address source semantics, recipient/address display, navigation, or dispatch pages.
- close document display issues outside `DocumentEnvelopePrint.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01.md`
- `frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue`
- `artifacts/AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/documents/pages/DocumentEnvelopePrint.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "文档编号|\\{\\{ documentId \\}\\}|return value \\|\\| '-'" frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue && rg -n "当前文档|未知地址来源" frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue'
./scripts/evidence_run.sh AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01/baseline_external_files.txt`
