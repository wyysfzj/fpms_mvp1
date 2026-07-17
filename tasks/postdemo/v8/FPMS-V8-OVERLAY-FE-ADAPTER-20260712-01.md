# FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `266`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `804`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-FE-ADAPTER`

- RED expectation: The exact lifecycle-overlay import/shape probe makes serialized `FE-TYPE` fail while the adapter cannot represent all 29 ordered entries, repeated `gateCode`, composite identity or exact decimal-string DTOs without flattening.
- GREEN expectation: The exact contract probe, exact-file ESLint and serialized `FE-TYPE` pass with count-capable gate types, composite consumption identity and lossless DTO/provenance preservation.

## Exact Closure Slice

Dedicated typed adapter; preserve decimal strings and server associations.

## Explicit Non-Closure

No page behavior, server-state inference or backend change. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section is authoritative for High implementation. It freezes only the typed
frontend adapter for the accepted overlay HTTP response. It does not add page behavior,
resolve or activate a decision gate, calculate money, infer server state, paginate
milestones locally or change a backend contract.

### Exact public adapter surface

`frontend/src/api/lifecycleOverlay.types.ts` exports the four exact string unions and
the fifteen DTOs below. JSON `snake_case` may be mapped to the public `camelCase` names,
but every value and association must survive unchanged. Nullable server fields are
required properties with `| null`; they are not optional properties. Repeated fields are
ordered `readonly ...[]` values (or readonly tuples where a literal probe fixes the
count), never `Set`, `Map`, generator or `Record`.

```ts
export type OverlayCenterAxis =
    | 'BUSINESS_STAGE'
    | 'OFFICIAL_PROCEDURE_STAGE'
    | 'LEGAL_STATUS'

export type OverlayWarningKind =
    | 'UNVERIFIED'
    | 'CUSTOMER_DECISION_GATE'
    | 'CONFLICT'
    | 'REFERENCE_ONLY'

export type OverlayFeeRelatedFactKind =
    | 'DRAFT'
    | 'PAY_LIST'
    | 'PAYMENT'
    | 'OFFICIAL_EVIDENCE'

export type OverlayGateResolutionStatus = 'RESOLVED' | 'UNRESOLVED'

export interface LifecycleOverlayQuery {
    afterSequence: number
    limit: number
    asOfRevision: number | null
}

export interface OverlayCenterSnapshot {
    businessStage: BusinessStage | null
    officialProcedureStage: OfficialProcedureStage | null
    legalStatus: LegalStatus | null
    effectiveAt: string | null
    verificationStatus: ConfirmationStatus | null
    sourceEventId: string | null
}

export interface OverlayCenterAxisChange {
    previousValue: BusinessStage | OfficialProcedureStage | LegalStatus | null
    currentValue: BusinessStage | OfficialProcedureStage | LegalStatus | null
}

export interface OverlayDocumentEvidence {
    version: EvidenceVersionResult
    derivations: readonly EvidenceDerivationResult[]
}

export interface OverlayWorkPackageReceipt {
    receiptId: string
    receiptKind: string
    receiptAttachmentId: string | null
    receivingCaseNo: string | null
    submitter: string | null
    receivedAt: string | null
    archiveStatus: string
}

export interface OverlayWorkPackage {
    packageId: string
    packageKind: string
    status: string
    sourceDocumentId: string | null
    replyDocumentId: string | null
    manifestEvidenceVersionIds: readonly string[]
    receipts: readonly OverlayWorkPackageReceipt[]
    missingGateCodes: readonly string[]
}

export interface OverlayTask {
    taskId: string
    documentId: string | null
    taskTemplateId: string | null
    title: string | null
    dueDate: string | null
    internalDueDate: string | null
    status: string
    doneAt: string | null
}

export interface OverlayFeeLine {
    lineId: string
    feeCode: string
    feeName: string
    feeYearKey: number
    officialFullAmount: string | null
    reductionRatio: string
    payableAmount: string
    sourceAmount: string | null
    sourceDate: string | null
    differenceReviewState: FeeDifferenceReviewState
}

export interface OverlayFeeRelatedFact {
    kind: OverlayFeeRelatedFactKind
    objectId: string
    status: string
}

export interface OverlayFeeObligation {
    obligationId: string
    sourceActivityId: string
    sourceDocumentId: string | null
    sourceStatus: FeeSourceStatus
    feeDomain: FeeDomain
    obligationType: string
    dueDate: string | null
    currency: string
    statuses: FeeObligationStatuses
    lines: readonly OverlayFeeLine[]
    relatedFacts: readonly OverlayFeeRelatedFact[]
    supersedesObligationId: string | null
    supersedeReason: string | null
}

export interface OverlayWarning {
    kind: OverlayWarningKind
    code: string
    message: string
    activityId: string | null
    sourceObjectType: string | null
    sourceObjectId: string | null
}

export interface OverlayDecisionGate {
    gateCode: DecisionGateCode
    requestedScopeKey: string
    resolutionStatus: OverlayGateResolutionStatus
    gateId: string | null
    resolvedScopeKey: string | null
    decisionValue: string | null
    sourceReference: string | null
    sourceVersion: string | null
    confirmedBy: string | null
    effectiveAt: string | null
    unresolvedReason: string | null
}

export interface OverlayLegacyConflict {
    code: string
    activityId: string | null
    message: string | null
}

export interface OverlayMilestone {
    sequence: number
    activityId: string
    lane: ActivityLane
    activityType: string
    sourceActivityId: string | null
    effectiveAt: string
    confirmationStatus: ConfirmationStatus
    centerChanges: Readonly<Partial<Record<OverlayCenterAxis, OverlayCenterAxisChange>>>
    documentEvidence: readonly OverlayDocumentEvidence[]
    workPackages: readonly OverlayWorkPackage[]
    tasks: readonly OverlayTask[]
    feeObligations: readonly OverlayFeeObligation[]
    evidenceSummary: readonly EvidenceReference[]
    warnings: readonly OverlayWarning[]
}

export interface LifecycleOverlay {
    caseId: string
    lifecycleRevision: number
    generatedAt: string
    centerSnapshot: OverlayCenterSnapshot
    milestones: readonly OverlayMilestone[]
    decisionGates: readonly OverlayDecisionGate[]
    warnings: readonly OverlayWarning[]
    legacyConflicts: readonly OverlayLegacyConflict[]
    nextCursor: number | null
    hasMore: boolean
}
```

