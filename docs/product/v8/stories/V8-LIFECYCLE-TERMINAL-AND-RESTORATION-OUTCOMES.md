# Story V8-LIFECYCLE-TERMINAL-AND-RESTORATION-OUTCOMES

- Risk: `PROTECTED`
- Base: `e74dafb37f64702443c81fa49a0f866c7c95e726`
- Outcome: implement and prove the seven authority-backed application/patent terminal and
  restoration lifecycle transitions in frozen catalog order.
- Authority: `docs/product/v8/domain-contract.md`; the lifecycle event matrix in
  `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`;
  frozen catalog rows 35–41; and the current reviewed lifecycle rule/apply-event seam.

## Catalog IDs

1. `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01` (ordinal 35)
2. `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01` (ordinal 36)
3. `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01` (ordinal 37)
4. `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01` (ordinal 38)
5. `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01` (ordinal 39)
6. `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01` (ordinal 40)
7. `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01` (ordinal 41)

The rows are one serialized story because they share the only lifecycle rule registry and
form one closed terminal/restoration matrix. Each event retains its own public rule test,
observable transition and catalog identity.

## Observable transitions and evidence

| Event | Exact predecessor | Required evidence | Result |
| --- | --- | --- | --- |
| `APPLICATION_WITHDRAWAL_CONFIRMED` | confirmed pending application in one coherent ungranted procedure stage | withdrawal request plus distinct official confirmation | closed / procedure closed / application withdrawn |
| `APPLICATION_ABANDONMENT_CONFIRMED` | confirmed pending application in one coherent ungranted procedure stage | effective deemed-abandonment notice or right-abandonment confirmation | closed / procedure closed / application abandoned |
| `PATENT_TERMINATION_CONFIRMED` | post-grant / grant announced / patent in force | termination notice or controlled register evidence | closed / procedure closed / patent terminated |
| `PATENT_EXPIRY_CONFIRMED` | post-grant / grant announced / patent in force | expiry confirmation or controlled register evidence | closed / procedure closed / patent expired |
| `PATENT_INVALIDATION_CONFIRMED` | post-grant / grant announced / patent in force | effective invalidation decision plus distinct controlled register evidence | closed / procedure closed / patent invalidated |
| `APPLICATION_RIGHT_RESTORATION_CONFIRMED` | closed / procedure closed / application abandoned | official restoration decision plus one explicit restored official procedure stage | pending application at the exact coherent business/procedure pair derived from that stage |
| `PATENT_RIGHT_RESTORATION_CONFIRMED` | closed / procedure closed / patent terminated | official restoration decision plus distinct controlled register evidence | post-grant / grant announced / patent in force |

The application-restoration payload contains exactly
`restored_official_procedure_stage`. The rule accepts only the nine already-authorized
coherent pending-application stages and deterministically derives their business stage.
It has no default and cannot restore to a closed, unfiled or patent stage.

All commands require exact typed lifecycle/confirmed facts, canonical same-case document
evidence identities and hashes, naïve datetimes, no correction/supersession carrier and
the event-specific payload boundary. The pure rules never access the transaction.

## Exact paths

- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/tests/test_v8_lifecycle_application_withdrawal.py`
- `backend/tests/test_v8_lifecycle_application_abandonment.py`
- `backend/tests/test_v8_lifecycle_patent_termination.py`
- `backend/tests/test_v8_lifecycle_patent_expiry.py`
- `backend/tests/test_v8_lifecycle_patent_invalidation.py`
- `backend/tests/test_v8_lifecycle_application_restoration.py`
- `backend/tests/test_v8_lifecycle_patent_restoration.py`

## TDD and verification

Each row began with one public behavior test that failed only because its exact registry
entry/rule was absent. Each then received the minimum rule and passed before the next row
started. Boundary tests cover every authorized application restoration stage, all
terminal projections, evidence cardinality/order/identity/kind/hash, command type/lane,
confirmation, payload and exact predecessor failures.

The seven focused files pass `108` tests. The one complete story GREEN adds the current
application-rejection, patent-register/conflict-service, apply-event and lifecycle
projection regressions and passes `294` tests. The only warning is the inherited
third-party `passlib` `crypt` deprecation. Scoped Ruff passes and all seven new tests are
Ruff-formatted.

## Non-goals and rollback

No API/evidence adapter, UI, fee/obligation/payment behavior, deadline, schema/migration,
source activation, customer decision, generic lifecycle endpoint, adjacent refactor or
row 42+ behavior is included. These rules do not infer an event from
`PATENT_REGISTER_STATUS_CONFIRMED`; that event continues to record only the reviewed typed
conflict.

Rollback reverts the seven rule/registry slices, their seven exact tests and this story
card while retaining all rows 1–34.
