# FPMS-V8-OVERLAY-CONTRACTS-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `259`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- Delta-3 supplemental materialization row: `14`
- Source catalog line: `790`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-INTERFACE`

- RED expectation: Exact contract test fails because the named type/enum/interface is absent.
- GREEN expectation: Exact contract test and task-scoped Ruff pass.

## Exact Closure Slice

Freeze center snapshot, milestone, document, task, fee, warnings, gates, conflicts and cursor schemas.

## Explicit Non-Closure

No persistence, business adapter, endpoint or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section freezes only the public value/schema interface in
`backend/app/modules/cases/lifecycle_overlay_schemas.py`. It does not implement a
resolver loop, database read, applicability rule, join, HTTP adapter or UI behavior.

### Shared representation rules and exact enums

- Every DTO below uses `@dataclass(frozen=True, slots=True, kw_only=True)`. Field names,
  order and annotations are exact; nullable fields remain required constructor arguments.
- Repeated values use `tuple[...]`, never list, set, generator or a mutable default.
- `center_changes` uses `Mapping[OverlayCenterAxis, OverlayCenterAxisChange]`; DOCUMENT and
  FEE milestones represent no center change as an empty mapping, never `None` or a list.
- Reuse the accepted LC, DE, FO and decision-gate types named below. Do not copy, alias or
  widen their vocabularies in the overlay module.
- Each overlay enum is a string enum whose member name and wire value are identical. The
  exact ordered members are:

```text
OverlayCenterAxis: BUSINESS_STAGE | OFFICIAL_PROCEDURE_STAGE | LEGAL_STATUS
OverlayWarningKind: UNVERIFIED | CUSTOMER_DECISION_GATE | CONFLICT | REFERENCE_ONLY
OverlayFeeRelatedFactKind: DRAFT | PAY_LIST | PAYMENT | OFFICIAL_EVIDENCE
OverlayGateResolutionStatus: RESOLVED | UNRESOLVED
```

### Exact DTO fields, order and annotations

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleOverlayQuery:
    after_sequence: int
    limit: int
    as_of_revision: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayCenterSnapshot:
    business_stage: BusinessStage | None
    official_procedure_stage: OfficialProcedureStage | None
    legal_status: LegalStatus | None
    effective_at: datetime | None
    verification_status: ConfirmationStatus | None
    source_event_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayCenterAxisChange:
    previous_value: BusinessStage | OfficialProcedureStage | LegalStatus | None
    current_value: BusinessStage | OfficialProcedureStage | LegalStatus | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayDocumentEvidence:
    version: EvidenceVersionResult
    derivations: tuple[EvidenceDerivationResult, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayWorkPackageReceipt:
    receipt_id: str
    receipt_kind: str
    receipt_attachment_id: str | None
    receiving_case_no: str | None
    submitter: str | None
    received_at: datetime | None
    archive_status: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayWorkPackage:
    package_id: str
    package_kind: str
    status: str
    source_document_id: str | None
    reply_document_id: str | None
    manifest_evidence_version_ids: tuple[str, ...]
    receipts: tuple[OverlayWorkPackageReceipt, ...]
    missing_gate_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayTask:
    task_id: str
    document_id: str | None
    task_template_id: str | None
    title: str | None
    due_date: date | None
    internal_due_date: date | None
    status: str
    done_at: datetime | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayFeeLine:
    line_id: str
    fee_code: str
    fee_name: str
    fee_year_key: int
    official_full_amount: str | None
    reduction_ratio: str
    payable_amount: str
    source_amount: str | None
    source_date: date | None
    difference_review_state: FeeDifferenceReviewState


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayFeeRelatedFact:
    kind: OverlayFeeRelatedFactKind
    object_id: str
    status: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayFeeObligation:
    obligation_id: str
    source_activity_id: str
    source_document_id: str | None
    source_status: FeeSourceStatus
    fee_domain: FeeDomain
    obligation_type: str
    due_date: date | None
    currency: str
    statuses: FeeObligationStatuses
    lines: tuple[OverlayFeeLine, ...]
    related_facts: tuple[OverlayFeeRelatedFact, ...]
    supersedes_obligation_id: str | None
    supersede_reason: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayWarning:
    kind: OverlayWarningKind
    code: str
    message: str
    activity_id: str | None
    source_object_type: str | None
    source_object_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayDecisionGate:
    gate_code: DecisionGateCode
    requested_scope_key: str
    resolution_status: OverlayGateResolutionStatus
    gate_id: str | None
    resolved_scope_key: str | None
    decision_value: str | None
    source_reference: str | None
    source_version: str | None
    confirmed_by: str | None
    effective_at: datetime | None
    unresolved_reason: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayLegacyConflict:
    code: str
    activity_id: str | None
    message: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayMilestone:
    sequence: int
    activity_id: str
    lane: ActivityLane
    activity_type: str
    source_activity_id: str | None
    effective_at: datetime
    confirmation_status: ConfirmationStatus
    center_changes: Mapping[OverlayCenterAxis, OverlayCenterAxisChange]
    document_evidence: tuple[OverlayDocumentEvidence, ...]
    work_packages: tuple[OverlayWorkPackage, ...]
    tasks: tuple[OverlayTask, ...]
    fee_obligations: tuple[OverlayFeeObligation, ...]
    evidence_summary: tuple[EvidenceReference, ...]
    warnings: tuple[OverlayWarning, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleOverlay:
    case_id: str
    lifecycle_revision: int
    generated_at: datetime
    center_snapshot: OverlayCenterSnapshot
    milestones: tuple[OverlayMilestone, ...]
    decision_gates: tuple[OverlayDecisionGate, ...]
    warnings: tuple[OverlayWarning, ...]
    legacy_conflicts: tuple[OverlayLegacyConflict, ...]
    next_cursor: int | None
    has_more: bool
```

