# FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `106`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `534`
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

- RED expectation: The exact dedicated contract probe fails its isolated TypeScript
  compile before the named strict request/result exports and function signature exist.
- GREEN expectation: The isolated contract-probe compile and exact-file ESLint pass
  without status/amount inference or a legacy request overload.

## Exact Closure Slice

Type the explicit estimate context/result and preserve the server's ESTIMATE label, decimal strings and source metadata without creating a frontend obligation.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section is the complete High implementation contract for this typed adapter. It
consumes the accepted strict preview HTTP dependency without changing the existing route,
adding page behavior or restoring any legacy request shape.

### Exact public preview surface

`frontend/src/api/fees.types.ts` replaces the three legacy preview-specific exports
`OfficialFeePreviewPayload`, `OfficialFeePreviewCandidate` and `OfficialFeePreview` with
exactly these two public preview interfaces. Nested objects stay inline so this task does
not invent another public preview DTO vocabulary:

```ts
export interface OfficialFeeEstimateContext {
    case_id: string
    trigger_context: {
        trigger: string
        source_document_id: string | null
    }
    currency: 'CNY'
    rate_effective_on: string
}

export interface OfficialFeeEstimateResult {
    case_id: string
    estimate_status: 'ESTIMATE'
    trigger_context: {
        trigger: string
        source_document_id: string | null
    }
    currency: 'CNY'
    candidates: {
        line: {
            fee_code: string
            fee_name: string
            fee_year_key: number
            official_full_amount: string | null
            reduction_ratio: string
            payable_amount: string
            source_amount: string | null
            source_date: string | null
            difference_review_state: 'MATCHED' | 'SOURCE_PENDING' | 'REVIEW_REQUIRED'
        }
        source: {
            rate_id: string | null
            source_document_id: string | null
            source_doc: string | null
            source_url: string | null
            source_policy: string | null
            source_version: string | null
            status: 'VERIFIED' | 'REVIEW_REQUIRED' | 'LEGACY_UNVERIFIED'
        }
    }[]
    total_payable_amount: string
}
```

`rate_effective_on` is a required caller-supplied HTTP date string in exact
`YYYY-MM-DD` form. The adapter passes it unchanged; it must not default it from system
time, a case, a document or a rate row, and must not parse it into a JavaScript `Date`.
The backend remains the shape/calendar-date validator. Nested
`trigger_context.source_document_id` is required and nullable; omission must not be
silently converted to `null` by the adapter.

`frontend/src/api/fees.ts` preserves the existing function name with exactly this
single-object signature:

```ts
export async function previewOfficialFeeCandidates(
    context: OfficialFeeEstimateContext,
): Promise<OfficialFeeEstimateResult>
```

The function performs one
`POST /fees/official-fee-preview` with `context` as the exact JSON body and returns
`response.data` as the direct `OfficialFeeEstimateResult`. It does not rename, flatten,
sort, group, deduplicate, calculate or synthesize any request or response field. Remove
the legacy `BackendOfficialFeePreview`/`mapOfficialFeePreview` conversion path: using
`Number`, `parseFloat`, arithmetic, default zero or another lossy money conversion is
prohibited.

There is no overload, alias or compatibility branch accepting top-level
`trigger_event`, top-level `source_document_id`, optional/defaulted currency or an omitted
effective date. In particular, do not retain the old `OfficialFeePreviewPayload` call
shape solely to keep the current `CaseFeesTab.vue` compiling.

### Exact value and identity invariants

- `currency` is the literal `CNY` in both request and result; `estimate_status` is the
  literal `ESTIMATE`.
- `official_full_amount`, `payable_amount`, non-null `source_amount` and
  `total_payable_amount` remain fixed two-fractional-digit decimal strings;
  `reduction_ratio` remains a fixed four-fractional-digit decimal string. Null remains
  null and no decimal string becomes a JavaScript number.
- `source_date` remains a nullable `YYYY-MM-DD` wire string. Candidate order and the
  nested `line`/`source` association are preserved exactly.
- All nested source provenance survives unchanged: `rate_id`, `source_document_id`,
  `source_doc`, `source_url`, `source_policy`, `source_version` and `status`.
