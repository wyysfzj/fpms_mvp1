# Story V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-CURRENT-ADOPTION

- Status: `READY_FOR_REVIEW`.
- Risk: `PROTECTED`.
- Catalog ID: `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
  (ordinal `74`).
- Product/test commit: `997a6896b90deae18ecda7bde9db35e48513b242`.
- Integration parent: `37beb56c66a2dc450a7cb9e0ba6acffee4b0ef51`.
- Authority: the exact frozen Row74 task contract, current-verified grant-registration
  lifecycle rule, Row61 lifecycle-neutral successor, and current-verified grant-notice
  fee-line snapshot prerequisite.

## Observable outcome

`dispatch_grant_registration_notice()` now validates one exact live grant task, source
document, current final independently approved evidence version, immutable content hash,
confirmed deadline lineage and canonical fee-line snapshot before dispatching exactly one
`GRANT_REGISTRATION_NOTICE_RECORDED` lifecycle fact. Its exact V1 payload and two evidence
references are immutable. Exact replay is write-free; drift, invalid evidence/snapshot or
ambiguous/reversed replacement lineage fails closed. Caller transaction ownership is
preserved.

The accepted document service already owned the sole call site after attachment/evidence
promotion; therefore this story did not change `documents/service.py`. Ordinary document
creation remains lifecycle-neutral, and the generic path cannot append a second activity.

## Exact current-tree scope

- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_v8_grant_notice_lifecycle_adapter.py`

The test was recovered from archive input `6b2ef89` and adapted only to remove the old
case-status-unchanged assertion owned by the separate pending Row75 contract. It retains
the exact one-activity, one-revision, immutable payload/evidence, replay, correction,
lineage-conflict, rollback and no-second-append assertions. No Row75/76/130 behavior is
absorbed.

## TDD and verification

- real current-tree RED before product change: `45 failed`; every node stopped at the
  absent public dispatch seam;
- focused GREEN after minimum implementation: `45 passed`;
- current snapshot plus lifecycle-rule dependency tranche: `114 passed`;
- Row61 semantics/acceptance/OA affected regression tranche: `159 passed`;
- exact inherited 26-file backend tranche: `162 passed, 55 failed`;
- scoped Ruff check and format check on the two changed paths: PASS;
- exact diff check: PASS.

The 55 inherited failures are current-tree baselines outside the two-path closure:
47 legacy CaseCreate fixtures stop at HTTP 422 because they omit the now-required explicit
`fee_reduction`; two older catalog-overlay expectations freeze the executable set before
later accepted rows 031/034; six are the already known OA_OUT reply-date/filter baseline.
No Row74 focused, dependency or Row61 regression failed. Independent High review must
verify that classification on the exact candidate and rerun the decisive checks before
adoption.

## Non-goals and rollback

No generic dispatcher, ordinary-document lifecycle write, grant attachment-status rule,
grant-fee-done status rule, annuity obligation, fee/draft creation, schema/migration,
second entrypoint, parser change, mutable source reread or adjacent cleanup. Rollback
reverts exactly `997a6896b90deae18ecda7bde9db35e48513b242`; it must not rewrite existing
lifecycle history or current-verified dependency stories.
