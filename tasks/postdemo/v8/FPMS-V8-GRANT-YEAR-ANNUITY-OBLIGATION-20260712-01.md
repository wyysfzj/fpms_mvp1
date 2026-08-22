# FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-13 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `130`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `572`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Recognize/reuse only the explicitly reviewed grant-year annuity lines frozen on one
confirmed grant-registration-notice lifecycle activity, or wholly supersede the unique
direct-predecessor obligation for a correction; never infer or add another fee line.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract for this one adapter closure.
It consumes the immutable output of the fee-line-snapshot and grant-notice lifecycle
prerequisites and delegates the sole fee write to the already frozen FO recognition seam.
It does not parse a notice, calculate a rate, decide fee-reduction eligibility or create a
draft.

### Exact public adapter interface

`backend/app/modules/grant_fees/service.py` defines exactly one new task-owned command and
one synchronous public callable. The command uses
`@dataclass(frozen=True, slots=True, kw_only=True)` with the exact field order below. The
adapter returns the existing frozen `RecognizeFeeObligationResult`; it does not introduce
a second result projection.

```python
class RecognizeGrantYearAnnuityObligationCommand:
    grant_fee_task_id: str
    source_activity_id: str
    actor_id: str
    idempotency_key: str


def recognize_grant_year_annuity_obligation(
    command: RecognizeGrantYearAnnuityObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    ...
```

- Parameter order, names and annotations are exact. Raw mappings, a `Document`, caller-
  supplied fee lines, amount, ratio, due date, case ID, source-document ID, patent category,
  supersede target or rate provider are not accepted.
- All four strings must be non-blank, equal to their own `strip()` value and within the
  existing carrier limits. Invalid command type or field shape is HTTP 400
  `GRANT_YEAR_ANNUITY_COMMAND_INVALID` with `details.field`, before any query or write.
- The caller owns `transaction`. The adapter may read and call `recognize_obligation()` but
  must not commit, roll back, close, add a retry loop or append an activity itself.

### Sole immutable source and exact lineage gate

Resolve the named `T_GrantFeeTask` and named lifecycle activity. Before calling the deep
module, all of the following must hold exactly:

1. The task exists, has exact `type="GRANT"`, has a non-null `source_document_id`, a
   non-null `due_date`, a non-blank `deadline_source` and a non-null
   `deadline_confirmed_at`. Its case, source document and due date are facts; no caller or
   fallback may replace them.
2. The activity exists, belongs to the task's exact case, has exact event type
   `GRANT_REGISTRATION_NOTICE_RECORDED`, exact `lane=LIFECYCLE` and exact
   `confirmation_status=CONFIRMED`.
3. Its frozen lifecycle payload uses the schema and field names produced by
   `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01` and
   `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`. The payload's exact `case_id`
   must equal both `activity.case_id` and `task.case_id`; its `grant_fee_task_id`,
   `source_document_id`, ISO due date, deadline source and deadline-confirmed timestamp
   must byte-for-byte or value-for-value match the resolved activity and task.
4. The activity-bound fee-line snapshot is a canonical JSON string with schema
   `FPMS_GRANT_NOTICE_FEE_LINES_V1`; its persisted lowercase SHA-256 must equal the SHA-256
   of the exact UTF-8 snapshot bytes. The snapshot binds exactly its
   `source_document_id`, `reviewed_evidence_version_id` and
   `reviewed_evidence_content_hash` to the corresponding immutable lifecycle payload
   facts; the canonical snapshot has no `case_id` field.
5. Among the activity's immutable evidence links there is exactly one reviewed-evidence
   link identified by that evidence-version ID. Its case, object ID and content hash must
   exactly match the activity payload and snapshot. The persisted evidence version must
   resolve to the same case and source document and have the same content hash. No current-
   version inference or replacement evidence is allowed at recognition time.
