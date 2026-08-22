# FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-13 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `74`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `460`
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

Consume the resolver's frozen grant semantics and act as the sole dispatcher of the grant-registration event while retaining confirmed due/source lineage; prove exactly one activity/revision and no second append by the generic document adapter.

## Ultra Contract Freeze — 2026-07-13

This section freezes the complete High implementation contract for the existing grant
adapter. It preserves the exact closure above: this task validates and dispatches one
reviewed grant-registration fact; the separate snapshot task owns fee-line parsing and the
separate lifecycle-rule task owns the projection decision.

### Exact public seam and sole-dispatch boundary

`backend/app/modules/grant_fees/service.py` exposes exactly this task-owned callable:

```python
def dispatch_grant_registration_notice(
    *,
    grant_fee_task_id: str,
    source_document_id: str,
    reviewed_evidence_version_id: str,
    expected_content_hash: str,
    actor_id: str,
    recorded_at: datetime,
    idempotency_key: str,
    transaction: Session,
) -> LifecycleTransitionResult:
    ...
```

- All identifiers and the idempotency key are non-blank within their existing carrier
  lengths; `recorded_at` is timezone-naive; `expected_content_hash` is exactly
  `sha256:<64 lowercase hexadecimal characters>`. Malformed input is HTTP 400
  `GRANT_NOTICE_LIFECYCLE_INVALID` and writes nothing.
- For `GRANT_NOTICE`, `backend/app/modules/documents/service.py` calls only this seam after
  the Document and its GrantFeeTask are available in the same caller-owned transaction. It
  must not call `apply_lifecycle_event()` or `append_case_activity()` itself. Therefore the
  generic document adapter cannot append a second activity or increment the lifecycle
  revision a second time.
- The seam calls `apply_lifecycle_event()` exactly once for a new fact with
  `event_type="GRANT_REGISTRATION_NOTICE_RECORDED"`, `lane=LIFECYCLE`,
  `confirmation_status=CONFIRMED`, `effective_at=occurred_at=recorded_at`,
  `reviewer_id` from the approved evidence version, and
  `idempotency_key=f"grant-registration-notice:{idempotency_key}"`. The frozen grant rule,
  not this adapter, decides the central projection.

### Live source, reviewed evidence and snapshot validation

For a new append, resolve the named GrantFeeTask, source Document, DocumentEvidenceVersion
and Case before constructing the lifecycle command. Missing rows are HTTP 404 using the
existing resource-specific not-found code. All other source inconsistencies below are HTTP
409 `GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT`, with no activity, evidence link, revision or
source-row mutation:

- the task is type `GRANT`, belongs to the same case as the Document, has
  `source_document_id == document.id`, has no `superseded_by_task_id`, and has confirmed
  lineage: non-null `due_date`, `deadline_source` and timezone-naive
  `deadline_confirmed_at`;
- the Document resolves to executable `GRANT_NOTICE` semantics for that same case;
- the named evidence version belongs to that same case and Document, is the unique current
  row for its lineage (`current_identity_key == f"{case_id}|{lineage_key}"`), has
  `state == FINAL`, `review_state == APPROVED`, and has non-null `reviewer_id` and
  timezone-naive `reviewed_at`;
- its immutable stored `content_hash` exactly equals `expected_content_hash`; a different
  hash is HTTP 409 `GRANT_NOTICE_EVIDENCE_HASH_CONFLICT`, never a best-effort match.

After those checks, invoke only the separate frozen callable:

```python
snapshot = extract_grant_notice_fee_line_snapshot(
    document=document,
    reviewed_evidence_version_id=reviewed_evidence_version_id,
    expected_evidence_content_hash=expected_content_hash,
)
```

Require the exact `GrantNoticeFeeLineSnapshot` result with fields `schema`,
`source_document_id`, `reviewed_evidence_version_id`,
`reviewed_evidence_content_hash`, `lines`, `canonical_json` and `snapshot_hash`. Its
`schema` must be `FPMS_GRANT_NOTICE_FEE_LINES_V1`; its three provenance fields must equal
the resolved Document/evidence identities and hash; `canonical_json` is the canonical
snapshot string; and `snapshot_hash` is the bare lowercase 64-character SHA-256. A parser
rejection, wrong result type or field mismatch is HTTP 409
`GRANT_NOTICE_FEE_LINES_CONFLICT`. This adapter copies `canonical_json` and `snapshot_hash`
verbatim; it does not parse JSON, OCR/PDF content, recalculate the hash, look up a rate,
decide fee-reduction eligibility or trust mutable `Document.extra_data` after the activity
is recorded. It creates no fee obligation, grant-year annuity, payment draft or other
draft.

### Exact immutable V1 activity payload and evidence set

The lifecycle command payload is a JSON object with exactly these keys and no others:

```text
schema                              = "FPMS_GRANT_REGISTRATION_NOTICE_RECORDED_V1"
case_id                             = Case.id
grant_fee_task_id                   = GrantFeeTask.id
source_document_id                  = Document.id
reviewed_evidence_version_id        = DocumentEvidenceVersion.id
reviewed_evidence_content_hash      = DocumentEvidenceVersion.content_hash
reviewed_at                         = DocumentEvidenceVersion.reviewed_at.isoformat()
grant_fee_lines_schema              = "FPMS_GRANT_NOTICE_FEE_LINES_V1"
grant_fee_lines_snapshot            = parser canonical JSON string
grant_fee_lines_snapshot_hash       = parser bare lowercase SHA-256
due_date                            = GrantFeeTask.due_date.isoformat()
deadline_source                     = GrantFeeTask.deadline_source
deadline_confirmed_at               = GrantFeeTask.deadline_confirmed_at.isoformat()
predecessor_grant_fee_task_id       = direct predecessor task ID or null
supersedes_activity_id              = predecessor grant activity ID or null
```

