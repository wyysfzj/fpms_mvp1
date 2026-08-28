# FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["ui"]
Task-Path: tasks/frontend/FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01.md
Chosen runbook: `P0-single-lane-story`

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low

## chosen_runbook

P0-single-lane-story

## Exact Closure Slice

Prevent structured document metadata JSON from appearing as customer-visible document
content, and present the existing official deadline projection as Simplified Chinese fields
on the document detail page.

This closure includes exactly:

- map only the backend `description` projection into document content;
- preserve legacy plain-text descriptions through the backend's existing projection;
- show existing official due date, source, and confirmation status as Chinese fields;
- add focused V6 frontend contract assertions for those behaviors.

## Explicit Non-Closure

This task does not:

- change backend APIs, persistence, deadline semantics, evidence lineage, or lifecycle state;
- change document create/edit behavior;
- redesign other document, case, or demo pages;
- modify the existing untracked colleague guide.

## Allowed Files

- `frontend/src/api/documents.ts`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`
- `tasks/frontend/FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01.md`
- `artifacts/FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01 test /bin/zsh -lc 'cd frontend && node tests/demo-v6-lifecycle-ui-contract.mjs && npm run typecheck && npm run build'
```

```bash
./scripts/evidence_run.sh FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/api/documents.ts src/modules/documents/pages/DocumentDetail.vue tests/demo-v6-lifecycle-ui-contract.mjs --max-warnings 0'
```

## Evidence Path

- `artifacts/FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01/results.jsonl`
- `artifacts/FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01/summary.md`
- `artifacts/FE-DOCUMENT-DETAIL-STRUCTURED-CONTENT-20260828-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None.
