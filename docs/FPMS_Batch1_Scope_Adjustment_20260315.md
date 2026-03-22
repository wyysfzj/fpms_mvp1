# FPMS Batch 1 Scope Adjustment Decision (2026-03-15)

## Purpose

This document records the approved Option A decision for `Batch 1` after execution evidence review.

Decision goal:
- keep `Batch 1` inside the original Case-domain intent
- avoid forced overreach into schema/model expansion
- avoid carrying forward a false `complete` status
- provide a clean basis for closing the actually completed subset and deferring blocked items into follow-up atomic tasks

## Decision Summary

`Batch 1` is scope-adjusted rather than force-closed as originally planned.

Approved direction:
- keep validated Case-domain backend and frontend subset work
- formally defer blocked or unproven sub-scope
- do not enter `Batch 2`
- do not add schema or migration work

Resulting status:
- original `Batch 1`: `not complete`
- adjusted `Batch 1A` close recommendation: `closable`

## Original Batch 1 Scope

Original covered `Partially Implemented` items:
- `US-CM-01`
- `US-CM-02`
- `US-CM-03`
- `FR-CM-02`
- `FR-CM-03`
- `FR-CM-04`
- `FR-CM-05`

Original implementation carriers:
- backend: `tasks/postenhancement/backend/PE-BE-CM-01.md`
- frontend: `tasks/postenhancement/frontend/PE-FE-CM-01.md`
- qa gate: `tasks/postenhancement/backend/PE-QA-CM-01.md`
- manifest: `tasks/postenhancement/BATCH1_CASES_MANIFEST_20260315.md`

## Evidence Review Basis

Primary evidence reviewed:
- `artifacts/PE-BE-CM-01/summary.md`
- `artifacts/PE-FE-CM-01/summary.md`
- isolated frontend lint/typecheck replay in clean temp copy
- Batch 1 execution and wave review conclusions

Evidence-supported conclusions:
- backend changes are substantial and validated on targeted checks
- frontend allowlist subset materially advances Batch 1 behavior
- frontend atomic close is not clean because current worktree includes many out-of-allowlist changes
- some original functional claims remain only partial or blocked

## Scope Adjustment Rule

The following rule is adopted for Batch 1 close readiness:

- keep only evidence-backed Case-domain gaps in adjusted `Batch 1A`
- move blocked schema-shaped or insufficiently proven scope into follow-up tasks
- do not claim full coverage for any item that lacks direct evidence

## Adjusted Batch 1A Scope

### Retained in Batch 1A

The following outcomes remain in adjusted `Batch 1A`:

- `US-CM-01`
  - create/update validation hardening
  - clearer frontend pre-submit validation
- `US-CM-02`
  - case-type driven conditional UI sections
  - API/type mapping for additional case fields
- `US-CM-03` partial
  - customer quick-create and backfill path
  - applicant quick-create / selection / backfill path
- `FR-CM-02`
  - same validation and conditional behavior improvements as above
- `FR-CM-03` partial
  - customer quick-create path
  - applicant quick-create / selection / backfill path
- `FR-CM-04`
  - status-related backend rules and readonly detail hints
- `FR-CM-05` partial
  - priority `0..n` capture/display/validation only

### Deferred out of Batch 1A

The following scope is deferred and must not be claimed as completed under Batch 1A:

- `FR-CM-03`
  - foreign-agent quick-create full loop
- `FR-CM-05`
  - bacteria deposit specific attributes
  - PCT international / national phase specific attributes
  - invalidation-case specific attributes
- any work that requires:
  - new persistent fields
  - ORM model expansion
  - schema changes
  - migration changes

## Deferred Scope Mapping

| Item | Deferred Portion | Why Deferred | Required Future Form |
|---|---|---|---|
| `FR-CM-03` | foreign-agent quick-create loop | current evidence now proves customer + applicant path, but not foreign-agent path | new atomic FE/BE tasks with direct evidence |
| `FR-CM-05` | bacteria deposit fields | no storage/model support in current allowlist | plan update + schema-aware follow-up task if approved |
| `FR-CM-05` | PCT phase fields | no storage/model support in current allowlist | plan update + schema-aware follow-up task if approved |
| `FR-CM-05` | invalidation-specific fields | no storage/model support in current allowlist | plan update + schema-aware follow-up task if approved |

## Why Scope Adjustment Is Required

### 1. Schema boundary

Backend evidence explicitly states that part of `FR-CM-05` cannot be completed inside the current no-schema constraint.

### 2. Evidence boundary

Frontend evidence does not support a clean atomic `PASS` for the original full task because:
- worktree contains unrelated frontend changes outside allowlist
- manual Case Create / Edit / Detail evidence is incomplete
- task-level gate evidence is incomplete

### 3. AGENTS compliance

AGENTS requires:
- exact atomic task ownership
- allowlist compliance
- evidence-backed `PASS`

Keeping the original Batch 1 definition would force an inaccurate completion claim.

## Revised Close Criteria For Adjusted Batch 1A

Adjusted `Batch 1A` may be closed only when all conditions below are met:

- backend `PE-BE-CM-01` remains `PASS`
- frontend `PE-FE-CM-01` is reclassified against retained scope only
- frontend `PE-FE-CM-02` closes the applicant quick-create / selection gap inside adjusted scope
- frontend evidence is normalized to the adjusted scope
- execution summary explicitly marks deferred portions as out of adjusted scope
- no claim is made that `FR-CM-03` or `FR-CM-05` are fully fixed

## Required Follow-up Tasks

The following follow-up tasks should be created before any future implementation of deferred scope:

- `Batch1-Followup-CM-03-ForeignAgent-QuickCreate`
- `Batch1-Followup-CM-05-Special-Patent-Attributes`

These should each be separate atomic tasks with their own:
- task file path
- allowlist
- verification set
- evidence folder

## Non-Goals

This decision does not authorize:
- `Batch 2`
- schema changes
- migration changes
- document generation features
- broad frontend cleanup outside current task evidence normalization

## Final Decision

Adopt Option A.

Interpretation:
- original `Batch 1` is not fully complete
- adjusted `Batch 1A` is the accepted close path from current evidence
- deferred portions must be tracked as new follow-up tasks, not hidden inside a false `PASS`

## Explicit Stop Line

Stopped after Batch 1 scope-adjustment decision.
No Batch 2 work is authorized by this document.
