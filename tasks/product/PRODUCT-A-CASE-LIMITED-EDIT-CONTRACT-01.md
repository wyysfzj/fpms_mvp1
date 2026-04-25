# PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Freeze the TC-A-010 limited-edit MVP product/backend contract so backend and automation can proceed without guessing product semantics.

## Explicit Non-Closure

This task does not implement backend, frontend, pytest automation, schema migration, or UI changes.

## Remaining Follow-Up Task IDs

- BE-A-CASE-LIMITED-EDIT-RULE-01
- A-AUTO-PY-A-LIMITED-EDIT-P0-01
- BATCH-A-WAVE-CLOSE-AUDIT-01

## Allowed Files

- tasks/product/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01.md
- docs/product/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01.md
- artifacts/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01/**

## Verification Commands

```bash
./scripts/evidence_run.sh PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01 lint /bin/zsh -lc 'test -f tasks/product/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01.md && test -f docs/product/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01.md'
./scripts/evidence_run.sh PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01 test /bin/zsh -lc 'rg -n "TC-A-010|whitelist|blacklist|remarks|A-AUTO-PY-A-LIMITED-EDIT-P0-01" docs/product/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01.md'
./scripts/evidence_run.sh PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01 task_gate ./scripts/task_validate.sh PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01
```

## Evidence Path

- artifacts/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01/results.jsonl
- artifacts/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01/summary.md
- artifacts/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01/git/diff.patch
