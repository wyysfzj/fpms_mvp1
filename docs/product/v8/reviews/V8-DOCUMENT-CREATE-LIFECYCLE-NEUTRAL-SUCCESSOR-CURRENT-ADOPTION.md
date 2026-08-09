# Independent Review — V8 Document Create Lifecycle-Neutral Successor Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row61_successor_current_review`
- Integration parent: `acf934bd050387c86bbe2ff7c43acf4dd61f1cfe`
- Exact reviewed linear range:
  `acf934bd050387c86bbe2ff7c43acf4dd61f1cfe..f42d396ae783542f5548e816565d2560bdfffd2d`
- Product/test commits:
  `ae26fc6db220a6f54dc85e8a7bfc7b16982131e5` and
  `d5ea31f2293f2497e854029e7a6015c23aa6ac07`
- Adoption-story commits:
  `eb9256eedf9863e40a107f72a6b46eeea0b6ddb8`,
  `9b11d7b024cfa8e2e7f4f9665408ac44b72ef326`,
  `c12f4319c78f01dded2d3885029fe7d0f8557801`, and
  `f42d396ae783542f5548e816565d2560bdfffd2d`
- Story:
  `docs/product/v8/stories/V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-SUCCESSOR-CURRENT-ADOPTION.md`
- Frozen contract:
  `docs/product/v8/stories/V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-SUCCESSOR-CONTRACT.md`
- Integration binding: `UNBOUND` (the controller alone owns coverage-ledger binding and
  ordinal-61 activation)
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

## Independent scope and contract review

The exact range changes only the frozen five product paths, three decisive tests, four
named inherited alignment files, the one named wizard fixture file and this adoption
story. Ordinary single create, wizard/batch create and ordinary edit no longer apply
template status metadata to legacy or central lifecycle state and do not append lifecycle
activity. Document persistence, confirmed official-deadline storage, reply/task routing
and existing fee routing remain in place. The wizard change is exactly one prerequisite
fixture field, `fee_reduction: "0"`; no wizard assertion or product behavior changed.

The two exact dedicated routes require `Doc.Edit`, derive `actor_id` from the authenticated
user, own commit/rollback and return HTTP 200. Their strict request models expose only the
frozen client fields. Both adapters validate exact document/template semantics and one
current final independently approved official-PDF evidence version before dispatch. OA
also validates the confirmed stored deadline and exact case-sensitive template-code
mapping. Exact replay remains idempotent and bound-fact drift remains a lifecycle conflict.
Invalid or missing template configuration and invalid stored evidence identity now fail
409 without dispatch.

No generic dispatcher, grant-notice transition, schema/migration, fee amount, accepted
lifecycle rule, grant attachment transition or OA_OUT repair entered the range. The
terminal-status inherited test retains the protected public Case-update 409 assertion and
uses a direct database fixture only to reach the frozen ordinary-create neutrality seam.
The rollback boundary names both product/test commits and forbids lifecycle-history
rewrites.

## Fresh commands and observed results

From `backend/` on the reviewed current tree:

```text
pytest -q tests/test_v8_document_semantics_event_adapter.py \
  tests/test_v8_acceptance_notice_evidence_adapter.py \
  tests/test_v8_oa_notice_evidence_api.py
```

Result before the correction: `155 passed, 3 warnings`, exit 0. Fresh result after
`d5ea31f`: `159 passed, 3 warnings in 52.67s`, exit 0.

```text
pytest -q tests/test_v8_acceptance_notice_evidence_adapter.py \
  tests/test_v8_oa_notice_evidence_api.py
```

Result after the correction: `147 passed, 3 warnings in 48.44s`, exit 0.

```text
pytest -q tests/test_document_wizard_batch_create.py
```

Result: `8 passed, 3 warnings in 5.41s`, exit 0.

```text
pytest -q tests/test_b2_reply_chain.py::test_doc_template_cascade_rejects_illegal_status_regression
```

Result after the correction: `1 passed, 3 warnings in 1.93s`, exit 0.

