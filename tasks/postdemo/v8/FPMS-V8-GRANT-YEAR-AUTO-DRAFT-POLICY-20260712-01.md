# FPMS-V8-GRANT-YEAR-AUTO-DRAFT-POLICY-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR RED
Risk class: `PROTECTED`
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Catalog ordinal: `212`
Executor role: Backend Developer / worker

## Authority and prerequisites

- Accepted Scheme A SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Runtime gate: `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL`.
- Required predecessors:
  - `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`;
  - `FPMS-V8-GRANT-YEAR-DRAFT-MANIFEST-ACTIVATION-20260712-01`;
  - accepted current grant-notice lifecycle, grant-year annuity-obligation and
    prepare-grant-draft behavior.

Scheme A authorizes product development for this policy but does not install runtime authority.
The exact GLOBAL gate must still be persisted, current, confirmed and source-backed at runtime.
A missing, revoked, future, stale, conflicting, corrupt or scope-mismatched gate fails closed with
409 and no policy write.

## Exact closure and interface

Add exactly this result and entry point to `backend/app/modules/grant_fees/service.py`:

```python
@dataclass(frozen=True, slots=True)
class GrantYearAutoDraftPolicyResult:
    recognition: RecognizeFeeObligationResult
    draft: PrepareGrantFeeTaskDraftResult


def apply_grant_year_auto_draft_policy(
    *,
    transaction: Session,
    grant_fee_task_id: str,
    source_activity_id: str,
    actor_id: str,
    as_of: datetime,
) -> GrantYearAutoDraftPolicyResult: ...
```

The entry point accepts only nonblank canonical identifiers, an exact SQLAlchemy `Session`, and
a UTC-naive `as_of`. It rejects a caller session with pending new, dirty or deleted state before
opening a connection, resolving the gate or calling a writer.

After resolving exactly `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL` at caller `as_of`, it delegates to the
accepted `recognize_grant_year_annuity_obligation` contract and the generic `prepare_draft` deep
module in one caller-owned transaction. The source activity must be the accepted, verified real
grant-registration notice already bound to the task. Its reviewed notice bytes remain the sole
source of grant year, official amount, reduction and deadline truth.

The accepted public `prepare_grant_fee_task_draft` adapter remains the post-`PAY` path and must not
be weakened or silently repurposed. Add only the minimum private grant-year bridge needed by this
policy. Add `FeeDraftAuthority.REVIEWED_GRANT_YEAR_NOTICE` and make the generic deep module accept
that authority only after independently validating the exact stored grant-year graph: one current
`GRANT_YEAR_ANNUITY` obligation, its canonical recognition, the bound verified grant-registration
notice/evidence, and exactly one canonical `GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED` activity whose
task, obligation, notice, evidence hash, lines and confirmed values all match current persisted
state. A caller-supplied enum is never authority by itself.

The new draft activity uses the distinct canonical schema
`FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_GRANT_YEAR_NOTICE_V1`, records authority
`REVIEWED_GRANT_YEAR_NOTICE`, and points to the obligation-recognition activity. Existing client
instruction and reviewed-application schemas, validation and replay remain byte-compatible. A
later explicit `PAY` instruction may consume this exact reviewed-grant draft without rebuilding
it; any other or ambiguous reviewed-draft graph fails closed.

The policy creates or reuses exactly one internal draft for the recognized obligation. The
obligation remains `client_instruction_status=PENDING` and `payment_status=UNPAID`; the draft is
not a payment instruction, pay list, government payment or legal-state change. Actual payment
requires a later explicit customer `PAY` instruction through the existing instruction contract.

## Atomicity, replay and failures

- Resolve the gate before either business writer.
- Establish SQLite's outer transaction when necessary, then run recognition and draft preparation
  inside one nested savepoint.
- Derive stable policy idempotency keys only from the accepted grant task/source activity; an exact
  replay reuses the same obligation, draft, links and activity without duplicates.
- Any post-recognition failure rolls back the whole policy savepoint. Never commit, roll back or
  close the caller session.
- Malformed input is 400 before query/write. Missing linked business state is 404. Unusable gate,
  corrupt notice/obligation/draft lineage, conflict or changed replay is 409 with no partial write.

## Explicit non-closure

No schema/migration, endpoint/UI, gate publication, default/seed, customer instruction, pay list,
government payment, fee-rate invention, notice mutation, lifecycle/legal-state change, second
entry point or adjacent refactor. Do not edit the catalog, coverage ledger or adoption record.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-AUTO-DRAFT-POLICY-20260712-01.md`
- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/fees/obligation_contracts.py`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_grant_year_auto_draft_policy.py`

No artifact or other file is authorized. Preserve untracked `backend/uv.lock`; do not stage, edit
or absorb it. Shared `backend/app/modules/grant_fees/service.py` ownership and all SQLite-writing
verification remain serialized behind ordinal 211.

## Focused acceptance

1. A canonical reviewed real grant notice plus the exact current GLOBAL gate creates one pending,
   unpaid internal grant-year draft and exact replay creates nothing else.
2. Missing/revoked/future/stale/wrong-source/wrong-version/corrupt/fallback-scope gate authority is
   409 before recognition or draft writes.
3. Dirty caller state and malformed input precede connection/gate/writer calls; injected failure
   after recognition leaves no residue after caller rollback.
4. The reviewed notice remains authoritative for grant year, amount, reduction and deadline; no
   caller-supplied or default fee facts are accepted.
5. Creating the draft does not create a pay list or government payment. Payment is rejected until
   a later explicit customer `PAY` instruction, after which existing payment behavior may proceed
   without rebuilding the draft graph.
6. The service never commits, rolls back or closes the caller session; caller rollback removes the
   whole new policy result.
7. The ordinary post-`PAY` grant adapter and reviewed-application auto-draft/replay/instruction
   paths retain their accepted behavior and schemas.

## Verification and review boundary

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_year_auto_draft_policy.py`
- Affected regressions: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_draft_obligation_adapter.py tests/test_v8_application_auto_draft_policy.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py app/modules/fees/obligation_contracts.py app/modules/fees/obligation_service.py tests/test_v8_grant_year_auto_draft_policy.py && .venv/bin/ruff format app/modules/grant_fees/service.py app/modules/fees/obligation_contracts.py app/modules/fees/obligation_service.py tests/test_v8_grant_year_auto_draft_policy.py && .venv/bin/ruff check app/modules/grant_fees/service.py app/modules/fees/obligation_contracts.py app/modules/fees/obligation_service.py tests/test_v8_grant_year_auto_draft_policy.py`
- Scope: `git diff --check -- tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-AUTO-DRAFT-POLICY-20260712-01.md backend/app/modules/grant_fees/service.py backend/app/modules/fees/obligation_contracts.py backend/app/modules/fees/obligation_service.py backend/tests/test_v8_grant_year_auto_draft_policy.py`

Do not run pytest or touch product code until the controller releases the serialized SQLite lane
after ordinal 211. No repo-wide, broad Playwright, milestone or release checks belong here. An
independent High reviewer must approve the exact implementation commit/range with
`P0/P1/P2 = 0/0/0`; the implementer does not self-approve.
