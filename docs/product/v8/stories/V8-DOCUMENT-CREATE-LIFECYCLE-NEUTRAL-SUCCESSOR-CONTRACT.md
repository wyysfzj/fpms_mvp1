# V8 Document Create Lifecycle-Neutral Successor Contract

- Status: `CONTRACT_FROZEN / IMPLEMENTATION_PENDING`.
- Risk: `PROTECTED`.
- Superseded catalog row after implementation acceptance:
  `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01` (ordinal 61).
- Decision authority:
  `DEC-V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-20260809` in
  `docs/product/v8/source-decision-registry.md`.
- Inspection base: `ff4308e26016e714f09f39221d5a7f1ad2be7447`.
- Archive implementation input only (not acceptance):
  `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Conflict resolved

The old row-61 closure required ordinary document creation to dispatch a non-grant
lifecycle event. That requirement conflicts with the higher V8 domain contract: central
legal state changes require a confirmed command containing actor identity, reviewed
evidence references, effective time and an idempotency key. `DocumentCreateIn` and the
ordinary create endpoint supply none of those facts.

The approved decision resolves the conflict fail-closed. Ordinary document persistence is
not evidence confirmation and cannot itself change lifecycle truth. The current tree has
the accepted pure acceptance/OA lifecycle rules but no acceptance/OA evidence adapters or
API routes; the accepted ordinals 78–87 story explicitly excluded them. This successor
therefore closes that exact gap with two dedicated reviewed-evidence adapters while making
ordinary document operations neutral. It does not implement a generic dispatcher. Row 61
is superseded only after the complete neutral-plus-two-adapter successor is current-tree
verified.

## Observable outcome

For ordinary single create, wizard/batch create and ordinary edit:

1. Creating or editing an inbound executable document never applies
   `ResolvedDocumentSemantics.case_status_effect` to `Case.status`.
2. Creating or editing an outbound reply never applies `DocTemplate.status_restore` to
   `Case.status`.
3. No central lifecycle projection, lifecycle revision or lifecycle activity is changed
   or appended by those operations.
4. Document persistence, `need_reply`, confirmed official-deadline storage, reply linkage,
   task routing and exact existing fee-routing behavior remain unchanged.
5. The impact preview does not claim that ordinary registration will change or restore
   case status. When a selected template carries legacy `status_effect` or
   `status_restore` metadata, the preview returns no `CASE_STATUS` or
   `CASE_STATUS_RESTORE` impact and includes the Simplified-Chinese risk tip:
   `文书登记不会直接变更案件法律状态；请通过已复核证据的生命周期入口确认状态变化`.
6. Template status metadata remains readable compatibility/configuration data. It is not
   transition authority.
7. The exact dedicated routes
   `POST /documents/{document_id}/lifecycle/acceptance-notice` and
   `POST /documents/{document_id}/lifecycle/oa-notice` require `Doc.Edit`, derive
   `actor_id` from the authenticated user, own commit/rollback and return HTTP 200.
8. Both routes accept exactly `evidence_version_id`, `effective_at`, optional
   `occurred_at` and `idempotency_key`; extra fields fail 422. Business timestamps are
   naïve, stored identities are exact and bounded, and the client cannot supply case,
   event type, evidence kind, confirmation state, reviewer, OA sequence, template code or
   official deadline.
9. Acceptance dispatches only `ACCEPTANCE_NOTICE_RECORDED` from an inbound executable
   `ACCEPTANCE_NOTICE` document and one current final independently approved
   `OFFICIAL_FINAL_PDF` evidence version of that exact case/document.
10. OA dispatches only `OA_NOTICE_RECORDED` from an inbound enabled executable `OA_REPLY`
    document, one equivalent exact reviewed evidence version, the document's exact
    confirmed official-deadline snapshot and the frozen template-code-to-sequence mapping.
    It never accepts or infers OA sequence from a filename, amount, title or mutable case
    status.

`ResolvedDocumentSemantics` exposes one read-only computed property
`lifecycle_event_type` without changing its dataclass field list or `asdict()` result:

| `execution_behavior` | computed value |
| --- | --- |
| `ACCEPTANCE_NOTICE` | `ACCEPTANCE_NOTICE_RECORDED` |
| `OA_REPLY` | `OA_NOTICE_RECORDED` |
| `GRANT_NOTICE` | `GRANT_REGISTRATION_NOTICE_RECORDED` |
| every other value | `None` |

The property is routing metadata for dedicated adapters. Ordinary document operations
must not dispatch it.

## Exact implementation closure

Expected product paths:

- `backend/app/modules/documents/semantics.py`;
- `backend/app/modules/documents/service.py`;
- `backend/app/modules/documents/lifecycle_evidence_adapters.py`;
- `backend/app/modules/documents/official_notice_catalog.py`;
- `backend/app/modules/documents/api.py`.

Expected decisive test paths:

- `backend/tests/test_v8_document_semantics_event_adapter.py`;
- `backend/tests/test_v8_acceptance_notice_evidence_adapter.py`;
- `backend/tests/test_v8_oa_notice_evidence_api.py`.

The implementation may align only direct obsolete assertions in these affected inherited
test files when the focused RED proves they encode ordinary document status mutation:

- `backend/tests/test_addgap_document_semantic_state_effect.py`;
- `backend/tests/test_document_impact_preview_api.py`;
- `backend/tests/test_b2_reply_chain.py`;
- `backend/tests/test_spec_alignment_e2e.py`.

Alignment is limited to replacing the obsolete expectation that ordinary document
registration directly changes/restores `Case.status` or previews such a change. Deadline,
reply-task, fee, document, template, HTTP, transaction and all unrelated assertions remain
unchanged. Any additional failing test requires explicit current-tree impact proof before
it enters this closure.

The minimum implementation removes the status-write branches from the shared template-
defaults helper, not by bypassing transition validation or writing the same value through
another path. It does not call `apply_lifecycle_event()` and does not add actor, evidence,
confirmation or idempotency fields to ordinary document input.

## Dedicated adapter contract

The two adapter request models reuse the exact strict field/validation contract of
`RectificationNoticeIn`. Their frozen/slots/keyword-only commands have exact fields
`document_id`, `evidence_version_id`, `actor_id`, `effective_at`, `occurred_at`, and
`idempotency_key`. Results return case/document/evidence/activity identity, activity
sequence, lifecycle revision, effective/occurred time, idempotency key and replay flag;
the OA result additionally returns exact official due date/source/status and OA sequence.

Both services validate before calling `apply_lifecycle_event()` and remain caller-owned
transaction functions. Missing document/case/evidence preserves 404. Wrong relationship
preserves 400. Invalid template semantics, stored evidence state/hash/current identity,
deadline or OA mapping preserves 409 and writes nothing. Exact replay returns the same
activity with `reused=True`; same-key drift propagates the lifecycle conflict.

The OA sequence mapping is exact and case-sensitive:

| template code | sequence |
| --- | --- |
| `OA_IN` | 1 |
| `OFFICIAL_NOTICE_003` | 1 |
| `OFFICIAL_NOTICE_005` | 2 |
| `OFFICIAL_NOTICE_021` | 3 |
| `OFFICIAL_NOTICE_024` | 4 |
| `OFFICIAL_NOTICE_029` | 5 |

Every other value returns no mapping and fails 409 at the OA adapter. The acceptance event
payload is empty. The OA payload contains exactly `official_due_date`,
`official_due_date_source`, `official_due_date_status="CONFIRMED"`, `oa_sequence`, and the
exact stored template code. Evidence kinds are exactly `ACCEPTANCE_NOTICE` and
`OA_NOTICE`. No adapter mutates the document, evidence version, template, deadline or fee.

## RED, GREEN and affected verification

The decisive RED proves on the current tree:

- `lifecycle_event_type` routing metadata is absent;
- ordinary OA create changes legacy case status;
- ordinary grant create changes lifecycle-related case state or appends activity;
- ordinary reply create applies template status restoration; and
- the impact preview advertises a direct status mutation;
- both dedicated routes and public adapter DTOs/functions are absent.

GREEN proves all three ordinary operation families preserve the exact six-value lifecycle
snapshot: legacy `Case.status`, business stage, official-procedure stage, legal status,
lifecycle revision and lifecycle activity count. It separately proves the document,
confirmed due date, reply marker, task/grant-task routing and preview risk-tip outcomes.

After focused GREEN, run only the four named affected inherited files plus the currently
accepted exact shared-seam tranches below. SQLite-writing verification is serialized:

```text
backend/tests/test_document_wizard_batch_create.py
backend/tests/test_v8_attachment_evidence_atomic_adapter.py
backend/tests/test_v8_generated_attachment_evidence_adapter.py
backend/tests/test_v8_oa_out_package_atomic_link.py
backend/tests/test_v8_oa_prepared_activity.py
backend/tests/test_v8_oa_external_submission_evidence.py
backend/tests/test_v8_preliminary_started_evidence_api.py
backend/tests/test_v8_preliminary_passed_evidence_api.py
backend/tests/test_v8_rectification_notice_evidence_api.py
backend/tests/test_v8_publication_notice_evidence_api.py
backend/tests/test_v8_substantive_started_evidence_api.py
backend/tests/test_v8_reexamination_started_evidence_api.py
backend/tests/test_v8_application_rejection_evidence_api.py
backend/tests/test_v8_application_withdrawal_evidence_api.py
backend/tests/test_v8_application_abandonment_evidence_api.py
backend/tests/test_v8_application_restoration_evidence_api.py
```

Run them together with the three decisive successor tests and four named obsolete-
assertion alignment files. Then run scoped Ruff and exact-path diff checks. No other
test-file assertion may be changed to make this tranche green.

## Downstream dependency effect

After independent implementation approval and ledger integration:

- ordinal 61 becomes `SUPERSEDED_BY_STORY`, resolving the old dispatch conflict;
- acceptance and OA transitions become available only through the two exact new evidence
  routes; ordinary creation remains insufficient evidence;
- `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01` may proceed as the sole dedicated
  grant-notice lifecycle transition adapter;
- grant-year annuity, format-letter context, legacy reconciliation and overlay chains may
  use that independently accepted successor dependency;
- no downstream task may treat document presence alone as confirmed lifecycle evidence.

## Non-goals and rollback

No new lifecycle event or generic lifecycle endpoint; no change to accepted lifecycle
rules, evidence adapters, deadline rules, fee amounts, grant evidence decisions,
attachment promotion, schema/migration, permission, public document request/response
shape, template catalog, source bytes or historical evidence. The grant attachment path
and its transition remain owned by the dedicated grant adapter task.

Rollback reverts only the successor implementation, its direct test alignments, decision
record, story/review and ledger mapping. It must not create, delete or rewrite lifecycle
events or case history.
