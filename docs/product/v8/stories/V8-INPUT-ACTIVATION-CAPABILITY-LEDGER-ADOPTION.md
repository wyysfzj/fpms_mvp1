# V8 Input Activation Capability Ledger Adoption

Status: `IMPLEMENTATION — INDEPENDENT PROTECTED REVIEW REQUIRED`

## Authority boundary

The customer-approved input-decoupling decision makes the payment-workbook and service-price
implementation lanes development capabilities whose missing production inputs fail closed at
runtime. This story adopts implementation evidence only. It does not assert that either real
input is present, reviewed or active.

The exact adopted rows are 175, 176, 214–229 and 278. Their shared story must expose:

```json
{
  "capability_status": "CAPABILITY_READY",
  "production_inputs": {
    "DG-PAYMENT-WORKBOOK:GLOBAL": "CONFIG_REQUIRED",
    "DG-SERVICE-RATE-VERSION:GLOBAL": "CONFIG_REQUIRED"
  },
  "production_failure": "409 / NO WRITE",
  "production_activation_claimed": false
}
```

`CURRENT_VERIFIED` therefore means the reviewed capability bytes and tests are current. It
does not mean a production decision gate is positive. Row199 and terminal rows remain outside
this story and require their own successor contracts.

## Git-native compatibility correction

The Full-terminal dependency overlay pins immutable catalog identity, exact additive edges,
base/effective dependency hashes, Row283's predecessor sentinel, order and deferred coverage.
It must not pin mutable task-card bytes that legitimately receive reviewed latest-wins
appendices; current task/product bytes are instead bound by reachable story commits and exact
tree fingerprints.

The integrated-owner check excludes only `docs/product/v8/coverage-ledger.json`. Historical
stories that listed the ledger still validate their recorded candidate fingerprint, while the
current ledger remains subject to its schema, catalog digest, exact row set, story references,
reachable commits and story fingerprints. All non-ledger owned paths retain latest accepted
owner drift protection.

## Exact closure and non-closure

The exact closure, allowlist, verification and rollback boundary are frozen by
`tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-LEDGER-ADOPTION-20260813-01.md`.
No product source, runtime configuration, source registry, catalog, Row199, Full, Final or
Release claim belongs to this story.
