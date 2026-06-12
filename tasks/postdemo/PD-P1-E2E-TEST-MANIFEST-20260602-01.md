# PD-P1-E2E-TEST-MANIFEST-20260602-01 — P1 full-scope E2E test manifest

## Objective

Implement the P1 full-scope test design and E2E UI regression suite for the completed post-demo P1 implementation.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. The task adds one Playwright spec, one test fixture helper, and evidence/design artifacts; no product source files are touched. |
| prereq_dependency_density | Medium. Requires a running frontend dev/preview server, deterministic API-contract fixtures, and existing P1 implementation/API evidence. |
| be_fe_coupling | Medium for verification, low for edits. The E2E suite spans real frontend pages and mocked P1 API contracts; backend persistence proof is referenced from prior P1 evidence. |
| evidence_cost | High. Requires targeted E2E, frontend checks, task gate, evidence validation, screenshots/traces when available, and final coverage ledger. |

chosen_runbook: `P0-frontend-heavy-story`

## Execution Waves

| Wave | Task file | Owner role | Closure slice | Dependency / serialization |
|---|---|---|---|---|
| 1 | `tasks/postdemo/PD-P1-E2E-UI-FULLSCOPE-20260602-01.md` | Main thread / QA engineer | Create and verify one full-scope Playwright E2E suite plus P1 test coverage ledger. | Serialized single-task execution. No parallel product edits. |

## Non-Closure

No backend, frontend product, database migration, CPC/OA direct submit, RPA, auto-signature, auto-payment, or Longxia mail-sending implementation.

## Follow-Up Task IDs

None planned if the full-scope suite passes. If the E2E run exposes product defects, create focused follow-up implementation tasks from the diagnose findings.
