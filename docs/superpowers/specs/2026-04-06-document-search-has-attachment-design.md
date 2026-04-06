# Document Search Has Attachment Design

Date: 2026-04-06

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

- P0-frontend-heavy-story

## Problem Statement

`FPMS SPEC 2.0` section `3.8.1` requires the document-specific search page to support filtering by whether a document has attachments.

Current implementation provides document search filters for document name, direction, case, template, doc type, date range, reply state, and client, but does not provide an attachment-existence filter.

## Exact Closure Slice

Close exactly one residual:
- document-specific search supports `has_attachment` filtering through:
  - backend query contract
  - backend query semantics
  - frontend selector / user path
  - targeted tests

## Non-Closure

- no export
- no result column expansion
- no attachment count display
- no detail-page changes
- no attachment preview / generation
- no doc generation
- no other Module 2 residuals

## Existing Carrier

- `Document.attachments` already exists
- `DocumentOut.attachments` already exists
- no new schema or migration is required

## Backend Semantics

- `has_attachment=true`: return only documents with at least one attachment
- `has_attachment=false`: return only documents with no attachments
- omitted parameter: no attachment filter applied

Implementation should use attachment existence semantics based on the existing document-attachment relationship.

## Frontend Semantics

Add a Simplified Chinese selector to the document search page:
- 全部附件状态
- 有附件
- 无附件

The selector must flow into the existing `/documents` query path.

## Shared Ownership Files

- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentList.vue`
- `backend/tests/test_document_specific_search_api.py`

These files must be edited in serialized ownership across waves.

## Verification Targets

- backend targeted pytest for document-specific search
- frontend lint on touched files
- frontend typecheck
- task gates and evidence artifacts

## Prerequisite Judgment

- no prerequisite
- no schema change
- directly implementable on current carriers
