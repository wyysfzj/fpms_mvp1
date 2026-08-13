# FPMS V8 Full-Suite Case-Create Input Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align the inherited full-suite case creation fixtures exposed by the failed Row283 backend
matrix lane with the current reviewed request contract. Positive and behavior-targeted creates
must explicitly send canonical `fee_reduction`; callers must not send server-owned create
`status`. Tests that need a historical non-default status establish it only after a successful
canonical create.

## Exact RED and closure

The one Row283 full-backend run ended with `5917 passed / 204 failed / 23 errors`. Exactly seven
failures belong to separate Final/governance/concurrency checks. The remaining 197 failures and
23 setup errors are downstream of inherited case-create inputs: the log contains 194
`fee_reduction` references, 192 `422 == 201` assertions, and 41 detailed responses containing
both rejected `status` and missing `fee_reduction`.

This task may only:

- add literal canonical `"fee_reduction": "0"` (or the existing scenario-specific canonical
  value) to positive and behavior-targeted case-create inputs;
- remove obsolete create-time `status="NOT_FILED"` because the service owns that exact default;
- for report/annuity fixtures that require another historical state, create canonically first
  and then seed only that test projection through its existing transaction fixture;
- move the two historical publication/grant missing-field checks from forbidden create-status
  input to the current full-update boundary while preserving their exact business errors.

## Non-closure

- No product, schema, migration, seed, API validation, permission, fee, lifecycle or registry
  change.
- No shared fixture/conftest injection, assertion deletion, skip, xfail, fallback default or
  broad cleanup.
- No change to the seven distinct Final/governance/concurrency failures.
- No Row283 report/story/ledger/receipt or release claim. The failed broad run is not reused as
  PASS; Row283 may restart only after this task is independently approved.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-CASE-CREATE-INPUT-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_annuity_e2e.py`
- `backend/tests/test_annuity_generate.py`
- `backend/tests/test_annuity_report.py`
- `backend/tests/test_annuity_targeted_generation_api.py`
- `backend/tests/test_apply_bill_readiness.py`
- `backend/tests/test_apply_bill_unhappy.py`
- `backend/tests/test_apply_fee_draft_rule.py`
- `backend/tests/test_apply_fee_item_validation.py`
- `backend/tests/test_apply_fee_limit_base_source.py`
- `backend/tests/test_apply_fee_limit_task_fields.py`
- `backend/tests/test_apply_gov_paylist_readiness.py`
- `backend/tests/test_b5_billing_polish.py`
- `backend/tests/test_b6_search_filters.py`
- `backend/tests/test_case_a7_inventor_address_rule.py`
- `backend/tests/test_case_advanced_filters_api.py`
- `backend/tests/test_case_agent_split_api.py`
- `backend/tests/test_case_applicant_kind_rule.py`
- `backend/tests/test_case_applicant_masterdata_link_write_path.py`
- `backend/tests/test_case_batch_filing_action.py`
- `backend/tests/test_case_batch_filing_document_gate_query.py`
- `backend/tests/test_case_batch_filing_document_gate_submit.py`
- `backend/tests/test_case_batch_filing_query.py`
- `backend/tests/test_case_batch_filing_side_effects.py`
- `backend/tests/test_case_date_number_rules.py`
- `backend/tests/test_case_document_gate_api.py`
- `backend/tests/test_case_fields.py`
- `backend/tests/test_case_intake_document_gate_api.py`
- `backend/tests/test_case_limited_edit_rule.py`
- `backend/tests/test_case_receipt_crud.py`
- `backend/tests/test_case_report.py`
- `backend/tests/test_case_search.py`
- `backend/tests/test_case_spec_fee_discount_rule.py`
- `backend/tests/test_case_type_combo_rule.py`
- `backend/tests/test_commission_e2e.py`
- `backend/tests/test_commission_rule_seed_readiness.py`
- `backend/tests/test_commission_waitpay_threshold.py`
- `backend/tests/test_doc_dispatch_envelope.py`
- `backend/tests/test_doc_dispatch_handoff.py`
- `backend/tests/test_doc_dispatch_mailing_action.py`
- `backend/tests/test_document_list_export_api.py`
- `backend/tests/test_document_template_render_context.py`
- `backend/tests/test_document_wizard_attachment_preview.py`
- `backend/tests/test_document_wizard_fee_preview.py`
- `backend/tests/test_fee_report.py`
- `backend/tests/test_flows.py`
- `backend/tests/test_gov_paylist_validation_mvp.py`
- `backend/tests/test_offset_list.py`
- `backend/tests/test_payment_bill_linkage_api.py`
- `backend/tests/test_payment_offset_case_receipt_readiness.py`
- `backend/tests/test_pd_p1_case_official_fields_api.py`
- `backend/tests/test_prepayment_reporting_api.py`
- `backend/tests/test_task_reminder_response.py`
- `backend/tests/test_v3_workflow.py`

## Verification and acceptance

Run the exact 58 affected files from the failed log, including unchanged import-consumers, then
scoped Ruff and exact diff-check. Every prior request-contract failure must close; any newly
reached distinct assertion remains explicit non-closure unless separately authorized. An
independent High review must approve P0/P1/P2 `0/0/0` before Row283 resumes.

## Current verification result

The initial fresh exact 58-file run completed `252 passed / 30 failed` in `135.02s`. Independent
review rejected that candidate because it had replaced existing `0.85` scenarios with no
reduction. The amendment restores those exact non-zero scenarios and original amount assertions,
seeds current applicant-scoped approval evidence, and retains the current maximum supported
`0.85` boundary in the specification test.

The fresh exact 58-file rerun on the amended bytes completed `252 passed / 30 failed` in
`136.71s`. All restored fee-reduction scenarios pass through exact applicant-scoped approval and
retain their original reduced amount assertions. The 30 remaining failures are causally distinct
current-contract gaps reached after this task's boundary: annuity obligation lineage,
application-fee obligation/activation, batch-filing lifecycle/evidence, one applicant update
explicit-selection boundary, one A2 unsupported canonical-value boundary, grant template/manifest
maintenance, and the official-package archive gate. They are not changed or claimed closed by
this task.
