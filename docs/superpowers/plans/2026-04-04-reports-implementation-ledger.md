# REPORTS-LEDGER-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `family ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `REPORTS-LEDGER-01` | main thread | `docs/superpowers/specs/2026-04-04-reports-implementation-ledger-design.md`, `docs/superpowers/plans/2026-04-04-reports-implementation-ledger.md`, `tasks/postenhancement/backend/REPORTS-LEDGER-01.md`, `tasks/postenhancement/backend/REPORTS-QA-LEDGER-01.md` | Depends on current `#13` refresh baseline, mitigation ledger entry, and observed report-family product evidence | Freeze strict report-family implementation ledger and implementation priority for `#13` | No product implementation, no close update, no export/print/chart work |
| `REPORTS-QA-LEDGER-01` | monitor / main thread | `artifacts/REPORTS-LEDGER-01/**`, `artifacts/REPORTS-QA-LEDGER-01/**`, `tasks/postenhancement/backend/REPORTS-QA-LEDGER-01.md` | Runs after ledger closure | Audit evidence and close summary for the strict report-family ledger | No product-code changes |

## Family Execution Recommendation

- Reports ledger only:
  - `REPORTS-LEDGER-01`
- First family eligible for implementation after ledger:
  - `RPT-CASE`
- Explicitly deferred families for this planning wave:
  - `RPT-FEE`
  - `RPT-ANN`
  - any cross-report shell
  - any export / print / chart / drill-down work

## Serialized Shared-file Decisions

- This wave is doc-only; no FE/BE product shared files are touched
- Future family implementation must serialize shared ownership for:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
  - module-level `api.py|service.py|schemas.py` carriers

## Verification

- `./scripts/task_validate.sh REPORTS-LEDGER-01`
- `./scripts/task_validate.sh REPORTS-QA-LEDGER-01`

## Done Definition

- `#13` strict report-family ledger exists
- family-by-family classification is explicit:
  - `Implemented`
  - `Partially Implemented`
  - `Contract/Plan Only`
  - `Missing`
- first implementation family recommendation is explicit
- required artifacts exist and both task gates pass
