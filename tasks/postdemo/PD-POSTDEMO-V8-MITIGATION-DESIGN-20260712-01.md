# PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01

## Design References

- `AGENTS.md`
- `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`
- `artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/analysis/source_ledger.md`
- `docs/superpowers/specs/2026-07-10-fpms-additional-gap-mitigation-design.md`
- `docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md`

## Story Shape Classification

- `shared_file_density`: low for this documentation task; one new design document plus the required authoritative source-index registration in `AGENTS.md`.
- `prereq_dependency_density`: high; the design must reconcile closed Additional-GAP work, current implementation evidence, fixed legal/process rules, and customer-dependent decision gates before any plan may be written.
- `be_fe_coupling`: high in the future implementation; the current task is documentation-only and freezes tier-spanning interfaces without changing code.
- `evidence_cost`: high; every implementation standard must trace to the accepted re-review, customer sources, official rules, current code, or accepted task evidence.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Create one canonical V8 post-demo mitigation design that becomes the authoritative standard for the next implementation plan and subsequent execution. The design must subtract already accepted Additional-GAP work, define the remaining three-lane domain contracts and deep-module seams, isolate unresolved customer choices behind explicit decision gates, prescribe migration and execution-wave dependencies, and define atomic planning and acceptance requirements. Register the new authoritative design in `AGENTS.md` as required by the source-index rule.

## Explicit Non-Closure

Do not create the implementation plan or atomic implementation-task manifest, modify V7/V6 historical demo documents, decide unresolved customer policies, change backend/frontend/database/migrations/seed/tests, implement XML generation or official-system integration, execute a UI demo, commit, push, or claim that any residual implementation GAP is closed.

## Allowed Files

- `AGENTS.md`
- `tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `artifacts/PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01/**`

## Verification Commands

- `rg -n "Authority|Story Shape Classification|Closed-work subtraction|Decision gates|Deep modules|Lifecycle|Document evidence|Fee obligation|Migration|Execution waves|Atomic task standard|Acceptance|Non-goals" docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `rg -n "2026-07-12-fpms-postdemo-three-lane-mitigation-design" AGENTS.md`
- `git diff --check -- AGENTS.md tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01.md docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `./scripts/task_validate.sh PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01`

## Evidence Path

- `artifacts/PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01/`

## Done Definition

- The design has explicit authority and supersession rules relative to V7 and prior mitigation documents.
- Every accepted Additional-GAP closure is treated as inherited foundation rather than planned again.
- Fixed legal/customer rules are separated from unresolved customer policy/version decisions.
- The lifecycle, document-evidence, fee-obligation, and lifecycle-overlay modules have small interfaces, invariants, error semantics, and observable acceptance behavior.
- Schema/migration, compatibility, sequencing, shared-file serialization, SQLite, Simplified Chinese UI, and evidence requirements are explicit.
- The next writing-plans session can derive an atomic batch manifest without reopening broad source analysis.
- Required evidence, dirty-baseline artifacts, independent design review, atomic validation, and repository task gate pass.

## Remaining Follow-Up Task IDs

- `PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01`
