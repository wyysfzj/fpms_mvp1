# PD-P1-E2E-SAFE-SMOKE-CLEANUP-20260612-01 — Safe smoke fixture cleanup allowlist

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: medium
- `be_fe_coupling`: backend fixture only
- `evidence_cost`: medium

## chosen_runbook

`P0-single-lane-story`

## Exact Closure Slice

Create and verify a safe smoke/demo cleanup allowlist for P1 E2E fixture data. The cleanup may only delete explicitly listed fixture IDs whose ownership is proven by local seed/test files or prior evidence.

## Explicit Non-Closure

No wildcard deletion by prefix such as `SMOKE-*`, `P1E2E-*`, or `*-SMOKE`. No deletion of real, production-like, or unproven data. No product workflow implementation, CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, or Longxia email sending.

## Proposed Allowlist Inputs

Before implementation, inspect and cite exact ownership evidence from:

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.full-scope.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- Existing `artifacts/PD-P1-*/summary.md` that created or used smoke/demo fixture data

## Required Design

- Build an explicit table of deletable fixture IDs grouped by table/model.
- Require every row to include source evidence and reason for safe deletion.
- Implement cleanup in dry-run mode first.
- Only after dry-run evidence, allow an execution mode that deletes exact allowlisted IDs and their direct children.
- Refuse to run if an ID is not in the allowlist.

## Allowed Files

To be confirmed by the implementer before execution. Expected scope:

- A fixture cleanup helper under the Playwright support area or backend test support area.
- A targeted test or dry-run evidence script.
- `artifacts/PD-P1-E2E-SAFE-SMOKE-CLEANUP-20260612-01/**`

## Verification Commands

- Dry-run cleanup command showing exact IDs that would be deleted.
- Targeted test proving unlisted `SMOKE-*` records are not deleted.
- Task gate: `./scripts/task_validate.sh PD-P1-E2E-SAFE-SMOKE-CLEANUP-20260612-01`

## Done Definition

- Cleanup allowlist is explicit and evidence-backed.
- Dry-run output is generated before any delete mode.
- No wildcard prefix deletion exists.
- Verification proves unlisted smoke/demo-looking data is preserved.
- Evidence artifacts exist and task gate passes.

## Remaining Follow-Up Task IDs

None.
