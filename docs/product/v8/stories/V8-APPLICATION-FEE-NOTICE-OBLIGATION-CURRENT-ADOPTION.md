# Story V8-APPLICATION-FEE-NOTICE-OBLIGATION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `4f550a2`
- Outcome: a reviewed confirmed application-fee notice with exact source, due date and
  item lines creates or reuses the corresponding obligation without activating or drafting
  it.
- Catalog ID: `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
  (ordinal `126`, profile `TC-ADAPTER`).
- Authority: frozen catalog row `126`, its exact task contract, the current-verified fee
  recognition and PCT policy stories, and `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/app/modules/documents/semantics.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/app/modules/documents/application_fee_notice_contracts.py`
- `backend/tests/test_v8_application_fee_notice_obligation.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`

All catalog dependencies are current-verified. This lane shares no product/test path with
the filing-preparation story; SQLite verification is serialized. The contract module is
an archive-owned path already assigned for adoption but absent from the integration tree.
This story transfers that one exact path from the unresolved broad document-evidence
bucket because it is the direct public input/error contract required by the frozen row.

## Observable contract

The resolver freezes semantic `APPLICATION_FEE_NOTICE`. Only a reviewed, confirmed notice
with exact due/source/item-line authority creates or reuses the application-fee
obligation. Preview difference enters review. For PCT cases, exemptions arise only from
confirmed RO/search/report evidence through the pure PCT policy, never from `case_type`
alone. The story neither activates the catalog row nor creates a draft.

The current-verified PCT policy is latest-wins over the archived row-126 fixture: its
command/result intentionally have no `national_stage_entry_date`. The adapter preserves
the notice carrier's entry-date authority by passing that exact date as policy
`effective_on`; the focused fixture must assert the current command/result shape rather
than reintroduce the superseded field into the policy module.

## TDD and verification

The archive RED first failed at the absent transferred contract carrier, then reached all
`15` missing-adapter nodes. Initial GREEN passed `14/14`; current PCT compatibility exposed
one stale archive field and was corrected to the latest-wins `effective_on` interface.
Independent review then found two authority gaps: unrestricted due-source text and an
unbound reviewed-evidence ID. The final candidate restricts both, binds canonical review
activity/evidence lineage and adds negative regressions. Final focused GREEN passed
`26/26`; scoped Ruff/compile/diff checks passed. Independent High re-review approved
P0/P1/P2 all zero.

## Non-goals and rollback

No activation, draft creation, second entrypoint, deep fee-rule change, endpoint, UI,
schema, migration, old task/evidence mutation or adjacent cleanup. Rollback reverts only
product commit `e307d68`, the one-path disposition transfer and this story mapping.
