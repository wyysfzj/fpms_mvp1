# FPMS V8 Full CONFIG_REQUIRED Successor

Status: `IMPLEMENTATION`
Risk: `PROTECTED`
Runbook: `P0-prereq-heavy-story`

## Observable outcome

Freeze the narrow latest-wins authority needed for catalog Row199 development closure:
the already reviewed payment-workbook and service-price capabilities satisfy their Full
development prerequisites as `CAPABILITY_READY + CONFIG_REQUIRED`. Their real production
inputs remain absent/PENDING, every production action remains `409 / NO WRITE`, TEST_ONLY
remains isolated, and no production activation may be claimed.

The other five GLOBAL gate families and all 22 exact legacy-form scopes remain governed by
their existing current catalog-row stories and source-decision authority. This successor does
not weaken, replace or synthesize any of those decisions.

## Preconditions

- Capability-close commit `a8219b7a39047b819100cc69dd4cffadfc3e170c` is independently
  approved.
- Capability-ledger adoption `03138fbd5b1089634b84d353bf2abffd70777e41` is current.
- Catalog rows 170–198 resolve to current stories; rows 175 and 176 resolve specifically to
  `V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION`.
- The customer-adopted input-decoupling authority explicitly permits Full, Final and Release
  to accept this split only with proved negative production behavior and TEST_ONLY isolation.

## Exact closure

1. Materialize one successor contract for Row199's development-versus-production interpretation.
2. Prove the frozen Row199 identity and its 29 exact requested gate identities remain unchanged.
3. Prove catalog gate rows 170–198 are current, including all exact form scopes.
4. Prove only payment workbook and service rate use the capability/configuration split and bind
   their accepted story metadata, decision-registry PENDING status and negative-path evidence.
5. Preserve an explicit next-step boundary: Row199 remains unadopted until its own Full
   capability-manifest close story passes independent High review.

## Non-closure

- Do not change the frozen catalog, source-decision registry, coverage ledger or Row199 task.
- Do not configure real workbook, upload proof, service-rate version, grant source or role binding.
- Do not change product source, tests outside this contract, schemas, migrations, API or UI.
- Do not close Row199, Row281, Row282, Row283, Full, Final or Release.
- Do not use historical taskctl/evidence machinery or the old manifest gate to claim current close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-CONFIG-REQUIRED-SUCCESSOR-20260813-01.md`
- `docs/product/v8/stories/V8-FULL-CONFIG-REQUIRED-SUCCESSOR.md`
- `scripts/tests/test_v8_full_config_required_successor.py`
- `docs/product/v8/reviews/V8-FULL-CONFIG-REQUIRED-SUCCESSOR.md`

`backend/uv.lock` remains unrelated and untouched.

## Verification and acceptance

```text
python3 -m pytest -q scripts/tests/test_v8_full_config_required_successor.py
python3 -m ruff check scripts/tests/test_v8_full_config_required_successor.py
git diff --check -- <exact allowlist>
```

The implementation candidate requires an independent High review with P0/P1/P2 `0/0/0`.
The reviewer, not the implementer, materializes the exact review receipt. Rollback removes only
this authority successor; production configuration and data are never changed.
