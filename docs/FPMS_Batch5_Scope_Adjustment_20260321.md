# FPMS Batch 5 Scope Adjustment Decision (2026-03-21)

## Purpose

This document records the approved scope-narrowing decision for `Batch 5` after execution and close-audit review.

Decision goal:
- keep the completed commission-domain work inside `Batch 5`
- avoid a false `complete` claim for consulting/search items that have no schema-safe exact closure slice
- formally move the consulting/search residual scope out of `Batch 5`
- provide a clean basis for closing the actually completed subset

## Decision Summary

`Batch 5` is scope-adjusted from `commission + consulting/search` to `commission-only`.

Approved direction:
- retain all evidence-backed commission slices
- remove `US-CS-01`, `FR-CS-01`, `US-CS-05`, `FR-CS-06` from Batch 5 adjusted scope
- do not fabricate a no-schema carrier for consulting/search-specific attributes
- do not treat blocked/deferred consulting/search work as part of the Batch 5 close decision

Resulting status:
- original `Batch 5` mixed scope: `not complete`
- adjusted `Batch 5A` close recommendation: `closable`

## Original Batch 5 Scope

Original in-scope `Partially Implemented` items:
- `US-COM-02`
- `US-COM-06`
- `FR-COM-02`
- `FR-COM-06`
- `FR-COM-07`
- `US-CS-01`
- `US-CS-05`
- `FR-CS-01`
- `FR-CS-06`

Original implementation carriers:
- manifest: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- backend tasks:
  - `tasks/postenhancement/backend/PE-BE-COM-01.md`
  - `tasks/postenhancement/backend/PE-BE-COM-02.md`
  - `tasks/postenhancement/backend/PE-BE-COM-03.md`
- frontend tasks:
  - `tasks/postenhancement/frontend/PE-FE-COM-01.md`
  - `tasks/postenhancement/frontend/PE-FE-COM-02.md`
  - `tasks/postenhancement/frontend/PE-FE-COM-03.md`
- qa task:
  - `tasks/postenhancement/backend/PE-QA-B5-01.md`

## Evidence Review Basis

Primary evidence reviewed:
- `artifacts/PE-BE-COM-01/summary.md`
- `artifacts/PE-FE-COM-01/summary.md`
- `artifacts/PE-BE-COM-02/summary.md`
- `artifacts/PE-FE-COM-02/summary.md`
- `artifacts/PE-BE-COM-03/summary.md`
- `artifacts/PE-FE-COM-03/summary.md`
- `artifacts/PE-QA-B5-01/summary.md`
- consulting/search freeze re-review against:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`
  - `frontend/src/api/consulting.ts`
  - `frontend/src/api/consulting.types.ts`

Evidence-supported conclusions:
- commission-domain slices are fully evidenced and independently gate-passing
- consulting/search UI currently collects project-specific fields that are not carried in API payloads
- backend consulting create flow has no durable consulting/search-specific attribute carrier
- no approved schema-safe exact closure slice exists for the consulting/search financial chain under current constraints

## Scope Adjustment Rule

The following rule is adopted for Batch 5 close readiness:

- keep only evidence-backed commission-domain gaps in adjusted `Batch 5A`
- move consulting/search residual scope out of Batch 5 adjusted scope
- do not claim consulting/search coverage without a schema-safe exact closure slice and direct evidence

## Adjusted Batch 5A Scope

### Retained in Batch 5A

The following items remain in adjusted `Batch 5A`:

- `US-COM-02`
  - manual bill to commission auto-generation slice
  - commission list stage / settleability visibility slice
- `FR-COM-02`
  - same narrowed auto-generation and visibility interpretation
- `US-COM-06`
  - settlement line generation marks `S1_Done / S2_Done`
  - settlement page stage completion visibility
- `FR-COM-06`
  - same narrowed settlement completion interpretation
- `FR-COM-07`
  - settlement report completeness on backend
  - settlement report detail visibility on frontend

### Moved out of Batch 5A

The following scope is moved out of adjusted `Batch 5A` and must not be claimed as completed under Batch 5:

- `US-CS-01`
- `FR-CS-01`
- `US-CS-05`
- `FR-CS-06`

## Moved-Out Scope Mapping

| Item | Moved-Out Portion | Why Moved Out | Required Future Form |
|---|---|---|---|
| `US-CS-01` | consulting/search-specific project attributes | no durable carrier under current no-schema rule | new explicit task after carrier approval |
| `FR-CS-01` | same project-attribute scope | same blocker as `US-CS-01` | new explicit task after carrier approval |
| `US-CS-05` | consulting/search billing / payment / commission chain parity | no approved narrow schema-safe exact slice | new explicit manifest after narrower split |
| `FR-CS-06` | consulting/search commission rule and settlement linkage parity | same deferred reason as `US-CS-05` | new explicit manifest after narrower split |

## Why Scope Adjustment Is Required

### 1. Carrier boundary

Frontend currently captures consulting/search-specific fields, but the API contract and backend persistence path do not carry them.

### 2. Exact-slice boundary

The cross-module consulting/search financial chain spans:
- `consulting`
- `billing`
- `commission`

Under current rules, no single approved no-schema exact closure slice exists that can honestly close `US-CS-05 / FR-CS-06`.

### 3. AGENTS compliance

`AGENTS.md` requires:
- exact closure slice
- explicit non-closure
- evidence-backed `PASS`

Keeping the original mixed Batch 5 scope would force an inaccurate completion claim.

## Revised Close Criteria For Adjusted Batch 5A

Adjusted `Batch 5A` may be closed only when all conditions below are met:

- `PE-BE-COM-01` remains `PASS`
- `PE-FE-COM-01` remains `PASS`
- `PE-BE-COM-02` remains `PASS`
- `PE-FE-COM-02` remains `PASS`
- `PE-BE-COM-03` remains `PASS`
- `PE-FE-COM-03` remains `PASS`
- `PE-QA-B5-01` is refreshed against adjusted scope only
- execution summary explicitly marks consulting/search residuals as out of adjusted Batch 5 scope

## Required Follow-up Work

The moved-out consulting/search scope should not be hidden inside Batch 5. If it is pursued later, it should start from:

- a new explicit manifest
- new atomic task file paths
- approved storage/carrier decision for project attributes
- new QA close audit

## Final Decision

Adopt Batch 5 scope adjustment.

Interpretation:
- original mixed `Batch 5` is not fully complete
- adjusted `Batch 5A` is the accepted close path from current evidence
- consulting/search residual scope is moved out of Batch 5 and must be handled by future explicit planning

## Explicit Stop Line

Stopped after Batch 5 scope-adjustment decision.
No later batch work is authorized by this document.