`BusinessStage`, `OfficialProcedureStage`, `LegalStatus`, `ConfirmationStatus`,
`ActivityLane`, `EvidenceReference`, `EvidenceVersionResult`,
`EvidenceDerivationResult`, `FeeDifferenceReviewState`, `FeeSourceStatus`, `FeeDomain`,
`FeeObligationStatuses` and `DecisionGateCode` mirror their accepted HTTP wire types
exactly. The adapter must not replace any of them with `any`, `unknown`, an unbounded
`string`, a locally narrowed vocabulary or a lossy duplicate DTO. Timestamps and dates
remain wire strings; this task does not parse them into `Date` objects.

`frontend/src/api/lifecycleOverlay.ts` exports exactly:

```ts
export function lifecycleOverlayGateKey(
    gate: Pick<OverlayDecisionGate, 'gateCode' | 'requestedScopeKey'>,
): `${DecisionGateCode}:${string}`

export function getLifecycleOverlay(
    caseId: string,
    query: LifecycleOverlayQuery,
): Promise<LifecycleOverlay>
```

`getLifecycleOverlay` calls the accepted bodyless
`GET /cases/{case_id}/lifecycle-overlay`, maps `afterSequence`, `limit` and
`asOfRevision` to the exact HTTP query parameters, and losslessly maps the response. It
does not sort, filter, merge, deduplicate, recalculate or synthesize any response field.
The key helper returns exactly `` `${gate.gateCode}:${gate.requestedScopeKey}` ``. An
equivalent readonly `[gateCode, requestedScopeKey]` identity would satisfy the semantic
contract, but this task freezes the string helper above as the single exported
consumption identity.

### Decimal-string and association invariants

- `officialFullAmount`, `payableAmount` and `sourceAmount` remain two-fractional-digit
  decimal strings (or the exact declared `null`); `reductionRatio` remains a
  four-fractional-digit decimal string. None may become `number`, `number | string`,
  `Decimal`, or a value produced by `Number`, `parseFloat`, rounding or arithmetic.
- The adapter preserves milestone-local warnings separately from top-level warnings,
  document evidence with its derivations, work packages with their receipts, fee lines
  and related facts with their owning obligation, and every source/status/provenance
  field. It must not flatten nested collections into detached lookup records.
