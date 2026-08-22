# Story V8-OA-PREPARED-DOCUMENT-ACTIVITY-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `bbd7bae82e5c`
- Outcome: OA_OUT/package preparation appends one confirmed `OA_REPLY_PREPARED`
  `DOCUMENT` activity in the caller-owned transaction, with the exact OA reply package
  and prepared reply evidence linked and no central lifecycle change.
- Catalog ID: `FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01` (ordinal `68`,
  profile `TC-ADAPTER`).
- Authority: frozen catalog row `68`, `docs/product/v8/domain-contract.md`, the current
  lifecycle append adoption at `7bb54cef0d4f`, and the independently accepted Row 67
  product/review commits `24aadc66215e` / `ae42096d7a82`.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Dependency and exact paths

The current Row 67 `prepare_oa_out_package_link()` adapter is the only changed entrypoint.
Its accepted `prepare_oa_reply()` command, unique package/reply link, generated DRAFT reply
evidence and caller-owned transaction remain unchanged. The shared lifecycle
`append_case_activity()` seam remains unchanged.

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_oa_prepared_activity.py`
- `docs/product/v8/stories/V8-OA-PREPARED-DOCUMENT-ACTIVITY-CURRENT-ADOPTION.md`

## Observable contract

After the Row 67 preparation seam succeeds, the adapter resolves exactly one
`OA_REPLY_PREPARATION` derivation for the returned source and reply evidence identities.
An ambiguous derivation fails closed with `OA_REPLY_IDENTITY_CONFLICT`, allowing the
existing outer transaction to roll back the preparation and activity together.

The adapter appends `OA_REPLY_PREPARED` in the `DOCUMENT` lane at the derivation timestamp.
Its idempotency key is `oa-reply-prepared:{package_id}`. It links the exact
`OfficialWorkPackage` snapshot and exact prepared `DocumentEvidenceVersion`, and records
the package, source document, reply document, reply evidence and actor identities in the
`FPMS_OA_REPLY_PREPARED_ACTIVITY_V1` payload.

Both activity projections are identical and the payload carries `center_changes={}`.
Replay after a later lifecycle projection change reuses the stored prepared activity
without overwriting that later projection or adding duplicate evidence links. The OA task
remains open and the legacy case status is unchanged.

## TDD and verification

The archived focused test was restored byte-for-byte with SHA-256
`c663ceb446887c025337c3a797c652c05138b303bf55bca47a9300524bc8e7a7`.
Under the controller-granted serialized SQLite lane, focused RED produced
`3 failed, 2 warnings`: the prepared activity was absent and ambiguous preparation
derivations did not fail closed. The minimum archived adapter hunk then produced focused
GREEN `3 passed, 2 warnings`. Exact affected Row 67 and lifecycle-append regressions
produced `63 passed, 2 warnings`. The warnings are inherited passlib and Pydantic
deprecations. The serialized lane was released immediately after the final test command.

Scoped Ruff and exact diff checks run on the three owned paths. Independent High review
of the eventual exact commit/range remains required; this implementer does not approve the
`PROTECTED` story.

## Non-goals and rollback

No change to `prepare_oa_reply()`, the central lifecycle append/rule services, task close,
external submission, receipt projection, case lifecycle, API/UI, schema/migration/seed,
source or customer decision, ledger, review receipt, old task/evidence or broad tests. In
particular, catalog Row 69 external-submission behavior is not implemented here.

Rollback reverts only the focused test, this story card and the prepared-activity adapter
hunk in `backend/app/modules/official_workflows/service.py`.
