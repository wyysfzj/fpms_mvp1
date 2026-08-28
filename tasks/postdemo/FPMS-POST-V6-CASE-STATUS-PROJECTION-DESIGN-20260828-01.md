# FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01

Status: COMPLETE / SPEC REVIEWED / USER APPROVED
Risk-Tier: HIGH
Closure-Tags: ["api", "legal", "lifecycle", "ui"]
Task-Path: tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01.md

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Freeze one implementation-ready design that distinguishes the legacy case workflow status
from the authoritative lifecycle three-axis projection on case list and dashboard surfaces.
The design must preserve backward compatibility, expose explicit list API fields, correct
customer-visible labels, and restore the existing case update timestamp projection.

## Explicit Non-Closure

This design does not change product code, database schema, lifecycle transitions, legal
status rules, filing-date facts, historical data, permissions, demo seed values, or the
case-detail three-track projection. It does not deprecate or remove `Case.status`.

## Approved Design Boundary

- Keep `status` for backward compatibility and add `workflow_status` as its explicit API alias.
- Project `business_stage`, `official_procedure_stage`, `legal_status`, and `updated_at` on
  case list responses.
- Use workflow status for stage grouping and the "待授权" badge.
- Reserve lifecycle `legal_status` for actual legal-status wording.
- Rename visible workflow labels so they no longer claim to be legal status.
- Keep a missing `filing_date` as an unknown fact; display "待录入" and do not infer it.

## Allowed Files

- `tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01.md`
- `docs/superpowers/specs/2026-08-28-case-list-lifecycle-projection-design.md`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01/**`

## Remaining Follow-Up Task IDs

- `FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01`

## Verification Commands

```bash
./scripts/evidence_run.sh FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01 lint git diff --check -- tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01.md docs/superpowers/specs/2026-08-28-case-list-lifecycle-projection-design.md
./scripts/evidence_run.sh FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01 test shasum -a 256 tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01.md docs/superpowers/specs/2026-08-28-case-list-lifecycle-projection-design.md
./scripts/evidence_run.sh FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01 scope python3 scripts/evidence_scope.py finalize FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01
```

## Evidence Path

- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01/task.json`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01/results.jsonl`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01/summary.md`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-DESIGN-20260828-01/git/diff.patch`
