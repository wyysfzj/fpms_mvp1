# FPMS V8 Full-Suite OA Commission Fee-Reduction Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Preserve the inherited OA commission scenario's exact canonical `0.85` fee reduction while
supplying the current reviewed applicant-scoped approval prerequisite before Case creation. The
existing OA fee draft, bill, commission rule, agent split, amount and settlement assertions remain
unchanged.

## Exact RED and closure

The inherited OA commission test currently reaches `409 FEE_REDUCTION_APPROVAL_REQUIRED` because
it creates an exact one-applicant `0.85` Case without the required confirmed current approval.

This task may only seed the existing authoritative approval record for that exact applicant set
before calling the existing Case helper. It must retain `fee_reduction: "0.85"` and all original
commission behavior assertions.

## Non-closure

- No product, fee-reduction authority, commission, billing, schema, migration, seed or shared
  fixture change.
- No conversion to zero reduction, direct Case insert, monkeypatch, skip, xfail, assertion deletion
  or relaxed error.
- No claim over annuity draft lineage, legacy fee-obligation links or Row283 close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-OA-COMMISSION-FEE-REDUCTION-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_b_oa_commission_readiness.py`

## Verification and acceptance

Run the inherited OA commission test together with the authoritative fee-reduction create tests,
scoped Ruff, format-check and exact diff-check. All tests must pass. Independent High review must
approve P0/P1/P2 `0/0/0` before continuing.

## Current verification result

The exact inherited test plus authoritative fee-reduction create suite completed `28 passed` and
`19 subtests passed` in `11.60s`, with four pre-existing dependency/Pydantic warnings. The RED was
the exact inherited test failing at `409 FEE_REDUCTION_APPROVAL_REQUIRED`; the final bytes preserve
the original `0.85` scenario and all commission assertions.
