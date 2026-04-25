# PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01

## Scope

This freezes the Batch 4 MVP product contract for `TC-A-007` / inventors and addresses.

## Confirmed MVP Contract

Batch 4 automation may assert only the current stable backend-supported behavior:

- non-strict normal case can be saved with no inventors
- legal document and billing address ids can be saved
- address id belonging to another client is rejected
- stable backend error for wrong-client address: `CASE_ADDRESS_CLIENT_MISMATCH`

## Deferred Product Decisions

The following skeleton branches remain `product_decision_required` and are not Batch 4 MVP automation assertions:

- strict-country inventor-required warning/block
- disabled/stopped address representation and validation
- warning/block when both document and billing addresses are empty

Reasons:

- no country configuration to map country -> inventor-required rule was found
- current client address model/API does not expose an active/disabled flag
- current backend allows empty document and billing address fields
- there is no existing warning envelope to reuse safely

## Backend Readiness Contract

`BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01` should preserve existing behavior and add focused readiness evidence for the MVP surface. It must not invent strict-country or disabled-address semantics.

## Automation Assertion Surface

`A-AUTO-PY-A-FOREIGN-COMBO-P1-01` must assert:

- no-inventor save succeeds
- valid doc/bill address save succeeds
- wrong-client address is rejected with `CASE_ADDRESS_CLIENT_MISMATCH`

It must not fake strict-country or disabled-address behavior.
