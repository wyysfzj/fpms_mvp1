# Story V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-SUCCESSOR-CURRENT-ADOPTION

- Status: `READY_FOR_REVIEW`.
- Risk: `PROTECTED`.
- Product/test commits:
  `ae26fc6db220a6f54dc85e8a7bfc7b16982131e5` and the independent-review correction
  `d5ea31f2293f2497e854029e7a6015c23aa6ac07`.
- Integration parent: `acf934bd050387c86bbe2ff7c43acf4dd61f1cfe`.
- Superseded catalog row after independent acceptance:
  `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01` (ordinal `61`).
- Authority: approved source decision
  `DEC-V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-20260809`, frozen successor contract
  `d754b8c`, and its independent zero-finding contract review `acf934b`.

## Observable outcome

Ordinary single create, wizard/batch create and ordinary edit persist document, deadline,
reply, task and fee-routing facts without changing the case lifecycle snapshot or appending
lifecycle activity. Legacy template status metadata remains readable configuration but is
not transition authority. Impact preview returns no direct case-status impact and carries
the approved Simplified-Chinese risk tip.

Two actor-aware `Doc.Edit` routes now confirm acceptance or OA lifecycle evidence. They
derive the actor from the current user, require an exact current independently approved
final official-PDF evidence version, apply the frozen semantics/deadline/OA-sequence rules,
own transaction commit/rollback and preserve exact idempotent replay or fail-closed
conflict behavior. Ordinary document creation never dispatches these events.

## Exact current-tree scope

Product paths:

- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/lifecycle_evidence_adapters.py`
- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/app/modules/documents/semantics.py`
- `backend/app/modules/documents/service.py`

Decisive tests:

- `backend/tests/test_v8_document_semantics_event_adapter.py`
- `backend/tests/test_v8_acceptance_notice_evidence_adapter.py`
- `backend/tests/test_v8_oa_notice_evidence_api.py`

Exact inherited alignment/fixture paths:

- `backend/tests/test_addgap_document_semantic_state_effect.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_document_impact_preview_api.py`
- `backend/tests/test_spec_alignment_e2e.py`
- `backend/tests/test_document_wizard_batch_create.py`

The wizard file changes only one prerequisite fixture value,
`fee_reduction: "0"`, after the first exact regression tranche proved eight requests
stopped at the current required CaseCreate field with HTTP 422 before reaching the named
shared seam. The same current-tree prerequisite stopped the direct alignment assertions in
`test_addgap_document_semantic_state_effect.py` and
`test_document_impact_preview_api.py`; those allowed alignment fixtures add only the same
explicit no-reduction value. No wizard assertion or product behavior changed.

The terminal-status alignment preserves the public protected-status HTTP check. A parent-
tree node rerun proved the public Case update returns HTTP 409 with
`CASE_STATUS_MANAGED_BY_LIFECYCLE`; the current test retains that assertion, then uses a
direct database fixture only to establish `GRANTED` before proving ordinary document POST
returns 201 and leaves `GRANTED` unchanged.

## TDD and current verification

The real current-tree RED ran the three decisive files before product edits and returned
`153 failed, 2 passed`. It proved the computed lifecycle routing property, neutral ordinary
operations and both dedicated routes were absent.

Minimum GREEN results:

- three decisive files: `155 passed` (`12 + 63 + 80`), zero failures;
- wizard/batch shared seam after the one-field prerequisite fixture correction:
  `8 passed`, zero failures;
- fresh exact 23-file affected tranche: `585 passed, 4 failed, 3 warnings` in
  `235.20s`;
- scoped Ruff: PASS;
- staged exact diff check: PASS.

Independent review found and the exact successor correction `d5ea31f` closed three
fail-closed/scope defects before adoption: invalid or missing document-template
configuration now returns the contract-required 409 rather than resource 404; a stored
evidence version with an invalid attachment identity or non-positive/non-integer version
number now fails 409 without dispatch; and the protected public Case-update 409 assertion
is retained before the terminal-state fixture. Correction RED was `2 failed` for the
404/409 mismatch and `4 failed` because invalid evidence identity reached dispatch.
Correction GREEN was `2 passed`, then `5 passed`; the full acceptance/OA decisive files
passed `147/147`, scoped Ruff and exact diff check passed.

The four remaining failures are the same unrelated current-tree OA_OUT reply-date/filter
baseline in `test_b2_reply_chain.py` and `test_spec_alignment_e2e.py`: the source OA_IN
reply date is already `None`, so pending/replied filters and two workflow date expectations
fail before and after this successor. This story does not change OA_OUT behavior and does
not absorb those failures. Independent review must verify that causal separation and rerun
the decisive checks plus the exact affected tranche.

## Non-goals and rollback

No generic dispatcher, grant-notice transition, new lifecycle event, schema/migration,
fee amount, deadline rule, evidence-kind expansion, public ordinary-document request
shape, adjacent cleanup or OA_OUT reply-date repair. Rollback reverts only
`ae26fc6db220a6f54dc85e8a7bfc7b16982131e5`; it must not rewrite lifecycle history or
accepted predecessor stories.
