# FPMS-V8-FUTURE-ANNUITY-AUTO-DRAFT-POLICY-20260712-01

Status: FROZEN / PRODUCT NOT STARTED
Risk: `PROTECTED`
Catalog ordinal: `213`
Outcome: generate one pending internal future-annuity draft only from an exact usable Scheme A
exception; preserve instruction-first as the default and preserve explicit `PAY` before payment.

## Authority and dependencies

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`,
  `DEC-V8-FULL-BATCH-SCHEME-A-20260810`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`, SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`
- `V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION`
- `V8-FUTURE-ANNUITY-GATE-MANIFEST-ACTIVATION-CURRENT-ADOPTION`
- `V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-CURRENT-ADOPTION`
- `V8-FUTURE-ANNUITY-EXCEPTION-AUTHORITY-SERVICE-CURRENT-ADOPTION`
- `V8-FUTURE-ANNUITY-OBLIGATION-CURRENT-ADOPTION`
- accepted fee-obligation draft and annuity-instruction services

The exact GLOBAL decision remains `APPROVED_POLICY`, source path as above and source version
`customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`. The default exception set is empty.
No missing, historical, expired, revoked, corrupt or ambiguous record is authority.

## Exact public seam

Add to `backend/app/modules/annuity/service.py`:

```python
@dataclass(frozen=True, slots=True)
class FutureAnnuityAutoDraftPolicyResult:
    annuity_task_id: int
    fee_obligation_id: str
    exception_attestation: FutureAnnuityExceptionUseAttestation
    draft: PrepareFeeObligationDraftResult

