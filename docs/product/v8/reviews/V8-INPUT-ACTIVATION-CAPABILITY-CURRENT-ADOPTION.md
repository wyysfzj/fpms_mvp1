# V8 Input Activation Capability — Current Adoption

Status: CAPABILITY EVIDENCE GREEN / INDEPENDENT REVIEW REQUIRED
Risk: PROTECTED
Recorded: 2026-08-13

This QA-only receipt closes the implemented input surfaces as
`CAPABILITY_READY + CONFIG_REQUIRED`. It does not supply or activate a production input.
The current source-decision registry keeps both production gates pending:

- `DG-PAYMENT-WORKBOOK:GLOBAL`
- `DG-SERVICE-RATE-VERSION:GLOBAL`

Until a reviewed real input and its matching gate are active, every production consumer remains
fail closed at `409 / NO WRITE`. `TEST_ONLY` inputs remain isolated from production resolution.

## Capability receipt

```json
{
  "capability": "CAPABILITY_READY",
  "payment_workbook": "CONFIG_REQUIRED",
  "service_rate": "CONFIG_REQUIRED",
  "production_activation_claimed": false
}
```

## Current dependency binding

The accepted successor dependency reviews bind commits `090b4b7`, `d2810c3`, and `2280839`.
Row 278 binds the cumulative implementation `6a17a18 + 97771c2` against the current bytes.
Independent row 278 review: APPROVED; P0/P1/P2: 0/0/0. Its amended live-workbook
Playwright verification reported `1 passed` in `8.0s`.

## Decisive inherited proofs

- `backend/tests/test_v8_payment_workbook_input_service.py::test_test_only_isolated_resolution_never_activates_or_becomes_current`
- `backend/tests/test_v8_payment_workbook_input_service.py::test_test_resolution_rejects_ambiguity_and_production_rejects_test_only`
- `backend/tests/test_v8_official_payment_workbook_generation_service.py::test_missing_or_test_only_production_input_fails_409_without_side_effects`
- `backend/tests/test_v8_official_payment_workbook_generation_service.py::test_missing_or_mismatched_production_gate_fails_without_write`
- `backend/tests/test_v8_service_price_book_import.py::test_test_only_requires_explicit_test_profile_and_retains_classification`
- `backend/tests/test_v8_service_price_book_activation.py::test_malformed_or_test_only_candidate_is_409_without_mutation`
- `backend/tests/test_v8_service_price_book_activation.py::test_missing_or_mismatched_gate_is_409`
- `backend/tests/test_v8_service_price_book_activation.py::test_test_runtime_and_same_creator_are_409`
- `backend/tests/test_v8_service_receivable_obligation.py::test_active_item_creates_service_obligation_and_caller_owns_transaction`
- `backend/tests/test_v8_service_receivable_obligation.py::test_noncanonical_book_hash_is_409_without_receivable_write`

The focused QA RED reported `3 failed, 1 passed`: only the absent receipt and unclosed task card
failed, while the direct missing service-price configuration proof passed `409 / NO WRITE`.
The focused GREEN reported `4 passed` in `1.65s`. The ten named decisive inherited nodes expanded
to 15 tests and reported `15 passed` in `4.38s`. Both runs emitted only two pre-existing
dependency deprecation warnings.

## Boundary

No product code, source input, gate decision, configuration, payment, official-fee fact, or
service-price fact is created or inferred by this receipt. Independent High review of this
task's exact commit remains required; this implementer record is not self-approval.
