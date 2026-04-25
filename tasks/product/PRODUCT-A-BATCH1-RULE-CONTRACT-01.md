# PRODUCT-A-BATCH1-RULE-CONTRACT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Freeze the Batch 1 product and backend rule contract for:

- TC-A-006 applicant list / applicant kind mismatch rules.
- TC-A-008 date and number consistency rules.
- Follow-up backend and automation task split needed to implement those contracts.

This task only creates the product contract document and evidence. It does not implement backend code, pytest handlers, frontend UI, migrations, or skeleton data changes.

## Explicit Non-Closure

- Do not modify backend service, models, schemas, API, or migrations.
- Do not modify pytest automation handlers or tests.
- Do not modify frontend UI.
- Do not modify skeleton YAML, JSON, manifest, schema, or Playwright assets.
- Do not run real smoke.
- Do not implement TC-A-006 or TC-A-008.
- Do not mark backend implementation complete from this contract task.

## Remaining Follow-Up Task IDs

- BE-A-APPLICANT-DATA-MODEL-01
- BE-A-APPLICANT-KIND-RULE-01
- BE-A-DATE-NUMBER-RULES-01
- A-AUTO-PY-A-APPLICANT-RULES-P0-02
- A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01

## Allowed Files

- tasks/product/PRODUCT-A-BATCH1-RULE-CONTRACT-01.md
- docs/product/PRODUCT-A-BATCH1-RULE-CONTRACT-01.md
- artifacts/PRODUCT-A-BATCH1-RULE-CONTRACT-01/**

## Verification Commands

```bash
test -f tasks/product/PRODUCT-A-BATCH1-RULE-CONTRACT-01.md
test -f docs/product/PRODUCT-A-BATCH1-RULE-CONTRACT-01.md
rg -n "TC-A-006|TC-A-008|CASE_APPLICANT_KIND_MISMATCH|CASE_PUBLISHED_FIELDS_REQUIRED|CASE_GRANTED_FIELDS_REQUIRED|CASE_FILING_BEFORE_PRIORITY|CASE_APP_NO_INVALID" docs/product/PRODUCT-A-BATCH1-RULE-CONTRACT-01.md
./scripts/task_validate.sh PRODUCT-A-BATCH1-RULE-CONTRACT-01
```

## Evidence Path

- artifacts/PRODUCT-A-BATCH1-RULE-CONTRACT-01/results.jsonl
- artifacts/PRODUCT-A-BATCH1-RULE-CONTRACT-01/summary.md
- artifacts/PRODUCT-A-BATCH1-RULE-CONTRACT-01/git/diff.patch
- artifacts/PRODUCT-A-BATCH1-RULE-CONTRACT-01/baseline_allowlist.diff
- artifacts/PRODUCT-A-BATCH1-RULE-CONTRACT-01/baseline_external_files.txt