```text
pytest -q tests/test_v8_document_semantics_event_adapter.py \
  tests/test_v8_acceptance_notice_evidence_adapter.py \
  tests/test_v8_oa_notice_evidence_api.py \
  tests/test_addgap_document_semantic_state_effect.py \
  tests/test_document_impact_preview_api.py \
  tests/test_b2_reply_chain.py \
  tests/test_spec_alignment_e2e.py \
  tests/test_v8_attachment_evidence_atomic_adapter.py \
  tests/test_v8_generated_attachment_evidence_adapter.py \
  tests/test_v8_oa_out_package_atomic_link.py \
  tests/test_v8_oa_prepared_activity.py \
  tests/test_v8_oa_external_submission_evidence.py \
  tests/test_v8_preliminary_started_evidence_api.py \
  tests/test_v8_preliminary_passed_evidence_api.py \
  tests/test_v8_rectification_notice_evidence_api.py \
  tests/test_v8_publication_notice_evidence_api.py \
  tests/test_v8_substantive_started_evidence_api.py \
  tests/test_v8_reexamination_started_evidence_api.py \
  tests/test_v8_application_rejection_evidence_api.py \
  tests/test_v8_application_withdrawal_evidence_api.py \
  tests/test_v8_application_abandonment_evidence_api.py \
  tests/test_v8_application_restoration_evidence_api.py \
  tests/test_document_wizard_batch_create.py
```

This exact frozen 23-file command included the three decisive tests, four inherited
alignment files and all sixteen shared-seam files listed in the contract, including the
wizard file. It ran before the narrow correction and returned
`585 passed, 4 failed, 3 warnings in 220.85s`, exit 1. The only failures were:

- `test_b2_reply_chain.py::test_oa_reply_records_date_without_auto_writeoff`
- `test_b2_reply_chain.py::test_document_list_can_filter_by_reply_state`
- `test_b2_reply_chain.py::test_full_oa_lifecycle`
- `test_spec_alignment_e2e.py::test_e2e_oa_workflow`

The correction cannot affect those OA_OUT reply-date/filter paths: it changes only the
acceptance/OA reviewed-evidence guard, its decisive tests and the separately rerun
terminal-status inherited node.

Scoped Ruff ran first on all thirteen changed Python product/test paths and then freshly on
the four correction paths:

```text
ruff check app/modules/documents/lifecycle_evidence_adapters.py \
  tests/test_b2_reply_chain.py \
  tests/test_v8_acceptance_notice_evidence_adapter.py \
  tests/test_v8_oa_notice_evidence_api.py
```

Result: `All checks passed!`, exit 0. `git diff --check acf934b..f42d396` also returned
exit 0, and `git status --short` was empty before receipt creation.

## Causal baseline attestation

I created a read-only Git archive of `backend/` at exact parent
`acf934bd050387c86bbe2ff7c43acf4dd61f1cfe`, extracted it under `/tmp`, and ran the same
four failing node IDs there:

```text
pytest -q \
  tests/test_b2_reply_chain.py::test_oa_reply_records_date_without_auto_writeoff \
  tests/test_b2_reply_chain.py::test_document_list_can_filter_by_reply_state \
  tests/test_b2_reply_chain.py::test_full_oa_lifecycle \
  tests/test_spec_alignment_e2e.py::test_e2e_oa_workflow
```

The parent snapshot returned the same `4 failed, 3 warnings`
for the same reply-date/filter assertions: source OA_IN `reply_date` was already `None`,
and the replied/pending filter consequently disagreed. This proves the four remaining
tranche failures are unchanged current-tree OA_OUT baseline and were not caused by
`ae26fc6` or `d5ea31f`. No parent or candidate product/test file was changed for this
comparison.

## Exact identities

- cumulative binary patch SHA-256 for `acf934b..f42d396`:
  `492c6f578957b70f47f8848046bbd9f5f4aad6a9f6b248b0449f5ac6c7da0512`
- correction binary patch SHA-256 for `9b11d7b..d5ea31f`:
  `8793c92c1d3d2c8a7ff01dc99a9a6c3469157c10a3487b36688247fdf0a3ddb6`
- adoption-story SHA-256:
  `742c918a8cab0fd16d1af50428c4b02f2ae64f91d2f55c31d233f3bda50e08ab`
- adoption-story Git blob:
  `e6c82fd65b125ab9f867cbb1afd1bf19531c004f`

This receipt approves only the exact reviewed range and story bytes above. It does not
edit or bind the coverage ledger, activate ordinal 61, approve a grant/OA_OUT successor,
or claim a Foundation, release or production milestone.
