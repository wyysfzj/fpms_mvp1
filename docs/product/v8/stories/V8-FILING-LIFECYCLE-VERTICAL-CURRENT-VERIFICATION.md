# Story V8-FILING-LIFECYCLE-VERTICAL-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the three filing lifecycle rules form the
  exact fail-closed sequence from filing preparation through externally recorded
  submission to archived filing receipt, including the first establishment of
  `APPLICATION_PENDING`.
- Change mode: current adoption plus one minimum fail-closed correction. Independent
  review found that external-submission evidence accepted a blank object identity; the
  exact current-tree RED and minimum rule/test change close only that defect.
- Authority: the lifecycle and evidence-lineage invariants in
  `docs/product/v8/domain-contract.md`, frozen catalog rows 19–21, and their exact task
  contracts.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Catalog IDs and order

1. `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01` (ordinal 19)
2. `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01` (ordinal 20)
3. `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01` (ordinal 21)

The current tree already contains the accepted predecessors `CASE_OPENED`, the lifecycle
rule registry and the apply-event seam. This story adopts no later lifecycle event.

## Observable lifecycle sequence

Starting from the exact confirmed `CASE_OPENED` projection:

| Event | Business stage | Official procedure stage | Legal status | Verification |
| --- | --- | --- | --- | --- |
| `FILING_PREPARATION_STARTED` | `FILING_PREPARATION` | remains `NOT_SUBMITTED` | remains `NOT_ESTABLISHED` | remains `CONFIRMED` |
| `FILING_EXTERNAL_SUBMISSION_RECORDED` | `WAITING_EXTERNAL_RECEIPT` | `SUBMITTED_WAITING_RECEIPT` | remains `NOT_ESTABLISHED` | remains `CONFIRMED` |
| `FILING_RECEIPT_ARCHIVED` | `PROSECUTION_MANAGEMENT` | `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE` | `APPLICATION_PENDING` | remains `CONFIRMED` |

Every decision returns `oa_sequence=None`. The legal status does not change merely because
preparation starts or an external submission is manually recorded. It changes to
`APPLICATION_PENDING` only after the exact valid filing receipt evidence is archived.

## Exact fail-closed and lineage boundary

- Registry lookup accepts only each exact uppercase event key.
- Each rule accepts only its exact predecessor projection and a confirmed lifecycle-lane
  command with bounded identifiers and naive timestamps.
- Preparation requires exactly one `FILING_WORK_PACKAGE` /
  `OfficialWorkPackage` evidence reference.
- External submission requires exactly one `FINAL_SUBMISSION_VERSION` /
  `DocumentEvidenceVersion` and one `MANUAL_EXTERNAL_SUBMISSION_RECORD` /
  `CaseActivityEvent`.
- Receipt archive requires exactly one `FINAL_SUBMISSION_VERSION` /
  `DocumentEvidenceVersion` and one `VALID_FILING_RECEIPT` /
  `OfficialWorkPackageReceipt`.
- Evidence types, case identity, nonblank distinct object identities, lowercase
  `sha256:[0-9a-f]{64}` content hashes and naive capture times are checked exactly.
  Missing, extra, malformed, cross-case or non-exact evidence returns no decision.
- The three rules are pure and transaction-independent: they do not query, write, flush,
  commit, roll back or reconstruct evidence.

## Exact paths

- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/tests/test_v8_lifecycle_filing_preparation_started.py`
- `backend/tests/test_v8_lifecycle_filing_external_submission.py`
- `backend/tests/test_v8_lifecycle_filing_receipt_archived.py`

The preparation and receipt decisive-test blobs are byte-identical to their archive
counterparts. The external-submission test retains its archive cases and adds only the
blank/whitespace identity regression. Historical task RED and accepted evidence remain
comparison inputs and were not rerun.

## Current-tree verification

The controller granted the serialized SQLite/shared verification lane and ran:

`/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_lifecycle_case_opened.py tests/test_v8_lifecycle_filing_preparation_started.py tests/test_v8_lifecycle_filing_external_submission.py tests/test_v8_lifecycle_filing_receipt_archived.py tests/test_v8_lifecycle_apply_event.py tests/test_v8_lifecycle_activity_append.py tests/test_v8_lifecycle_evidence_kind_capacity.py`

The correction RED ran only
`test_filing_external_submission_rejects_blank_evidence_identity`: all four cases failed
because the invalid command returned a transition. After the minimum nonblank identity
guard, the same four cases passed.

The complete current-tree result is `204 passed`, with only the inherited third-party
`passlib` deprecation warning.

Scoped Ruff check and Ruff format-check pass on the shared lifecycle rule file and the
three decisive tests. An independent High reviewer must review the exact story commit,
independently rerun the decisive current-tree tranche and verify the exact Git
path/mode/blob fingerprint before this `PROTECTED` story is mapped.

## Non-goals and rollback

No second or later lifecycle event, API, UI, adapter/resolver, persistence, activity,
document creation, fee, deadline, permission, schema/migration, registry reorder,
historical evidence mutation, coverage-ledger edit or Foundation claim. Rollback removes
only this story-card commit; the current product and test bytes remain unchanged.
