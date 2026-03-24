# Wave 26 Contract Freeze

## Task
- Task ID: `PE-BE-COM-04`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-04.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/commission/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-04/**`
- Out of scope:
  - `backend/app/modules/billing/service.py` hook wiring (reserved for `PE-BE-COM-05`)
  - `backend/app/modules/commission/api.py`
  - schema/model/migration edits
  - unrelated module refactors

## Service Contract (Bill-triggered Commission Generation)
- Service responsibility:
  - when a bill is generated, derive commission base/amounts by case and rule, then create or update `t_commission`.
- Contracted function shape (implementation may rename but must keep semantics):
  - input:
    - `db: Session` (required)
    - `bill_id: str` (required)
    - `actor_id: str | None` (optional, audit)
    - `strict: bool = True` (optional; strict error behavior switch for future hook integration)
  - output:
    - structured summary object/dict with at least:
      - `bill_id`
      - `processed_cases`
      - `created_count`
      - `updated_count`
      - `skipped_count`
      - `items` (per-case action summary)
      - `status` (`APPLIED`, `NOOP`, or `FAILED_NON_BLOCKING` when `strict=False`)

## Rule Matching Priority and Effective-date Semantics
- Rule candidate baseline:
  - only `enabled=true` rules are candidates.
  - effective-date window must include billing reference date:
    - reference date = `bill.bill_date` if present, else current business date.
    - pass condition: `(effective_from is null or effective_from <= ref_date)` and `(effective_to is null or effective_to >= ref_date)`.
- Matching dimensions:
  - `fee_type` (service commission path should resolve to service-fee context)
  - `case_type`
  - `flow_dir`
  - `patent_category`
  - null rule fields are treated as wildcard dimensions.
- Deterministic priority when multiple rules match:
  - highest specificity first (most non-null dimension matches).
  - then latest `effective_from` (null last).
  - then largest `id` as final deterministic tie-break.
- No-match behavior:
  - no exception by default; case is marked skipped with reason `RULE_NOT_FOUND`.

## Idempotency Strategy (Same Bill Rerun)
- Hard requirement:
  - rerunning commission generation for the same `bill_id` must not create duplicate `t_commission` rows.
- Contracted strategy:
  - use deterministic upsert key at commission-row level:
    - `(case_id, agent_id, fee_type, rule_id)` for the current rule resolution.
  - for matched row: update-in-place (no new row).
  - for missing row: create exactly one row.
- Same-bill rerun outcome:
  - row count remains stable.
  - amounts/state converge to same values for identical source data (idempotent final state).
  - summary marks repeated runs as update/no-op instead of create duplicates.

## `T_Commission` Generate/Update Behavior
- Source scope:
  - process bill items tied to cases (`bill_item.case_id is not null`) in service-fee context.
- Field mapping on create:
  - `case_id`, `agent_id`, `rule_id`, `fee_type`
  - `base_fee` from bill-derived service base
  - `s1_rate`, `s2_rate` from matched rule
  - `s1_amount`, `s2_amount` computed deterministically from base + fixed amounts
  - `wait_pay`, `force_settle` inherited from matched rule
  - `status` initialized to open-state (`OPEN`) unless existing module convention dictates equivalent default
  - audit fields populated (`created_by`, `updated_by`)
- Field mapping on update:
  - recompute and overwrite mutable business fields from latest bill+rule snapshot:
    - `rule_id`, `base_fee`, `s1_rate`, `s2_rate`, `s1_amount`, `s2_amount`, `wait_pay`, `force_settle`, `updated_by`
  - do not reset settlement progress flags (`s1_done`, `s2_done`) if already true.
  - do not regress terminal settlement status without explicit later-task logic.

## Error Semantics and Non-intrusive Hook Behavior
- Strict mode (`strict=true`, default):
  - raise BusinessError for invalid business preconditions.
  - expected mappings for service-level domain errors:
    - `400`: invalid bill/rule data context (unsupported fee shape, invalid decimals, inconsistent case data).
    - `404`: bill or required related entity not found.
    - `409`: deterministic conflict where unique upsert target cannot be resolved safely.
- Non-intrusive mode (`strict=false`) for future billing hook (`PE-BE-COM-05`):
  - do not propagate exception to caller.
  - return summary with `status=FAILED_NON_BLOCKING` and reason details.
  - must not break existing billing API response contract.
  - partial-write behavior must be deterministic and documented (prefer all-or-none for one bill execution unit).

## SQLite / Migration Constraints
- No schema/migration/model changes in this task.
- ORM logic must remain SQLite-safe:
  - no PostgreSQL-specific SQL/operators/functions.
  - no reliance on `RETURNING` for correctness.
- Keep write window short to reduce SQLite lock exposure.

## Regression Risks
- Duplicate commission risk:
  - missing deterministic upsert key causes duplicate rows on rerun.
- Rule-selection drift risk:
  - non-deterministic tie-breaking changes selected rule across runs.
- Effective-date drift risk:
  - wrong reference-date or boundary handling selects wrong rule.
- Settlement-state corruption risk:
  - overwriting `s1_done/s2_done` on update breaks settlement integrity.
- Hook-intrusion risk:
  - unhandled service errors can fail bill generation flow in `PE-BE-COM-05`.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product file:
  - `backend/app/modules/commission/service.py`
- [ ] Service function contract implemented for bill-triggered commission generation/upsert.
- [ ] Rule matching enforces enabled + effective-date window + deterministic priority ordering.
- [ ] Same bill rerun is idempotent and does not create duplicate `t_commission` records.
- [ ] `t_commission` create/update mappings follow frozen field semantics.
- [ ] Error behavior supports strict mode and non-intrusive mode for future billing hook.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-04/results.jsonl`
  - `artifacts/PE-BE-COM-04/summary.md`
  - `artifacts/PE-BE-COM-04/git/diff.patch`
