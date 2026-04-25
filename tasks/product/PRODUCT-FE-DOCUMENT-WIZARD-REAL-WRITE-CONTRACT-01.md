# PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: low
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Freeze the frontend product contract for document wizard real-write semantics using existing backend `POST /documents/wizard/batch-create` behavior.

## Explicit Non-Closure

This task does not change frontend code, backend code, API schemas, document templates, task generation, fee generation, or attachments. It does not implement `FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01`.

## Remaining Follow-Up Task IDs

- FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01

## Allowed Files

- tasks/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md
- docs/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md
- artifacts/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01/**

## Verification Commands

- test -f tasks/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md
- test -f docs/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md
- rg -n "批量创建|最终提交|预览|task_rows|fee_rows|attachment_rows|MVP" docs/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md
- ./scripts/task_validate.sh PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01

## Evidence Path

- artifacts/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01/results.jsonl
- artifacts/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01/summary.md
- artifacts/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01/git/diff.patch
