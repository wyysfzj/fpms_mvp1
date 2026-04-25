# PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01

## Scope

This freezes the Batch 4 MVP product contract for `TC-A-002` / A1 full-field case creation.

## Confirmed MVP Contract

`TC-A-002` automation may assert the real backend-supported full-field save surface:

- case creation succeeds for a legal domestic invention case
- two applicants persist, with exactly one first applicant
- inventors persist
- two priorities persist
- one bio deposit persists
- document and billing address ids persist
- spec fields persist:
  - `spec_pages`
  - `draw_pages`
  - `claim_count`
  - `claim_pages`
  - `manuscript_words`
- fee/control fields persist:
  - `fee_reduction`
  - `discount_rate`
  - `no_power`
  - `no_prio_text`
  - `require_hk`
- created and updated audit timestamps are present
- case can be found through list/search and fetched through detail API

## PrioDate Decision

Do not add a case-level `prio_date` field for Batch 4.

MVP assertion surface:

- `priorities[]` is the source of truth
- automation computes `min(priorities[].prio_date)`
- that computed value is treated as the `PrioDate` behavior for `TC-A-002`

## GeneralPowerUsed Decision

`GeneralPowerUsed` is not a backend automation assertion for Batch 4.

Reason:

- current backend has no `GeneralPowerUsed` field or rule surface
- current testcase text says auto-check or suggestion, which may be UI/product behavior

Disposition:

- mark as `deferred_ui_or_product_decision`
- follow-up task id: `PRODUCT-A-GENERAL-POWER-CONTRACT-01`

## Backend Readiness Contract

`BE-A-CASE-A2-FULL-FIELDS-READINESS-01` should be test/readiness oriented unless discovery finds an actual persistence gap in the confirmed MVP surface.

## Automation Assertion Surface

`A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01` must not assert `GeneralPowerUsed` and must not require case-level `prio_date`.

It must assert full-field persistence and derived earliest priority date from priority rows.