6. The source document belongs to the same case. This lookup verifies identity only: the
   adapter must not read or parse `Document.extra_data`, attachment/PDF bytes or OCR output.

Missing task is HTTP 404 `GRANT_FEE_TASK_NOT_FOUND`. Missing activity, source document or
evidence version, a malformed/non-canonical snapshot, hash mismatch, multiplicity, wrong
case/type/lane/status, or any task/activity/document/evidence/snapshot/due-lineage mismatch
is HTTP 409 `GRANT_YEAR_ANNUITY_SOURCE_LINEAGE_CONFLICT`; `details.reason` identifies the
failed gate. Every such failure is write-free.

The immutable activity payload is the sole authority for fee lines. The adapter must never
re-read `Document.extra_data`, OCR or parse a PDF, use `task.gov_fee_amt`, query a rate book,
guess from a fee name, infer a fee-reduction ratio or eligibility, or accept a draft or
estimate as source truth. Later mutation of any such prohibited source cannot change an
exact replay.

### Exact fee-line validation and category mapping

The canonical snapshot contains a non-empty `lines` JSON array whose line-object field
names are exactly `fee_name`, `year`, `amount` and `reduction_ratio`. The adapter validates
the persisted facts again, without coercion or silent cleanup:

- `fee_name` is a non-blank string, equals its own `strip()` value and fits the existing
  fee-obligation line carrier.
- `year` is an exact positive `int`, not `bool`, and is unique across the complete
  snapshot. Duplicate years are invalid even when the duplicate line is otherwise equal.
- `amount` is an exact finite `Decimal`, strictly positive, has at most two
  fractional digits and fits `Numeric(18, 2)`. Floats, booleans, NaN/infinity, zero,
  negatives and over-precision are invalid.
- `reduction_ratio` is an exact finite `Decimal` equal to exactly `Decimal("0")`,
  `Decimal("0.7")` or `Decimal("0.85")`; no other ratio, float conversion, eligibility
  lookup or best-benefit calculation is allowed.

Any invalid, empty or duplicate persisted line fact is HTTP 409
`GRANT_YEAR_ANNUITY_FEE_LINE_CONFLICT` and writes nothing. Preserve the canonical snapshot
array order exactly when projecting lines to the deep module; do not sort, deduplicate or
otherwise reorder by `year`, amount, name or fee code.

Read `Case.patent_category` exactly, with no trimming, case-folding, aliasing or fallback,
and map every listed line to one category-specific annual fee code:

| Exact patent category | Exact fee code |
| --- | --- |
| `INV` | `CN_ANNUITY_FEE_INV` |
| `UM` | `CN_ANNUITY_FEE_UM` |
| `DES` | `CN_ANNUITY_FEE_DES` |

Every other value, including null, blank or differently cased text, is HTTP 409
`GRANT_YEAR_ANNUITY_PATENT_CATEGORY_UNSUPPORTED` and writes nothing.

### Exact FO command projection and prohibited additions

After all gates pass, call `recognize_obligation()` exactly once with a
`RecognizeFeeObligationCommand` projected as follows:

- `case_id`, `source_document_id` and `due_date` are copied exactly from the confirmed
  `T_GrantFeeTask`; `source_activity_id` is the confirmed lifecycle activity ID.
- `fee_domain=FeeDomain.GOV`, `currency="CNY"`,
  `obligation_type="GRANT_YEAR_ANNUITY"` and `source_status=FeeSourceStatus.VERIFIED`.
- Each and only each reviewed snapshot line becomes one `FeeObligationLineInput` with the
  mapped category fee code, exact source `fee_name`, `fee_year_key=year`,
  `payable_amount=amount`, `source_amount=amount`,
  `official_full_amount=None`, the exact source reduction ratio, `source_date=None` and
  `difference_review_state=FeeDifferenceReviewState.REVIEW_REQUIRED`.
- `actor_id` and `idempotency_key` are passed unchanged from the adapter command.
- The supersede pair is both null for an original notice and is the exact frozen correction
  pair below for a correction.