The command contains exactly two same-case evidence references, both with
`content_hash=reviewed_evidence_content_hash` and `captured_at=reviewed_at`:

1. `evidence_kind="SOURCE_DOCUMENT"`, `object_type="Document"`,
   `object_id=source_document_id`;
2. `evidence_kind="DOCUMENT_EVIDENCE_VERSION"`,
   `object_type="DocumentEvidenceVersion"`,
   `object_id=reviewed_evidence_version_id`.

The IDs and hashes in both references must equal the payload fields exactly. No mutable
Document field, fee amount or derived rate is stored as an alternative source of truth.

### Replay, correction and replacement lineage

- Check the same-case prefixed idempotency key before the live current/active-lineage guards.
  For an existing activity, reconstruct its stored projections, exact fifteen-key V1
  payload and complete two-reference evidence set, then delegate to the frozen lifecycle
  replay comparison. An exact retry returns that activity with `reused=True`, does no write
  and remains valid after later current-version or replacement advancement. Any payload,
  source ID, hash, timestamp, due-lineage, predecessor or evidence difference is HTTP 409
  `LIFECYCLE_IDEMPOTENCY_CONFLICT`.
- For a new initial notice, no task may point to the current task as its direct predecessor;
  both predecessor payload fields are null and `supersedes_event_id=None`.
- For a new correction/replacement notice, exactly one same-case predecessor task must have
  `superseded_by_task_id == current_task.id`; it must have exactly one prior
  `GRANT_REGISTRATION_NOTICE_RECORDED` activity whose payload identifies that predecessor.
  Copy its task/activity IDs into the two predecessor payload fields and pass that activity
  as `supersedes_event_id`. Missing, multiple, cross-case, reversed or inconsistent lineage
  is HTTP 409 `GRANT_NOTICE_REPLACEMENT_LINEAGE_CONFLICT`.
- Correction is append-only. Never update/delete the predecessor activity, its payload or
  evidence links, never rewrite an old snapshot, and never infer a predecessor from dates
  or document ordering.

### Transaction, RED/GREEN and fail-closed boundary

All reads, parser invocation and the one lifecycle dispatch use `transaction`. The adapter
may flush through the frozen lifecycle seam but must not commit, roll back or close the
Session. Any failure before dispatch writes nothing; caller rollback removes the new
activity/evidence/projection/revision together.

RED must prove the old grant path can omit the reviewed snapshot or append twice. GREEN must
prove: one valid initial notice appends exactly one confirmed lifecycle activity/revision;
the exact fifteen-key V1 payload and two evidence links are immutable and matching; non-current,
non-FINAL, non-APPROVED, wrong-case or hash-mismatched evidence fails closed; malformed fee
lines fail through the separate parser boundary; the generic document adapter performs no
second append; exact replay is write-free; correction appends one linked successor while
leaving the old activity byte-for-byte unchanged; ambiguous/reversed replacement lineage
fails with no mutation; and caller rollback is atomic.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`

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
- `inherited` — `Task51:FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_semantic_state_effect.py, backend/tests/test_document_impact_preview_api.py.
- `inherited` — `Task52:FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_preview_no_auto_draft.py.
- `inherited` — `Task53:FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_spec_alignment_e2e.py.
- `inherited` — `Task54:FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_b_official_due_date_task_generation.py.
- `inherited` — `Task55:FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_oa_acceptance_activation.py.
- `inherited` — `Task56:FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_out_keeps_task_open.py, backend/tests/test_b2_reply_chain.py.
- `inherited` — `Task57:FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_worklist_api.py.
- `inherited` — `Task58:FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_state_machine_api.py.
- `inherited` — `Task59:FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_mutation_lineage_gate.py.
- `inherited` — `Task60:FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts.
- `inherited` — `Task61:FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_draft_linkage_api.py.
- `inherited` — `Task62:FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_notice_document_api.py.
- `inherited` — `Task69:FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/summary.md, artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/git/diff.patch; targeted tests backend/tests/test_grant_fee_prereq_schema.py.

- Approved source dependency cell (verbatim): document semantics event adapter, grant-registration rule; Tasks35–44/49–62/69

### Shared ownership serialization

- `backend/app/modules/documents/service.py` order key `6`; project this order only across owners present in the active manifest.
- `backend/app/modules/grant_fees/service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01` — consume only the immutable reviewed activity snapshot; do not re-read mutable Document fee lines

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_v8_grant_notice_lifecycle_adapter.py`
- `artifacts/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_notice_lifecycle_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_notice_lifecycle_adapter.py tests/test_v8_grant_notice_fee_line_snapshot.py tests/test_addgap_grant_lineage_schema.py tests/test_addgap_grant_source_deadline.py tests/test_addgap_grant_auto_draft_gate.py tests/test_addgap_notice_grant_activation.py tests/test_addgap_grant_replacement_service.py tests/test_addgap_grant_replacement_api.py tests/test_addgap_grant_list_lineage_projection.py tests/test_addgap_grant_state_lineage_gate.py tests/test_b3_fee_linking.py tests/test_grant_fee_notice_task_creation.py tests/test_addgap_document_semantic_state_effect.py tests/test_document_impact_preview_api.py tests/test_addgap_grant_preview_no_auto_draft.py tests/test_spec_alignment_e2e.py tests/test_b_official_due_date_task_generation.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_grant_fee_worklist_api.py tests/test_grant_fee_state_machine_api.py tests/test_addgap_grant_mutation_lineage_gate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_document_api.py tests/test_grant_fee_prereq_schema.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_v8_grant_notice_lifecycle_adapter.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_v8_grant_notice_lifecycle_adapter.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_v8_grant_notice_lifecycle_adapter.py`
- `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_notice_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
