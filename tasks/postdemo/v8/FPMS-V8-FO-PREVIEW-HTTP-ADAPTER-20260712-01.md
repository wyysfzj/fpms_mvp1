# FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `105`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `533`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-API`

- RED expectation: Exact API test fails on the missing strict V8 request, direct
  `FeeEstimate` projection, production-provider injection, error mapping or no-write
  guarantee.
- GREEN expectation: Exact API test passes the frozen 200/400/401/403/404/409/422 matrix,
  exact response serialization and no-write assertions on every path.

## Exact Closure Slice

The existing official-fee preview POST adapts one strict, explicit-date HTTP request to
the frozen read-only `preview_estimate()` service and returns its exact `FeeEstimate`
projection without recognizing or writing anything.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract for this one HTTP adapter. It
preserves the existing route and consumes the already frozen preview service plus the
separately implemented production rate provider. It does not own a fee rule, provider
selection rule, persistence behavior or compatibility path.

### Exact route, permission and handler boundary

Preserve exactly `POST /api/v1/fees/official-fee-preview` in
`backend/app/modules/fees/api.py`. The module router is already wired; this task must not
edit `backend/app/api/router.py` or add another `include_router(...)`.

The handler keeps permission enforcement as a function parameter, never as decorator
metadata:

```python
def preview_official_fee_candidates(
    payload: OfficialFeePreviewIn,
    _perm: None = Depends(require_perm("Fee.Read")),
    db: Session = Depends(get_db),
) -> OfficialFeePreviewOut:
    ...
```

- The route has one success status only: HTTP 200. It is not a create route and must not
  return 201 or 204.
- The response is the direct `OfficialFeePreviewOut` body defined below. It is not wrapped
  in `data`, `result`, `preview`, `items` or another response envelope.
- Existing authentication behavior supplies 401 for no valid authentication and 403 for
  an authenticated caller without exact `Fee.Read`.
- No actor, idempotency key, current-user value, request clock or transaction write is
  needed by this read-only handler.

### Strict request schema and explicit date

`backend/app/modules/fees/schemas.py` replaces the legacy input shape with exactly these
request models. Both models use `ConfigDict(extra="forbid")`; every shown field has no
default and is therefore required, including the nullable `source_document_id` and the
literal `currency`.

```python
class OfficialFeePreviewTriggerContextIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trigger: str
    source_document_id: str | None


class OfficialFeePreviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    trigger_context: OfficialFeePreviewTriggerContextIn
    currency: Literal["CNY"]
    rate_effective_on: date
```

The HTTP representation of `rate_effective_on` is one ISO calendar date
`YYYY-MM-DD`. A datetime/timestamp, null, missing field or other type is 422. The handler
passes the parsed exact `date` unchanged. It must never call `date.today()`,
`datetime.now()`, a clock dependency, or derive this date from the case, source document,
rate row or database.

The only accepted JSON keys are the keys shown above at their exact nesting levels.
Specifically, the legacy top-level `trigger_event` and top-level `source_document_id`
shape is 422; it is not copied, aliased, deprecated-with-success or silently translated.
Missing nested `source_document_id` is also 422 even though an explicit JSON null is
valid. Pydantic shape/type/literal failures remain 422 and do not enter the handler.

After Pydantic validation, the adapter creates exactly one
`PreviewFeeEstimateCommand`:

```python
PreviewFeeEstimateCommand(
    case_id=payload.case_id,
    trigger_context=FeeEstimateContext(
        trigger=payload.trigger_context.trigger,
        source_document_id=payload.trigger_context.source_document_id,
    ),
    currency=payload.currency,
)
```

It performs no trimming, case-folding, defaulting or normalization; the frozen service
owns exact command validation.

### Case gate, production provider and sole service call

After authentication/request validation and before provider construction or service
invocation, query only for the exact `Case.id == payload.case_id`. Absence raises HTTP 404
with code `CASE_NOT_FOUND`, and neither the provider nor preview service is called.

