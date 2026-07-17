# FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `267`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `805`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-UI`

- RED expectation: Targeted Playwright fails because the page still issues the fixed
  `FILING_ACCEPTED` preview on mount, cannot send the strict explicit-date request or
  conflates an `ESTIMATE` with persisted overlay obligations/draft/payment state.
- GREEN expectation: Targeted Playwright, exact-file ESLint and the serialized full
  frontend typecheck pass with explicit user-triggered preview, lossless estimate and
  overlay rendering, and no inferred business state.

## Exact Closure Slice

Replace `CaseFeesTab`'s fixed `FILING_ACCEPTED` request with an explicit user-selected estimate context; display ESTIMATE separately from real overlay obligations and never infer a draft/payment.

## Explicit Non-Closure

No backend change, second page capability or frontend business-state calculation. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section is authoritative for High implementation. The existing canonical task is
the sole owner of the `CaseFeesTab.vue` callsite migration and its exact Playwright
specification; do not create a P3 prerequisite, duplicate page owner or compatibility
task. This task consumes the accepted document-review, official-fee-preview and
lifecycle-overlay frontend adapters after they pass. It does not change any adapter or
backend contract.

### Explicit estimate controls and request lifecycle

- Remove the fixed `FILING_ACCEPTED` request and every preview call from mount-time page
  loading. Loading the case-fees tab may read persisted fee drafts and the lifecycle
  overlay, but it issues zero official-fee-preview requests until the user explicitly
  chooses an estimate context and triggers the estimate.
- Render an explicit trigger-context selector with no hidden or fixed trigger. The
  supported choices are the server vocabulary `FILING_ACCEPTED` and
  `REEXAM_REQUESTED`; the selected wire value is sent unchanged. Do not derive a trigger
  from case status, lifecycle stage, document kind, existing obligation or draft.
- Render a `费率生效日` date control whose initial value is empty. Do not initialize it
  from today, a case date, document date, rate row, browser clock or server response.
  Invoking the estimate action while it is empty visibly shows exactly
  `请选择费率生效日期` and sends no preview request.
- `trigger_context.source_document_id` is always present in the request. It is the exact
  explicitly selected reviewed-document/evidence identifier supplied through the
  accepted document-review frontend adapter, or JSON `null` when the user has selected
  no source document. Do not infer it from the case, overlay, trigger or a current/final
  document flag.
- The initial explicit action and every refresh are user actions. Changing a trigger,
  source document or effective date never calls the preview automatically. After an
  input changes, an already rendered estimate is stale and must be cleared before the
  next explicit action; it must not be relabelled as matching the new inputs.

The sole preview call remains the accepted `previewOfficialFeeCandidates` export and
sends exactly the strict request shape:

```json
{
  "case_id": "<case-id>",
  "trigger_context": {
    "trigger": "<explicit-selected-trigger>",
    "source_document_id": "<explicit-selected-id-or-null>"
  },
  "currency": "CNY",
  "rate_effective_on": "<explicit-selected-YYYY-MM-DD>"
}
```

`rate_effective_on` is the selected ISO calendar-date string, not a timestamp. The page
must not send or recognize the removed top-level `trigger_event` or top-level
`source_document_id`, omit `rate_effective_on`, translate the strict request into the
legacy shape, or request a legacy overload. There is exactly one request contract.

### ESTIMATE and real-obligation separation

- Render the preview in a dedicated estimate region that visibly identifies the
  server-returned `estimate_status` as `ESTIMATE`. An estimate has no obligation ID,
  activity ID, draft ID, PayList ID, payment ID or idempotency identity, and the page
  must not synthesize any of them.
- Preserve the estimate candidate order and its nested `line` and `source`
  associations. Display `official_full_amount`, `payable_amount`, nullable
  `source_amount` and `total_payable_amount` as the exact two-fractional-digit wire
  strings, and `reduction_ratio` as the exact four-fractional-digit wire string. Never
  pass these values through `Number`, `parseFloat`, arithmetic, rounding or a lossy
  money formatter.