- The request/result and adapter expose no obligation ID or status, draft ID or status,
  activity ID, PayList/export ID, payment ID, idempotency key, generated preview ID,
  `draft_type`, `preview_only`, `total_gov`, quantity, unit price or legacy
  `trigger_event` field. Existing `case_id` and provenance `rate_id` are not synthesized
  persistence identities.

### Dedicated compile-time contract probe

`frontend/src/api/contracts/v8_fee_estimate_preview.contract.ts` imports exactly
`OfficialFeeEstimateContext`, `OfficialFeeEstimateResult` and
`previewOfficialFeeCandidates`. It must prove at compile time:

1. a direct request literal requires `case_id`, nested `trigger_context` with explicit
   nullable `source_document_id`, literal `currency: 'CNY'` and caller-owned
   `rate_effective_on`;
2. the function accepts that one object and returns
   `Promise<OfficialFeeEstimateResult>`;
3. `estimate_status`/currency are literals, every amount/ratio is a string, nullable
   values remain nullable, and line/source provenance remains nested;
4. direct legacy `trigger_event` input, omitted `rate_effective_on`, non-CNY currency,
   numeric money assignments and prohibited identity-property access are compile-time
   errors.

The probe is the only typecheck owner for this adapter task. It must not import or edit
`CaseFeesTab.vue` or its Playwright test.

### Existing callsite dependency break

The current `CaseFeesTab.vue` still calls the legacy fixed `FILING_ACCEPTED` shape, so a
full frontend typecheck is an expected failure after this strict adapter lands. The
existing canonical
`FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01` task solely owns the later
page migration and
`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-estimate-obligation.spec.ts`.
After this adapter and the overlay FE adapter are ready, that canonical UI task supplies
the explicit user-selected context/effective date, separates ESTIMATE from real
obligations, and owns its exact Playwright, exact-file ESLint and full frontend
typecheck. Do not create a duplicate prerequisite or move page/test ownership here.

## Explicit Non-Closure

No page behavior, server-state inference or backend change. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): preview HTTP

### Shared ownership serialization

- `frontend/src/api/fees.ts` order key `2`; project this order only across owners present in the active manifest.
- `frontend/src/api/fees.types.ts` order key `2`; project this order only across owners present in the active manifest.
- `FRONTEND_TYPECHECK_VERIFICATION` order key `2`; for this task the ownership is only
  the isolated contract-probe command below, not `npm run typecheck`. Project this order
  only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01.md`
- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/api/contracts/v8_fee_estimate_preview.contract.ts`
- `artifacts/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- Dependency gate: `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
- RED command: `cd frontend && npx tsc --noEmit --skipLibCheck --strictNullChecks --target ES2022 --module ESNext --moduleResolution Bundler src/api/contracts/v8_fee_estimate_preview.contract.ts`; run it before implementation and preserve the expected failure proving the missing strict surface or a narrowed nullable wire field.
- GREEN and scoped checks:
- `cd frontend && npx tsc --noEmit --skipLibCheck --strictNullChecks --target ES2022 --module ESNext --moduleResolution Bundler src/api/contracts/v8_fee_estimate_preview.contract.ts`
- `cd frontend && npx eslint src/api/fees.ts src/api/fees.types.ts src/api/contracts/v8_fee_estimate_preview.contract.ts --max-warnings 0`
- `git diff --check -- frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/api/contracts/v8_fee_estimate_preview.contract.ts tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

`npm run typecheck`, `vue-tsc --noEmit` over the frontend project, another whole-project
type command and any command that pulls `CaseFeesTab.vue` into this task are explicitly
prohibited. The exact isolated `tsc` command above is the only RED/GREEN type command for
this adapter.

## Evidence Path

- `artifacts/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact isolated RED is preserved; the minimum allowlisted change makes the exact
isolated GREEN, exact-file ESLint and scoped diff checks pass without running full
frontend typecheck; shared-file verification is serialized; dirty-baseline and
baseline-subtracted diff evidence exist; an independent reviewer approves the exact
closure and non-closure; atomic evidence validation and
`./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01` pass. Only then may
this task be reported PASS. The canonical CaseFees UI task remains responsible for the
later callsite migration and full frontend typecheck.