- `centerChanges` preserves axis association. DOCUMENT/FEE milestones may carry an empty
  object; the adapter must not convert that value to `null` or an array.

### Frozen 29-entry decision-gate collection and paging

- `LifecycleOverlay.decisionGates` is a count-capable ordered array/tuple, not an object.
  It contains exactly 29 entries in server order and permits repeated `gateCode`.
- Entries 1–7 are the seven non-legacy gate codes in accepted enum order, each with
  `requestedScopeKey=case:${caseId}`. Entries 8–29 repeat
  `DG-LEGACY-FORM-CLASS` with requested scopes `form-001` through `form-022` in ascending
  order.
- Consumption identity is the composite
  `` `${gateCode}:${requestedScopeKey}` `` returned by `lifecycleOverlayGateKey`.
  `Record<DecisionGateCode, ...>`, a map keyed only by `gateCode`, code-only uniqueness,
  or any code-only deduplication/replacement is prohibited.
- The adapter never accepts or produces `requestedScopeKey='ALL-22'`. When the accepted
  resolver uses the aggregate fallback carrier, the individual entry remains
  `requestedScopeKey='form-NNN'`, while `resolvedScopeKey='ALL-22'`, its extracted
  `decisionValue`, and all source provenance remain unchanged.
- Milestone pagination does not paginate gate state. Every HTTP page is mapped with its
  complete ordered 29-entry decision-gate snapshot, including later pages and pages with
  no milestones. The adapter never carries only the first page's gates, merges page gate
  arrays, or drops the snapshot while mapping `nextCursor`/`hasMore`.

### Exact contract probe and typecheck boundary

`frontend/src/api/contracts/v8_lifecycle_overlay.contract.ts` is a compile-only exact
import/shape probe. It must assert:

1. All four literal unions, all fifteen public DTO names, exact property names,
   nullability, nesting and readonly ordered-collection types above; dates/timestamps are
   strings and the four money/ratio fields cannot accept numbers.
2. A literal 29-entry `decisionGates` fixture satisfies the public collection type,
   exposes a numeric `length`, preserves seven `case:<case_id>` identities plus all 22
   `form-NNN` identities, and permits 22 occurrences of the legacy `gateCode`.
3. Mapping the fixture through `lifecycleOverlayGateKey` yields 29 unique composite keys
   while a code-only key set has only eight values. Type assertions and
   `@ts-expect-error` probes reject a `Record<DecisionGateCode, OverlayDecisionGate>`, a
   single-entry-per-code shape, number-valued decimal fields, missing
   `requestedScopeKey`, and flattened nested associations as substitutes for
   `LifecycleOverlay`.
4. A requested `form-NNN` fixture may retain `resolvedScopeKey='ALL-22'` plus its exact
   decision/source fields, but a requested `ALL-22` fixture is rejected by the probe's
   exact overlay fixture builder.
5. First, middle, final and empty-milestone page fixtures each retain the full 29-entry
   gate snapshot while only milestone/cursor fields vary; the adapter response type has
   no first-page-only or code-indexed gate alternative.

The RED is the absent public surface or any adapter/type model that cannot express these
fixtures without widening, flattening or code-only replacement. GREEN is the exact
compile probe plus serialized project typecheck; it does not authorize a page, runtime
gate resolver, business calculation or backend edit.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OVERLAY-HTTP-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): HTTP

### Shared ownership serialization

- `FRONTEND_TYPECHECK_VERIFICATION` order key `10`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01.md`
- `frontend/src/api/lifecycleOverlay.ts`
- `frontend/src/api/lifecycleOverlay.types.ts`
- `frontend/src/api/contracts/v8_lifecycle_overlay.contract.ts`
- `artifacts/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd frontend && npm run typecheck`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd frontend && npm run typecheck`
- `cd frontend && npx eslint src/api/lifecycleOverlay.ts src/api/lifecycleOverlay.types.ts src/api/contracts/v8_lifecycle_overlay.contract.ts --max-warnings 0`
- `git diff --check -- frontend/src/api/lifecycleOverlay.ts frontend/src/api/lifecycleOverlay.types.ts frontend/src/api/contracts/v8_lifecycle_overlay.contract.ts tasks/postdemo/v8/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
