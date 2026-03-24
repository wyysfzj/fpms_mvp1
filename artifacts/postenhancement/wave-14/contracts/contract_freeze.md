# Wave 14 Contract Freeze

## Task
- Task ID: `PE-BE-AN-04`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-04.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/annuity/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-AN-04/**`
- Out of scope:
  - `backend/app/modules/annuity/api.py` (endpoint delivery belongs to `PE-BE-AN-05`)
  - router wiring, schema/model/migration edits
  - unrelated module refactors

## Service Contract Assumptions
- Service implements annuity-task to fee-draft generation for selected/eligible annuity tasks.
- Service is callable by AN-05 endpoint without changing endpoint envelope rules.
- Service returns deterministic generation result structure usable for batch success/failure reporting in AN-05.
- Service updates task/draft related state in one coherent transaction scope per batch unit.

## Idempotence Assumptions (Mandatory)
- Re-running generation for the same already-generated annuity task must not duplicate fee draft lines.
- Idempotence key is task-year granularity (at minimum: task identity + year context).
- Duplicate generation attempts must be deterministic:
  - either strict no-op with existing linkage reused, or explicit conflict classification.
- If conflict path is used, behavior should align with reserved annuity code semantics:
  - `ANNUITY_DRAFT_ALREADY_GENERATED` (planned `409` meaning).
- Partial batch retries must preserve previously successful items and only process remaining eligible items.

## PayNextYear Behavior Assumptions (Mandatory)
- When `PayNextYear=false` (default), generate draft details for current task year only.
- When `PayNextYear=true`, generation logic includes current year and next year (`YearNo+1`) for the same case where eligible.
- Next-year generation follows the same validation/idempotence rules as current year.
- If next-year target task/rate context is missing or ineligible, behavior is deterministic and traceable in result details (for AN-05 to surface).
- PayNextYear processing must not break single-run consistency of draft totals and task flags.

## Regression Risks
- Duplicate line risk:
  - weak idempotence checks can create repeated GOV/SERVICE fee lines on retry.
- Cross-year drift risk:
  - `PayNextYear=true` may generate year+1 lines incorrectly or without proper eligibility checks.
- Totals consistency risk:
  - draft header totals can become inconsistent with item lines after append/retry paths.
- Retry safety risk:
  - partial failures without stable re-entry behavior can cause non-deterministic batch outcomes.
- Scope risk:
  - edits outside `annuity/service.py` violate atomic allowlist.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product file for `PE-BE-AN-04`.
- [ ] Service supports annuity-task to fee-draft generation per task definition.
- [ ] Idempotence control prevents duplicate generation on rerun/retry.
- [ ] `PayNextYear` option behavior is implemented:
  - `false` -> current year only
  - `true` -> current year + next year path with equivalent guards
- [ ] Generated draft data remains internally consistent after create/append/retry paths.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-AN-04/results.jsonl`
  - `artifacts/PE-BE-AN-04/summary.md`
  - `artifacts/PE-BE-AN-04/git/diff.patch`