For an existing case, construct exactly
`SqlAlchemyOfficialFeeEstimateRateProvider(db)` and call exactly once:

```python
preview_estimate(
    command=command,
    rate_effective_on=payload.rate_effective_on,
    rate_provider=SqlAlchemyOfficialFeeEstimateRateProvider(db),
)
```

The adapter must not import, call or wrap legacy
`preview_official_fee_candidates()` from `fees.service`; directly select an unlinked
`FeeRate`; fall back from the production provider to a legacy `FeeRate`, seed, customer
workbook or hard-coded amount; or retry an empty/unapproved/ambiguous provider result.
The production provider prerequisite owns all SQLAlchemy rate/source selection and this
adapter must not duplicate any trigger, rate, reduction, amount or candidate business
rule.

The case existence SELECT and provider SELECTs are the only database access allowed. The
handler performs no `add`, `delete`, `flush`, `commit`, `rollback`, write SQL, model
mutation or transaction ownership change.

### Exact direct `FeeEstimate` response projection

`OfficialFeePreviewOut` and its nested response models project every field of the frozen
`FeeEstimate`, `FeeEstimateCandidate`, `FeeObligationLineInput`, `FeeEstimateSource` and
`FeeEstimateContext` shapes, and no other field. The JSON body has exactly this structure
and key vocabulary:

```json
{
  "case_id": "CASE-ID",
  "estimate_status": "ESTIMATE",
  "trigger_context": {
    "trigger": "TRIGGER",
    "source_document_id": null
  },
  "currency": "CNY",
  "candidates": [
    {
      "line": {
        "fee_code": "FEE-CODE",
        "fee_name": "FEE-NAME",
        "fee_year_key": 0,
        "official_full_amount": "900.00",
        "reduction_ratio": "0.8500",
        "payable_amount": "135.00",
        "source_amount": null,
        "source_date": "2026-07-13",
        "difference_review_state": "SOURCE_PENDING"
      },
      "source": {
        "rate_id": "RATE-ID",
        "source_document_id": null,
        "source_doc": "SOURCE-DOC",
        "source_url": "SOURCE-URL",
        "source_policy": "SOURCE-POLICY",
        "source_version": "SOURCE-VERSION",
        "status": "VERIFIED"
      }
    }
  ],
  "total_payable_amount": "135.00"
}
```

- `estimate_status` is exactly `ESTIMATE`; `currency` is exactly `CNY`; the context is
  echoed from the frozen result.
- Money fields serialize as fixed two-decimal strings. This includes
  `official_full_amount`, `payable_amount`, non-null `source_amount` and
  `total_payable_amount`; null remains JSON null.
- `reduction_ratio` serializes as a fixed four-decimal string. It is never a JSON number,
  float-derived value or shortened decimal string.
- Every non-null date serializes as an ISO `YYYY-MM-DD` string. The service result's
  `source_date` is preserved; the adapter does not invent a due date.
- Candidate array order is exactly the tuple/provider order. The adapter must not sort,
  group, index by fee code, deduplicate or otherwise reorder it.
- Enum values serialize by their frozen string values. The adapter does not recompute
  totals, payable amounts, reduction ratios, source facts or difference state.
- There is no `obligation_id`, draft ID, activity ID, PayList/export ID, payment ID,
  idempotency key, generated preview ID, `draft_type`, `preview_only`, `trigger_event`,
  `total_gov`, `quantity`, `unit_price`, deadline or obligation status field. The
  `case_id`, source-document ID and provider `rate_id` already present in `FeeEstimate`
  remain part of the exact projection.

### Exact HTTP error mapping

Preserve the repository `BusinessError` envelope and the original frozen error code and
defensive-copy `details`; do not collapse errors into one generic preview code:

| HTTP status | Exact source |
| --- | --- |
| `200` | one successfully projected `FeeEstimate` |
| `400` | only `FEE_ESTIMATE_INVALID_COMMAND` or `FEE_ESTIMATE_TRIGGER_UNSUPPORTED` |
| `401` | unauthenticated request |
| `403` | authenticated caller lacks `Fee.Read` |
| `404` | case lookup fails, code `CASE_NOT_FOUND` |
| `409` | `FEE_ESTIMATE_RATE_MISSING`, `FEE_ESTIMATE_RATE_SOURCE_UNAPPROVED`, `FEE_ESTIMATE_RATE_SOURCE_AMBIGUOUS`, `FEE_ESTIMATE_RATE_SOURCE_INVALID`, `FEE_ESTIMATE_CANDIDATE_INVALID`, or any frozen `FeeReductionValidationError.code.value` |
| `422` | Pydantic request shape, required-field, extra-field, literal or type failure |

`FeeEstimatePreviewError` details pass through unchanged. `FeeReductionValidationError`
details and its exact `FeeReductionErrorCode.value` pass through unchanged at 409. The
adapter adds no catch-all conversion. Provider missing/unapproved/ambiguous/invalid
source must fail closed at 409; none may trigger a legacy fallback.

### Frozen RED / GREEN and no-write matrix

`backend/tests/test_v8_fee_estimate_preview_api.py` must prove at least:

1. the existing POST path, direct response, exact function-parameter `Fee.Read`
   dependency and absence of router rewiring;
2. exact strict request models, all four required top-level fields, required-nullable
   nested `source_document_id`, `currency="CNY"`, exact ISO date, nested/top-level extra
   rejection, and legacy `trigger_event` shape returning 422 with no compatibility call;
3. case absence returns 404 before provider/service construction; success constructs
   `SqlAlchemyOfficialFeeEstimateRateProvider` with the request `db` and calls
   `preview_estimate()` once with the exact command and explicit date;
4. a deliberately exploding legacy service/unlinked-`FeeRate` fallback remains untouched
   on success and every error branch;
5. the exact direct keys and nested keys, `ESTIMATE`, CNY, fixed two-place money strings,
   fixed four-place ratio strings, ISO dates, nullable fields and provider candidate order;
6. absence of every prohibited obligation/draft/activity/PayList/payment/idempotency or
   legacy-preview field in the response;
7. exact 200, 400, 401, 403, 404, 409 and 422 status/error-code mapping, including every
   preview error code and representative frozen fee-reduction errors with unchanged
   details;
8. before/after counts and transaction/write spies prove success and every individual
   400/401/403/404/409/422 path creates no fee obligation/header/line, fee draft/item,
   lifecycle or fee activity, PayList/export artifact, payment or payment-evidence link,
   and performs no flush/commit/rollback;
9. the pure preview-service and production-provider inherited targeted regressions remain
   green without changing their contracts.

## Explicit Non-Closure

No second endpoint, router rewiring, provider/rate/reduction/amount business-rule
duplication, obligation/draft/activity/PayList/payment write, legacy compatibility or
frontend work. Do not absorb the post-HTTP legacy-test migration, another V8 catalog row,
a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`

### External, gate and inherited prerequisites

- `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` — the read-only production
  provider must be PASS before this adapter's GREEN implementation.

- Approved source dependency cell (verbatim): preview service

### Shared ownership serialization

- `backend/app/modules/fees/api.py` order key `3`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/schemas.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01` — serialize after this
  HTTP adapter and complete it before Foundation close; this task must not modify the
  legacy test file.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md`
- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/fees/api.py`
- `backend/tests/test_v8_fee_estimate_preview_api.py`
- `artifacts/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md function-parameter permission injection, direct-response convention,
  FastAPI status/body and SQLite rules applicable to this closure.
- This adapter is read-only: it does not own a business transaction, commit, flush,
  rollback, persistence side effect or implicit clock.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_estimate_preview_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_estimate_preview_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_fee_estimate_preview_api.py && .venv/bin/ruff format app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_fee_estimate_preview_api.py && .venv/bin/ruff check app/modules/fees/schemas.py app/modules/fees/api.py tests/test_v8_fee_estimate_preview_api.py`
- `git diff --check -- backend/app/modules/fees/schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_estimate_preview_api.py tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