No registration fee, publication/printing fee, combined fee, fixed line, missing year,
zero line or rate-derived difference may be added. `official_full_amount` remains null
because this adapter performs no rate-book comparison. `REVIEW_REQUIRED` records that
unperformed difference review; it does not authorize amount replacement. The adapter must
not create or modify `FeeDraft`, `FeeItem`, PayList, payment, client instruction or
`T_GrantFeeTask`, and it must not append a second `FEE_OBLIGATION_RECOGNIZED` activity.
`recognize_obligation()` owns the only FEE activity and all obligation writes.

### Correction, supersession and replay

- An original notice requires both `activity.supersedes_event_id is None` and no
  `T_GrantFeeTask` whose `superseded_by_task_id` names the current task. It passes
  `supersedes_obligation_id=None` and `supersede_reason=None`.
- A correction requires exactly one direct predecessor activity named by
  `activity.supersedes_event_id` and exactly one direct predecessor task whose
  `superseded_by_task_id` equals the current task ID. The predecessor activity must be the
  same-case confirmed `GRANT_REGISTRATION_NOTICE_RECORDED` activity bound to that
  predecessor task and its exact source document/due/evidence/snapshot lineage.
- The predecessor must source exactly one existing `GRANT_YEAR_ANNUITY` obligation that is
  the direct current predecessor of this correction. Pass its ID as
  `supersedes_obligation_id` and exact reason
  `GRANT_REGISTRATION_NOTICE_CORRECTION`. Never choose the newest, oldest or first row.
- A correction marker on only one lineage, no predecessor obligation, multiple candidate
  tasks/activities/obligations, an indirect ancestor, cross-case source, or a predecessor
  already replaced by another correction is HTTP 409
  `GRANT_YEAR_ANNUITY_PREDECESSOR_CONFLICT`, with no write.
- An exact same-command replay revalidates the immutable source facts and delegates the
  same command to `recognize_obligation()`. It returns the same obligation/activity IDs
  with `reused=True`, including a correction whose predecessor is now historical. Replay
  creates no new header, line or activity and does not reread a prohibited mutable source.
- Same idempotency key with any changed task, activity, actor, snapshot, line, category,
  due/source lineage or predecessor fact is a 409 conflict. A new key does not make an
  already-current source/fee-year identity reusable; the deep-module conflict propagates.

Except for the adapter-specific 400/404/409 errors frozen above, propagate the existing
`recognize_obligation()` `BusinessError` code/status unchanged. The adapter adds no catch-
all translation and every failed call leaves the caller-owned transaction usable.

### Frozen RED / GREEN matrix

The exact RED is the missing DTO, signature and adapter behavior through this public seam;
it is not a deliberately invalid fixture. GREEN must prove:

1. exact frozen/slots/keyword-only command fields, signature and existing result type;
2. INV, UM and DES success with multiple reviewed lines whose canonical source order is
   preserved exactly, unique positive `year` values, exact `amount`/ratio/name mapping,
   correct category code, GOV/CNY/type/due/source projection, null full amount and
   `REVIEW_REQUIRED` difference state;
3. only listed annual-fee lines exist—no registration, combined, printing/publication,
   zero, inferred or rate-derived line—and no draft, PayList, payment or instruction exists;
4. blank name, empty lines, duplicate/boolean/non-positive year, non-Decimal/non-finite/non-
   positive/over-precision amount and every ratio outside exact `0/0.7/0.85` each fail 409
   with unchanged obligation/activity/draft counts;
5. unsupported/null/mis-cased patent category fails 409 with no write;
6. missing/wrong-case/wrong-type/unconfirmed source activity and every payload, canonical-
   snapshot, snapshot-hash, evidence-ID/hash, document, task, deadline-source, deadline-
   confirmation or due-date mismatch fail 409 with no write;
