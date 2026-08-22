# FPMS-DEMO-ABC-TRUST-BOUNDARY-HARDENING-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["customer-decision", "demo", "fee", "lineage", "source-authority"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-TRUST-BOUNDARY-HARDENING-20260817-01.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer scope decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Controlling design: `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`.
- Independent findings: `P1-1`, `P1-2`, `P2-1`, plus the reviewed bundle-root separation risk.
- V8 catalog IDs: `None` — this is a non-release local demo recovery story and cannot close or
  activate a V8 catalog row.
- Dependency: exact candidate `eb8273b003d591da477a186c0d2d14595b7d5e28` and the persisted
  independent High report; no shared-file owner is active.

## Exact Closure Slice

Make the local ABC runtime bundle structurally distinguish `SYNTHETIC_TEST_ONLY` from
`CUSTOMER_AUTHORIZED`; cross-bind that class in the manifest, authority record, immutable snapshot
and run metadata; permit the synthetic class only for technical rehearsal and make it ineligible for
customer activation or `DEMO_READY`. Require the exact visible bilingual fictional marker in the
DOCX body and every first PDF page, reject hidden/deleted-only Word markers, make exact JSON value
checks type-sensitive, and reject bundle roots inside repository, run or product-storage roots.

## Explicit Non-Closure

No actual customer bundle is supplied or activated; no customer template, fee, legal or official
authority is invented. No billing, payment, offset, production, remote hosting, security or release
behavior changes.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-COMMAND-RESULT-HARDENING-20260817-01`
- `FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-02`

## Allowed Files

- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`
- `backend/app/core/demo_bundle.py`
- `backend/app/modules/fees/demo_service.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/scripts/validate_demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `tasks/postdemo/FPMS-DEMO-ABC-TRUST-BOUNDARY-HARDENING-20260817-01.md`
- `artifacts/FPMS-DEMO-ABC-TRUST-BOUNDARY-HARDENING-20260817-01/**`

## Verification Commands

1. Focused RED proves synthetic/customer classes were previously indistinguishable, English-only or
   hidden/deleted markers passed, and Boolean OA sequence passed.
2. Focused GREEN proves exact class propagation/eligibility, bilingual visible markers, strict types,
   forbidden-root rejection and unchanged runtime service behavior.
3. Scoped Ruff and exact allowlist checks pass.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-TRUST-BOUNDARY-HARDENING-20260817-01/`

## Rollback

Revert the one atomic commit. No shared database migration or customer input is involved.

## Done definition

Synthetic technical input cannot represent itself as customer-authorized, invisible or English-only
markers cannot pass, strict manifest types cannot coerce, forbidden roots fail before run creation,
and the focused tests pass on the exact candidate. Independent High acceptance remains required.