- Keep candidate provenance visible and associated with its candidate: `rate_id`,
  `source_document_id`, `source_doc`, `source_url`, `source_policy`, `source_version`,
  `status`, plus the line's `source_date` and `difference_review_state`. Null remains
  null/empty presentation; the page must not invent a fallback source or verified
  status.
- Render real persisted obligations from the accepted lifecycle-overlay adapter in a
  separate `真实费用义务` region. Preserve server order and each obligation's
  `obligationId`, activity/document source identities, source status, fee domain,
  obligation type, due date, status object, lines, related facts and supersession
  provenance. Preserve every obligation decimal string exactly as received.
- An empty real-obligation collection remains empty even when an estimate has
  candidates. Estimate candidates are never appended, counted or keyed as obligations.
  Conversely, an overlay obligation is never presented as an estimate merely because
  it has matching fee codes or amounts.
- Existing persisted fee-draft records remain a third, independent server-backed
  presentation. Preview success/refresh/error must not add a draft row, change a draft
  status, infer payment, navigate to draft creation, record an instruction or issue any
  obligation/draft/PayList/payment mutation. Only a later explicit task may own those
  state transitions.

Preview errors retain the accepted API error code/message/details and clear only the
estimate result. They do not hide persisted overlay obligations, synthesize a missing
rate, fall back to legacy preview data or infer any obligation/draft/payment state.

### Exact Playwright acceptance

`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-estimate-obligation.spec.ts`
MUST prove through the case-fees tab:

1. On first render the `费率生效日` value is empty and the preview request count is zero;
   an explicit estimate attempt shows `请选择费率生效日期` and still sends zero preview
   requests.
2. After an explicit trigger, optional reviewed source-document choice and effective
   date are selected, the explicit action sends exactly one request with nested
   `trigger_context`, explicit JSON-null-or-selected `source_document_id`, `currency`
   `CNY` and the selected `rate_effective_on`.
3. The captured request contains no `trigger_event`, no top-level
   `source_document_id`, no missing-date fallback and no additional legacy key. Changing
   any selection sends no request; the next explicit refresh sends exactly one new
   strict request with the newly selected values.
4. The estimate region visibly retains `ESTIMATE`, candidate order, exact decimal
   strings and every candidate source/provenance field from the response fixture.
5. A lifecycle-overlay fixture renders real obligations in the separate
   `真实费用义务` region with exact IDs, status/source associations, related facts,
   supersession provenance and decimal strings. Estimate candidates do not change the
   real-obligation row count, including the zero-obligation case.
6. Persisted draft fixtures remain separate, and request/navigation spies prove that
   initial render, estimate and refresh perform no draft, obligation, instruction,
   PayList or payment mutation and infer none of those states.
7. A preview error leaves real obligations and persisted drafts visible, exposes the
   accepted error information and produces no legacy fallback request or synthesized
   state.

The RED is any fixed/automatic preview, missing strict explicit-date payload, lossy
decimal/provenance rendering, estimate/obligation conflation or inferred mutation. GREEN
does not authorize a legacy overload, adapter edit, backend edit or instruction/draft
workflow.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
- `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`
- `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): preview FE adapter, overlay FE adapter

### Shared ownership serialization

- `frontend/src/modules/cases/components/CaseFeesTab.vue` order key `1`; project this order only across owners present in the active manifest.
- `FRONTEND_TYPECHECK_VERIFICATION` order key `11`; run the full frontend typecheck only
  after the document-review, preview and overlay frontend adapters are complete.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01.md`
- `frontend/src/modules/cases/components/CaseFeesTab.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-estimate-obligation.spec.ts`
- `artifacts/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-fees-estimate-obligation.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-fees-estimate-obligation.spec.ts --workers=1`
- `cd frontend && npx eslint src/modules/cases/components/CaseFeesTab.vue --max-warnings 0`
- `cd frontend && npm run typecheck`
- `git diff --check -- frontend/src/modules/cases/components/CaseFeesTab.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-estimate-obligation.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
