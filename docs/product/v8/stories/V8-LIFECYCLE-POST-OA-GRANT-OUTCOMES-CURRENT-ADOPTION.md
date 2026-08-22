# Story V8-LIFECYCLE-POST-OA-GRANT-OUTCOMES-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: adopt and prove the exact post-OA receipt, reexamination, grant-registration,
  grant-announcement, patent-register confirmation and application-rejection lifecycle
  outcomes, including immutable fee/source snapshots and typed register-status conflicts.
- Change mode: exact current adoption of independently accepted archived rule, service
  context and test slices. Historical RED is preserved and not rerun.
- Authority: lifecycle, legal-status, official-fee snapshot and evidence-lineage
  invariants in `docs/product/v8/domain-contract.md`, frozen catalog rows 29–34 and their
  exact accepted successor contracts.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Catalog IDs and ownership order

1. `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01` (ordinal 29)
2. `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01` (ordinal 30)
3. `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01` (ordinal 31)
4. `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01` (ordinal 32)
5. `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01` (ordinal 33)
6. `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01` (ordinal 34)

The current-reviewed prosecution-notice story is the exact predecessor. Catalog order
serializes the shared rule file; it does not invent one mandatory runtime path through
grant and rejection outcomes.

## Observable status outcomes

| Event | Exact accepted predecessor | Result |
| --- | --- | --- |
| `OA_RECEIPT_ARCHIVED` | OA reply / office-action response / application pending | prosecution management / substantive examination / application pending |
| `REEXAMINATION_STARTED` | substantive examination / application pending, or closed rejected application | prosecution management / reexamination / application pending |
| `GRANT_REGISTRATION_NOTICE_RECORDED` | confirmed pending application at preliminary, substantive or reexamination, or exact replacement of grant-registration state | grant registration in progress / grant registration / application pending |
| `GRANT_ANNOUNCEMENT_CONFIRMED` | grant registration / application pending, or exact replacement of announced in-force patent | post-grant maintenance / grant announced / patent in force |
| `PATENT_REGISTER_STATUS_CONFIRMED` | announced in-force patent or specifically terminated patent | projection remains unchanged; exact conflict codes direct differing legal status to a specific lifecycle event |
| `APPLICATION_REJECTION_CONFIRMED` | one of the exact coherent pending-application prosecution states | closed / procedure closed / application rejected |

All successful results remain `CONFIRMED` and return `oa_sequence=None`.

## Evidence, snapshot and replacement boundaries

- OA receipt requires one exact `OA_RECEIPT` /
  `OfficialWorkPackageReceipt`; reexamination requires one exact
  `REEXAMINATION_SOURCE` / `DocumentEvidenceVersion`. Both use exact empty payloads and
  pure transaction-independent rules.
- Grant registration requires the exact source document and reviewed evidence-version
  pair, identical reviewed hash/time facts, canonical notice payload, due date and
  deadline confirmation, and a canonical nonempty grant-fee-lines snapshot.
- Every grant fee line has one unique positive year, a canonical positive two-decimal
  amount and only reduction ratio `0`, `0.7` or `0.85`. The rule validates frozen facts;
  it does not calculate, infer, persist or collect an official fee.
- Initial and replacement grant notices are distinct. Replacement requires exact,
  non-self predecessor task/activity identities and the command
  `supersedes_event_id`; no fallback predecessor is selected.
- Grant announcement requires an independent reviewer, exact grant-announcement evidence,
  canonical source snapshot/hash and announcement date equal to the effective date.
  Replacement preserves the exact superseded announcement boundary.
- Patent-register confirmation requires an independent reviewer, exact evidence and
  canonical status snapshot/hash. An initial confirmation has no predecessor. A
  replacement requires the exact superseded register event plus the verified stored
  predecessor snapshot hash, and the new snapshot hash must differ.
- The service obtains only the exact predecessor event type and verified stored snapshot
  hash. Missing/cross-case predecessor, noncanonical stored JSON, wrong schema/hash or
  mismatched replacement fails closed with the frozen typed conflict.
- A same-status register confirmation preserves the projection with no conflict.
  Terminated/expired/invalidated status reported against an in-force patent, or in-force
  status reported against a terminated patent, preserves the projection and records only
  `PATENT_REGISTER_STATUS_REQUIRES_SPECIFIC_EVENT`. It never mutates legal status directly.
- Application rejection accepts exactly one rejection evidence version. A reexamination
  final rejection is valid only from the reexamination projection.

## Service integration and replay

`LifecycleRuleDecision` gains a default empty, sorted, unique `conflict_codes` tuple.
Existing rules therefore retain their prior behavior. Only patent-register confirmation
receives `PatentRegisterStatusRuleContext`; all other rules continue to receive the caller
transaction. The service validates the typed decision, passes conflict codes to the
existing atomic activity append, and preserves caller-owned commit/rollback behavior.

Register-status replay reconstructs and validates the stored predecessor context before
returning the existing activity result. The first valid differing-status confirmation
appends exactly one conflict activity and increments lifecycle revision once; exact replay
returns that same activity, conflict code, sequence and revision without another write.
The same idempotency key with a different immutable payload fails before rule dispatch and
does not add an activity or revision. An exact replacement with a new key and verified
predecessor appends exactly one successor activity/revision. Existing
idempotency/conflict behavior remains fail closed.

## Exact paths

- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/app/modules/cases/lifecycle_service.py`
- `backend/tests/test_v8_lifecycle_oa_receipt.py`
- `backend/tests/test_v8_lifecycle_reexamination_started.py`
- `backend/tests/test_v8_lifecycle_grant_registration_notice.py`
- `backend/tests/test_v8_lifecycle_grant_announcement.py`
- `backend/tests/test_v8_lifecycle_register_status.py`
- `backend/tests/test_v8_lifecycle_application_rejection.py`
- `backend/tests/test_v8_lifecycle_register_status_conflict_service.py`

The six rule tests and register-status service test are archive-identical. The shared rule
and service files adopt only the archive hunks needed by rows29–34 and the accepted
register-status successor context.

## Current verification

The controller ran one serialized tranche containing the exact six rules,
register-status conflict service, OA-notice predecessor and apply-event regression:
`461 passed`, with only the inherited third-party `passlib` deprecation warning.

Scoped Ruff check and exact diff-check pass. Current Ruff format-check would reformat the
shared rule file and three exact archive-identical tests; the archive bytes produce those
same diagnostics. No broad formatter-version migration is absorbed.

An independent High reviewer must review the exact commit/range, rerun the decisive tranche
once, verify the product/test Git fingerprint and confirm that no rows35+ terminal or
restoration rule entered the candidate.

## Non-goals and rollback

No withdrawal, abandonment, patent termination/expiry/invalidation/restoration or
application restoration; no adapter/API/UI, document creation, fee calculation,
obligation/payment, schema/migration, customer/source decision, ledger edit or milestone
claim. Rollback reverts the six rule slices, register-status service context, seven tests
and this story card as one exact candidate while retaining rows1–28.
