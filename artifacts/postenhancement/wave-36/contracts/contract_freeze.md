# Wave 36 Contract Freeze

## Task
- Task ID: `PE-BE-CS-04`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-04.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/fees/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CS-04/**`
- Out of scope:
  - API endpoint wiring changes (owned by `PE-BE-CS-05`)
  - schema/model/migration edits
  - unrelated module refactors

## Service Strategy Contract
- Service responsibility:
  - generate consulting/search fee draft lines using deterministic strategy modes and persist traceable `t_fee_draft` + `t_fee_item` data.
- Applicable case scope:
  - only cases where `case_type in {"CONSULTING", "SEARCH"}`.
- Draft type mapping:
  - `CONSULTING -> CONSULT_FEE`
  - `SEARCH -> SEARCH_FEE`
- Draft defaults:
  - `status=OPEN`
  - `currency` from request or case/client default
  - totals recalculated from persisted lines after write.

## Supported Modes
- `FIXED`:
  - one fixed service line.
  - canonical line code examples: `CONSULT_FIXED` or `SEARCH_FIXED`.
- `HOURLY`:
  - one or more hourly lines, each representing role/work bucket.
  - canonical line code examples: `CONSULT_PARTNER_HOUR`, `CONSULT_SENIOR_HOUR`, `SEARCH_ANALYST_HOUR`.
- `HYBRID`:
  - fixed base line + one or more hourly lines.

## Deterministic Amount Formulas
- Line formula:
  - `line_amount = round(quantity * unit_price, 2)` (money quantization to 2 decimals).
- `FIXED`:
  - `quantity = 1`
  - `unit_price = fixed_fee`
  - `amount = fixed_fee`
- `HOURLY`:
  - for each line:
    - `quantity = hours`
    - `unit_price = hourly_rate`
    - `amount = round(hours * hourly_rate, 2)`
- `HYBRID`:
  - fixed line: same as `FIXED`
  - hourly lines: same as `HOURLY`
  - total is sum of all lines.
- Draft totals:
  - `total_service = sum(amount where fee_type=SERVICE)`
  - `total_gov = sum(amount where fee_type=GOV)` (normally `0` for consulting/search mode)
  - `total_misc = sum(amount where fee_type=MISC)` (optional reimbursable lines if strategy includes them)
  - `amount = total_service + total_gov + total_misc`

## Traceable Line-level Breakdown Contract
- Every generated `FeeItem` must be traceable to its source input:
  - persisted fields include `fee_code`, `fee_name`, `fee_type`, `quantity`, `unit_price`, `amount`.
  - line-level remark metadata should include source mode and role bucket (for hourly/hybrid), or fixed-base marker.
- Service result must expose line breakdown summary to caller:
  - per line: `fee_code`, `quantity`, `unit_price`, `amount`, `trace_key`.

## Service Interface Contract (for `PE-BE-CS-05`)
- Contracted callable (name can differ, semantics fixed):
  - input:
    - `db: Session`
    - `case_id: str`
    - `mode: Literal["FIXED", "HOURLY", "HYBRID"]`
    - `currency: str | None`
    - `fixed_fee: Decimal | None`
    - `hourly_lines: list[HourlyLineIn] | None` where each item has at least:
      - `fee_code`
      - `fee_name`
      - `hours`
      - `hourly_rate`
      - optional `remark`
    - optional `misc_lines` (if included by implementation strategy)
    - `actor_id: str | None`
  - output:
    - structured result with:
      - `draft_id`
      - `draft_type`
      - `mode`
      - `currency`
      - `totals` (`total_gov`, `total_service`, `total_misc`, `amount`)
      - `items` (traceable generated lines)
      - `created_line_count`

## Boundary Validations
- Case boundary:
  - `case_id` required and must exist (`404`).
  - case must be consulting/search type (`400` otherwise).
- Mode boundary:
  - `mode` must be one of supported values (`400` otherwise).
- Mode-specific requirements:
  - `FIXED`: `fixed_fee > 0`, no required hourly lines.
  - `HOURLY`: at least one hourly line; each line `hours > 0`, `hourly_rate >= 0`.
  - `HYBRID`: `fixed_fee >= 0`, at least one hourly line, and final total `> 0`.
- Numeric boundary:
  - all quantities/rates/amount inputs must be numeric and non-negative where applicable.
- Currency boundary:
  - normalized uppercase currency code; invalid/blank after normalization is `400`.

## Error Semantics
- `400`:
  - invalid mode/payload, invalid case type, invalid numeric boundaries.
- `404`:
  - case not found (or other required referenced entity missing).
- `409` (as applicable):
  - conflict in target draft state (for example generation into disallowed locked/conflicting scope if strategy enforces conflict guard).
- Preserve existing BusinessError envelope conventions.

## Regression Risks
- Formula regression:
  - non-deterministic rounding/order causes inconsistent totals across reruns.
- Traceability regression:
  - missing line source markers makes audit/reconciliation difficult.
- Mode-validation regression:
  - weak boundary checks produce malformed drafts/lines.
- Interface drift:
  - unstable service contract breaks `PE-BE-CS-05` API integration.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/fees/service.py`
- [ ] Service supports all three modes: `FIXED`, `HOURLY`, `HYBRID`.
- [ ] Mode formulas are deterministic and quantized consistently.
- [ ] Generated lines include traceable breakdown fields and source markers.
- [ ] Draft totals are recalculated from persisted line items.
- [ ] Service interface output is stable for `PE-BE-CS-05` endpoint integration.
- [ ] Validation/error behavior aligns with frozen `400/404/409` semantics.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CS-04/results.jsonl`
  - `artifacts/PE-BE-CS-04/summary.md`
  - `artifacts/PE-BE-CS-04/git/diff.patch`
