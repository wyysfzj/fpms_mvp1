# V8 Document Create Lifecycle-Neutral Successor Contract

- Status: `CONTRACT_FROZEN / IMPLEMENTATION_PENDING`.
- Risk: `PROTECTED`.
- Superseded catalog row after implementation acceptance:
  `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01` (ordinal 61).
- Decision authority:
  `DEC-V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-20260809` in
  `docs/product/v8/source-decision-registry.md`.
- Inspection base: `ff4308e26016e714f09f39221d5a7f1ad2be7447`.

## Conflict resolved

The old row-61 closure required ordinary document creation to dispatch a non-grant
lifecycle event. That requirement conflicts with the higher V8 domain contract: central
legal state changes require a confirmed command containing actor identity, reviewed
evidence references, effective time and an idempotency key. `DocumentCreateIn` and the
ordinary create endpoint supply none of those facts.

The approved decision resolves the conflict fail-closed. Ordinary document persistence is
not evidence confirmation and cannot itself change lifecycle truth. Acceptance, OA,
grant and other legal transitions remain available only through their dedicated reviewed-
evidence adapters. Row 61 is therefore not implemented as a generic dispatcher; its
catalog obligation is superseded only after the exact neutral successor below is current-
tree verified.

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
- `backend/app/modules/documents/service.py`.

Expected decisive test path:

- `backend/tests/test_v8_document_semantics_event_adapter.py`.

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

## RED, GREEN and affected verification

The decisive RED proves on the current tree:

- `lifecycle_event_type` routing metadata is absent;
- ordinary OA create changes legacy case status;
- ordinary grant create changes lifecycle-related case state or appends activity;
- ordinary reply create applies template status restoration; and
- the impact preview advertises a direct status mutation.

GREEN proves all three ordinary operation families preserve the exact six-value lifecycle
snapshot: legacy `Case.status`, business stage, official-procedure stage, legal status,
lifecycle revision and lifecycle activity count. It separately proves the document,
confirmed due date, reply marker, task/grant-task routing and preview risk-tip outcomes.

After focused GREEN, run only the four named affected inherited files plus the currently
accepted dedicated lifecycle evidence adapter tranches that touch the same service seam.
Run scoped Ruff and exact-path diff checks. SQLite-writing verification is serialized.

## Downstream dependency effect

After independent implementation approval and ledger integration:

- ordinal 61 becomes `SUPERSEDED_BY_STORY`, resolving the old dispatch conflict;
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