def apply_future_annuity_auto_draft_policy(
    *, transaction: Session, annuity_task_id: int, actor_id: str, as_of: datetime
) -> FutureAnnuityAutoDraftPolicyResult: ...
```

Require a positive exact non-boolean task ID, exact Session, nonblank untrimmed/NUL-free actor ID
of at most 36 characters and UTC-naive exact datetime. Invalid input uses the accepted future-
annuity invalid-command error before connection or query. Dirty caller state uses its accepted 409.

The function names the exact task; it never selects the latest task. Validate the task's complete
six-field carrier and accepted future-annuity recognition graph: same case/client, exact
`FUTURE_ANNUITY` CNY obligation, one current matched line, task/year/due/fee code, source activity,
document, approved current evidence/hash and canonical recognition activity. Require obligation
states `RECOGNIZED`, `VERIFIED`, `PENDING`, `NOT_CREATED`, `UNPAID`, with official evidence
`PENDING`. Missing nodes preserve accepted 404; incoherent or partial graphs preserve accepted 409.

Resolve the exact exception with the persisted case relationship and caller time:

```python
ResolveFutureAnnuityExceptionCommand(
    client_id=case.client_id,
    case_id=case.id,
    as_of=as_of,
)
```

Propagate the accepted authority service's exact 404/409 failures. Derive the draft key exactly as
`future-annuity-exception-auto-draft:{annuity_task_id}:{publication_id}`. No caller key, fallback,
clock, environment authority or inferred exception is accepted.

## Deep draft authority and lineage

Add exact `FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION`. Extend
`PrepareFeeObligationDraftCommand` after `authority` with defaults:

```python
exception_gate_id: str | None = None
exception_gate_source_reference: str | None = None
exception_gate_source_version: str | None = None
exception_publication_id: str | None = None
exception_publication_snapshot_hash: str | None = None
exception_attested_at: datetime | None = None
```

All six are required only for the new authority and forbidden for every existing authority, so
existing payload bytes remain unchanged. The adapter supplies the exact resolved gate ID/source/
version, publication ID/snapshot hash and `as_of`. The enum is never authority by itself.

The deep service independently validates the immutable canonical publication row and its exact
client/case applicability at `exception_attested_at`, including source, scope, interval, actor,
snapshot bytes/hash and relationship. It must not depend only on the adapter result. Fresh creation
requires the complete recognized annuity graph and must fail closed for a fake publication, hash,
time, relation, task or obligation.

Use activity schema `FPMS_FEE_DRAFT_CREATED_FROM_FUTURE_ANNUITY_EXCEPTION_V1`. Its payload has
exactly existing keys `actor_id`, `authority`, `center_changes`, `draft_id`, `links`,
`obligation_id`, `schema`, plus `exception_publication_id`,
`exception_publication_snapshot_hash`, `exception_attested_at`, `exception_gate_id`,
`exception_gate_source_reference`, `exception_gate_source_version`. `center_changes` is `{}`; the
timestamp is microsecond UTC-naive ISO text; evidence refs are empty; source activity is the exact
canonical `FEE_OBLIGATION_RECOGNIZED` activity. Creation leaves instruction `PENDING`, creates no
PayList, GovPayment, payment or receipt, and uses one caller-owned nested savepoint.

## Replay and later instruction

Exact existing draft-activity replay is validated before any fresh-current gate or exception
lookup. Replay binds actor, task, obligation, key, stored gate ID/source/version, publication
ID/hash/attested time, canonical gate/publication bytes, links and activity; it creates nothing.
Those persisted facts plus the exact case/client graph reconstruct the full original
`FutureAnnuityExceptionUseAttestation`; current authority is never substituted. Later gate change,
expiry or revocation does not rewrite or invalidate a previously valid draft. Changed input or
corrupt history is 409.

Extend the stored reviewed-authority instruction branch to recognize the new schema and revalidate
its exact exception lineage. A later explicit `PAY` through accepted
`record_annuity_task_instruction` / `record_client_instruction` updates only instruction state and
the existing instruction activity chain; it reuses the same draft/items/links and creates no second
draft activity. `HOLD` and `ABANDON` after an exception draft fail closed. Payment remains forbidden
until stored instruction is exact `PAY`.

## Non-goals

No API/UI, model/migration, decision gate, permission, exception publication, rate, reduction,
amount, deadline, lifecycle/legal state, PayList, payment, workbook or service-rate behavior. Do
not change other draft-authority payloads or re-run future-annuity recognition.

## Paths and verification

Implementation allowlist:

- this task file;
- `backend/app/modules/annuity/service.py`;
- `backend/app/modules/fees/obligation_contracts.py`;
- `backend/app/modules/fees/obligation_service.py`;
- `backend/tests/test_v8_future_annuity_auto_draft_policy.py`;
- `backend/tests/test_v8_fee_obligation_contracts.py`.

All authority-service, carrier/model/migration, API, gate, rate, reduction, PayList, payment,
manifest and ledger paths are read-only during implementation. SQLite-writing checks are serial.

Verification:

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_auto_draft_policy.py tests/test_v8_fee_obligation_contracts.py`
- affected regressions: `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_exception_authority_service.py tests/test_v8_future_annuity_obligation.py tests/test_v8_fee_obligation_prepare_draft.py tests/test_v8_annuity_instruction_obligation_adapter.py tests/test_v8_application_auto_draft_policy.py tests/test_v8_grant_year_auto_draft_policy.py`
- scoped Ruff: `cd backend && .venv/bin/ruff check app/modules/annuity/service.py app/modules/fees/obligation_contracts.py app/modules/fees/obligation_service.py tests/test_v8_future_annuity_auto_draft_policy.py tests/test_v8_fee_obligation_contracts.py`
- exact allowlist diff and `git diff --check`.

Focused tests prove exact DTO/signature, CLIENT/CASE success, exact payload/replay, absent/expired/
revoked/ambiguous/wrong gate, malformed/dirty call order, incomplete/cross-case/corrupt lineage,
deep enum-only rejection, fault rollback, pre-PAY payment rejection, later PAY without a second
draft, HOLD/ABANDON rejection and historical replay after revocation.

Acceptance requires the exact implementation commit/range, focused and affected checks, scoped
lint/diff, one independent High zero-finding review, integration and controller adoption as
`V8-FUTURE-ANNUITY-AUTO-DRAFT-POLICY-CURRENT-ADOPTION`. A byte-changing rewrite invalidates review.