The module publicly exports all four enums and all fifteen DTOs above. It reuses
`BusinessStage`, `OfficialProcedureStage`, `LegalStatus`, `ConfirmationStatus`,
`ActivityLane` and `EvidenceReference` from LC contracts;
`EvidenceVersionResult` and `EvidenceDerivationResult` from DE contracts; and
`FeeDifferenceReviewState`, `FeeSourceStatus`, `FeeDomain` and
`FeeObligationStatuses` from FO contracts. `DecisionGateCode` is imported from the
accepted decision-gate record-service contract. The accepted DE raw-attachment
prerequisite extends the reused `EvidenceRole` carried by `EvidenceVersionResult`; this
task does not define another role or evidence DTO.

### Delta-3 inherited RAW guard boundary

- This task keeps exactly one direct RAW-role prerequisite:
  `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`. Delta-3 makes that prerequisite
  directly depend on both the RAW registration guard and the external-submission
  positive-role guard, so this task inherits both guards transitively. Do not add either
  guard as a direct dependency or duplicate either service rule here.
- `EvidenceRole.RAW_ATTACHMENT` remains an intake-only classification. Carrying it in the
  reused `EvidenceVersionResult` grants no overlay inclusion, document or formal-role
  semantics, decision-gate authority, or lifecycle-center authority. It cannot by itself
  populate `OverlayDocumentEvidence`, resolve a gate or change center state; this schema
  task adds no RAW applicability or authority rule.

### Wire invariants

- Overlay money fields are decimal strings with exactly two fractional digits;
  `reduction_ratio` is a decimal string with exactly four fractional digits. The schema
  carries those strings without float conversion, quantization or money calculation.
- Milestone warnings preserve their activity-local association. Top-level warnings are
  the current page/snapshot aggregation. This schema exposes both tuples; aggregation and
  deduplication rules belong to later joins.
- `LifecycleOverlay.decision_gates` is an ordered tuple that permits repeated
  `gate_code`. It represents all eight distinct `DecisionGateCode` values as exactly 29
  scoped entries: one `requested_scope_key=f"case:{case_id}"` entry for each of the seven
  non-legacy codes in enum order, followed by 22 `LEGACY_FORM_CLASS` entries ordered
  `form-001` through `form-022`.
- Gate-entry identity is exactly `(gate_code, requested_scope_key)`. A code-only dict,
  `Record<gate_code, ...>`, code-only uniqueness assertion, or deduplication by
  `gate_code` is prohibited. `requested_scope_key="ALL-22"` is never represented as an
  overlay request; a `form-NNN` entry may retain `resolved_scope_key="ALL-22"` when the
  downstream resolver selects the accepted fallback carrier.
