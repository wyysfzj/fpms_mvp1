# Story V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-CURRENT-ADOPTION

- Status: `REVIEW_CORRECTION_CONTRACT_FROZEN / IMPLEMENTATION_PENDING`.
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

Independent review proved the old frozen `documents/service.py` call-site assumption is
not implementable on the current evidence workflow: attachment upload creates only a
`RAW_ATTACHMENT / DRAFT` version and cannot itself confirm legal-state evidence. The
approved lifecycle-neutral source decision forbids turning that ordinary upload into a
transition trigger. The current-tree successor therefore replaces only that obsolete
orchestration detail with the exact dedicated API below. Ordinary document creation,
attachment upload and generic evidence review remain lifecycle-neutral and cannot append
a grant-registration activity.

## Exact production-entry successor

Add exactly one route:

```text
POST /grant-fee-tasks/{grant_fee_task_id}/lifecycle/grant-notice
```

It requires `Doc.Edit`, derives `actor_id` from the authenticated user, owns one
caller-level commit/rollback boundary and returns HTTP 200 with the direct
`LifecycleTransitionResult`. Its strict request model has exactly these required fields
and forbids extras:

```text
reviewed_evidence_version_id: str
expected_content_hash: str
recorded_at: naive datetime
idempotency_key: str
```

The adapter does not resolve, create, promote, mutate or approve evidence. It requires the
named version already to be the exact current `FINAL / APPROVED` version accepted by the
frozen service, resolves `source_document_id` only from the named task, and passes all four
body values plus server actor and the caller-owned Session to
`dispatch_grant_registration_notice()`. Missing task preserves 404; all same-case,
document, evidence, hash, deadline, snapshot, replay and replacement checks remain solely
owned by that service. Exact replay returns the same activity with no new write. Client-
supplied case, source document, reviewer, event type, evidence state or fee-line snapshot
is forbidden.

This route, rather than raw upload or generic review, is the sole production adapter for
this grant event. Existing service-level evidence registration/import/promotion workflows
remain responsible for producing a reviewed final version; creating a new grant-specific
promotion protocol is a separate non-goal and is not required to make this exact adapter
reachable for an existing valid version.

## Exact current-tree scope

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/api.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/tests/test_v8_grant_notice_lifecycle_adapter.py`
- `backend/tests/test_v8_grant_notice_lifecycle_api.py`

The test was recovered from archive input `6b2ef89` and adapted only to remove the old
case-status-unchanged assertion owned by the separate pending Row75 contract. It retains
the exact one-activity, one-revision, immutable payload/evidence, replay, correction,
lineage-conflict, rollback and no-second-append assertions. No Row75/76/130 behavior is
absorbed.

The API correction RED must prove the route is absent. GREEN must prove exact route/method,
strict body, `Doc.Edit`, server actor, direct service arguments/result, one commit on
success, rollback on service or commit failure, and no client control over case/document/
reviewer/event/evidence-state/snapshot fields. It must include one real-SQLite end-to-end
valid call and exact replay through the route, while retaining the existing service test
as the source of detailed failure-matrix coverage.

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

No generic dispatcher, ordinary-document/evidence-review lifecycle write, grant evidence
promotion protocol, grant attachment-status rule,
grant-fee-done status rule, annuity obligation, fee/draft creation, schema/migration,
second entrypoint, parser change, mutable source reread or adjacent cleanup. Rollback
reverts exactly `997a6896b90deae18ecda7bde9db35e48513b242`; it must not rewrite existing
lifecycle history or current-verified dependency stories.
