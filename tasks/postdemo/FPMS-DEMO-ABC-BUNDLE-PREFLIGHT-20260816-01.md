# FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "runtime-input", "source-authority", "template", "fee"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01.md

## Story shape

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: none
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Design references

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md` section 6
- `docs/superpowers/plans/2026-08-16-fpms-local-demo-abc-fast-track.md`

## Exact Closure Slice

Add a standalone, read-only local-demo bundle preflight that accepts only the frozen manifest v1,
validates the externally expected raw-manifest digest, current adopted-contract digest, inclusive
Asia/Shanghai validity dates, exact files/hashes/sizes, safe DOCX/PDF markers and the exact OA1
semantic metadata. A command-line entrypoint returns nonzero on any mismatch without opening a
database or port.

## Explicit Non-Closure

No entrypoint/Compose wiring, hot reload, database persistence, production input activation,
template/fee admin UI, document rendering, fee obligation, draft, billing, lifecycle mutation,
frontend or actual customer bundle contents. This task does not claim the demo runner starts.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-FRESH-LOCAL-RUNNER-20260816-01`
- `FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01`
- `FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01`
- `FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01`
- `FPMS-DEMO-ABC-FINANCE-UI-20260816-01`
- `FPMS-DEMO-ABC-LIVE-E2E-20260816-01`

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/scripts/validate_demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `artifacts/FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01/**`

## Verification Commands

1. RED proves no preflight implementation exists.
2. Targeted pytest covers valid input plus digest, validity, unknown key, path/file/hash, marker,
   ZIP safety and OA semantic failures.
3. Scoped Ruff passes for the three Python files.
4. CLI smoke accepts one temporary valid bundle and rejects a tampered manifest before any
   database path exists.
5. Exact allowlist and `git diff --check` pass. No broad/release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01/`

## Rollback

Revert the atomic story commit. It removes only the pure bundle validator, CLI and focused tests.

## Done definition

All targeted checks pass and the exact commit is ready for independent High review. No runtime
bundle bytes or product business writes are introduced.