- A resolved entry losslessly projects the accepted read result and has
  `unresolved_reason=None`. For any one of
  `DECISION_GATE_NOT_FOUND`, `DECISION_GATE_REVOKED`,
  `DECISION_GATE_NOT_EFFECTIVE`, `DECISION_GATE_CANDIDATE_MULTIPLICITY`,
  `DECISION_GATE_CURRENT_IDENTITY_CONFLICT`,
  `DECISION_GATE_CURRENT_ROW_CORRUPT` or
  `DECISION_GATE_LEGACY_MAP_CORRUPT`, the downstream join represents only that entry as
  `UNRESOLVED`, preserves the exact error code in `unresolved_reason`, and sets
  `gate_id`, `resolved_scope_key`, `decision_value`, `source_reference`,
  `source_version`, `confirmed_by` and `effective_at` all to `None`. Error translation,
  resolver isolation and continuation across the other 28 entries are not implemented by
  this schema task.
- One overlay invocation has one timezone-naive UTC timestamp identity:
  `LifecycleOverlay.generated_at` is the value downstream composition must reuse as
  `as_of` for all 29 decision-gate resolutions. This task freezes that single-value
  schema invariant only; clock capture, transaction reuse, resolver calls and join
  behavior belong downstream.

### Cursor contract

- The first query is `after_sequence=0, as_of_revision=None`.
- A service freezes revision `R`; subsequent pages reuse `as_of_revision=R` and select
  milestones where `sequence > after_sequence AND sequence <= R`.
- `next_cursor` equals the page's final sequence only when `has_more=True`; otherwise it
  is `None`.
- This task freezes only the query and response fields. Limit validation, revision reads
  and keyset behavior remain owned by the overlay keyset task.

### Exact contract-test boundary

`backend/tests/test_v8_lifecycle_overlay_contracts.py` must assert:

1. The four exact ordered enum vocabularies and the reused deep enum/DTO identities.
2. Every DTO is frozen, slotted and keyword-only, with the exact ordered fields and
   resolved annotations above; every repeated field is a tuple and `center_changes` is a
   `Mapping`.
3. Representative fee strings preserve two/four decimal wire forms without introducing
   `Decimal` or float fields in the overlay schema.
4. A 29-entry `decision_gates` tuple preserves eight distinct codes, all 22 repeated
   legacy-code entries, ordering and 29 unique composite identities. It must explicitly
   prove that a code-only dict/uniqueness model cannot represent the contract.
5. Resolved and unresolved gate fixtures preserve the exact nullable fields and exact
   unresolved reason codes above, including a requested `form-NNN` with resolved
   `ALL-22` provenance.
6. `LifecycleOverlayQuery` and cursor response fields have the exact order and
   annotations above, and the schema exposes one `generated_at` rather than a second
   per-gate timestamp.

The exact test must remain a pure interface test: no ORM/database access, resolver or
join invocation, HTTP request, UI behavior, clock read or business aggregation test.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-CONTRACTS-20260712-01`
- `FPMS-V8-DE-CONTRACTS-20260712-01`
- `FPMS-V8-FO-CONTRACTS-20260712-01`
- `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- `transitive through the RAW-role prerequisite` —
  `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` and
  `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`; neither is a direct
  dependency of this overlay-contract task.

- Approved source dependency cell (verbatim): all three deep-module contracts

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OVERLAY-CONTRACTS-20260712-01.md`
- `backend/app/modules/cases/lifecycle_overlay_schemas.py`
- `backend/tests/test_v8_lifecycle_overlay_contracts.py`
- `artifacts/FPMS-V8-OVERLAY-CONTRACTS-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_contracts.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_contracts.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_schemas.py tests/test_v8_lifecycle_overlay_contracts.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_schemas.py tests/test_v8_lifecycle_overlay_contracts.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_schemas.py tests/test_v8_lifecycle_overlay_contracts.py`
- `git diff --check -- backend/app/modules/cases/lifecycle_overlay_schemas.py backend/tests/test_v8_lifecycle_overlay_contracts.py tasks/postdemo/v8/FPMS-V8-OVERLAY-CONTRACTS-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OVERLAY-CONTRACTS-20260712-01`
- Evidence validation (single lane; no manifest or peer arguments): `python3 scripts/atomic_evidence_validate.py FPMS-V8-OVERLAY-CONTRACTS-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- If validation has post-init peer dirt, use that same wrapper with exactly one common
  authoritative execution `--manifest` containing this task and every peer, plus one
  `--concurrent-task <PEER-TASK-ID>` for every peer, as required by delta-3 G2. Never mix
  peers from different manifests or omit a peer ID.

## Evidence Path

- `artifacts/FPMS-V8-OVERLAY-CONTRACTS-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-CONTRACTS-20260712-01` pass. Only then may this task be reported PASS.