7. a success test makes `Document.extra_data`, OCR/PDF parsing, `task.gov_fee_amt`, rate-book
   selection, eligibility inference and draft creation fail if touched, proving the
   immutable activity snapshot is the sole consumed fee-line fact;
8. exact replay returns the same recognition result with `reused=True` and exactly one FEE
   activity; same-key drift and new-key current-identity collision are 409/no write;
9. one unique direct correction supersedes exactly its direct predecessor obligation;
   missing, ambiguous, indirect, cross-case, already-diverged and activity/task-lineage
   disagreement cases are 409/no write, while exact correction replay remains reusable;
10. caller-owned transaction behavior and the fee-line-snapshot, grant-notice lifecycle
    adapter, FO recognition and inherited grant-lineage regressions remain green.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task35:FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_lineage_schema.py.
- `inherited` — `Task36:FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_source_deadline.py.
- `inherited` — `Task37:FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_auto_draft_gate.py.
- `inherited` — `Task38:FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_grant_activation.py.
- `inherited` — `Task39:FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_replacement_service.py.
- `inherited` — `Task40:FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_replacement_api.py.
- `inherited` — `Task41:FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_list_lineage_projection.py.
- `inherited` — `Task42:FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_state_lineage_gate.py.
- `inherited` — `Task43:FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts.
- `inherited` — `Task44:FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts.
- `inherited` — `Task49:FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_b3_fee_linking.py.
- `inherited` — `Task50:FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_notice_task_creation.py.
- `inherited` — `Task52:FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_preview_no_auto_draft.py.
- `inherited` — `Task53:FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_spec_alignment_e2e.py.
- `inherited` — `Task55:FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_oa_acceptance_activation.py.
- `inherited` — `Task57:FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_worklist_api.py.
- `inherited` — `Task58:FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_state_machine_api.py.
- `inherited` — `Task59:FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_mutation_lineage_gate.py.
- `inherited` — `Task60:FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts.
- `inherited` — `Task61:FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_draft_linkage_api.py.
- `inherited` — `Task62:FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_notice_document_api.py.
- `inherited` — `Task64:FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/git/diff.patch; targeted tests backend/tests/test_addgap_document_create_atomicity.py.
- `inherited` — `Task69:FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/summary.md, artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/git/diff.patch; targeted tests backend/tests/test_grant_fee_prereq_schema.py.

- Approved source dependency cell (superseded by the Ultra delta): recognize; grant lineage regressions
- Approved Ultra delta dependency correction: fee-line snapshot, grant-notice lifecycle adapter and FO recognize

### Shared ownership serialization

- `backend/app/modules/grant_fees/service.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_v8_grant_year_annuity_obligation.py`
- `artifacts/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_year_annuity_obligation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_year_annuity_obligation.py tests/test_v8_grant_notice_fee_line_snapshot.py tests/test_v8_grant_notice_lifecycle_adapter.py tests/test_v8_fee_obligation_recognize.py tests/test_addgap_grant_lineage_schema.py tests/test_addgap_grant_source_deadline.py tests/test_addgap_grant_auto_draft_gate.py tests/test_addgap_notice_grant_activation.py tests/test_addgap_grant_replacement_service.py tests/test_addgap_grant_replacement_api.py tests/test_addgap_grant_list_lineage_projection.py tests/test_addgap_grant_state_lineage_gate.py tests/test_b3_fee_linking.py tests/test_grant_fee_notice_task_creation.py tests/test_addgap_grant_preview_no_auto_draft.py tests/test_spec_alignment_e2e.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_grant_fee_worklist_api.py tests/test_grant_fee_state_machine_api.py tests/test_addgap_grant_mutation_lineage_gate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_document_api.py tests/test_addgap_document_create_atomicity.py tests/test_grant_fee_prereq_schema.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py`
- `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_year_annuity_obligation.py tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01` pass. Only then may this task be reported PASS.
