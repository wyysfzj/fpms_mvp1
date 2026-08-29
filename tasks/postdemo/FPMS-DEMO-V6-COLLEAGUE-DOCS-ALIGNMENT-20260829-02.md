# FPMS-DEMO-V6-COLLEAGUE-DOCS-ALIGNMENT-20260829-02

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "docs", "fee", "lifecycle", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-COLLEAGUE-DOCS-ALIGNMENT-20260829-02.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Align the colleague quickstart, clone/deploy handoff, complete V6 runbook, seed/runtime input guide,
customer lifecycle HTML, frozen 103/30 UI-only contract, and V6 document checker with the current
customer-visible V6 behavior and the setup-only upload manifest. Use one future immutable tag name
`demo-v6-customer-20260829-r1`; distinguish current strict technical PASS from still-pending
independent HUMAN/CODEX receipts.

## Explicit Non-Closure

No new business fields, no change to 103 inputs/30 outputs/11 stages, no product UI or backend
behavior, no fee/date/source fact change, no actor receipt fabrication, no candidate push/tag,
no historical document deletion, and no production/security work.

## Allowed Files

- `docs/postdemo/demo-v6-colleague-clone-start-guide.md`
- `docs/postdemo/demo-v6-clone-deploy-handoff.md`
- `docs/postdemo/demo-lifecycle-customer-v6-runbook.md`
- `docs/postdemo/demo-lifecycle-customer-v6-seed-data.md`
- `docs/postdemo/demo-lifecycle-customer-v6.html`
- `FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs`
- `scripts/check_customer_demo_lifecycle_v6.py`
- `backend/tests/test_demo_integrated_a_runner.py`
- `tasks/postdemo/FPMS-DEMO-V6-COLLEAGUE-DOCS-ALIGNMENT-20260829-02.md`

## Done Definition

- Quickstart is tracked and clones the one immutable tag name, then delegates canonical checks to
  the handoff instead of defining a weaker second acceptance path.
- Handoff requires a fresh strict UI run before actor sessions, accurately states pending actor
  acceptance, documents upload-manifest usage, and limits comparator claims to its actual evidence.
- Runbook and HTML cover customer-name breadcrumb, case-list projection, structured document
  fields, historical/current gate context, visible official-fee actions, three current-first lanes,
  collapsed history, and customer-safe default hiding of UUID/hash/raw English status.
- Seed guide preserves all existing business values and adds exact operator use of
  `upload-manifest.json`, including the 12 frozen evidence rows and deadline metadata.
- The existing 103/30 rows express the latest checkpoints without changing counts or stage order.
- Checker reads all five V6 documents plus the JSON contract and fails on the stale candidate,
  missing current tokens, or inconsistent contract counts.

## Verification Commands

- `backend/.venv/bin/python scripts/check_customer_demo_lifecycle_v6.py`
- `node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs`
- `cd backend && .venv/bin/python -m pytest -q tests/test_demo_integrated_a_runner.py`
- `backend/.venv/bin/ruff check --no-fix scripts/check_customer_demo_lifecycle_v6.py backend/tests/test_demo_integrated_a_runner.py`
- `git diff --check`

## Evidence Path

- `artifacts/FPMS-DEMO-V6-COLLEAGUE-DOCS-ALIGNMENT-20260829-02/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-HISTORICAL-DOC-RETIREMENT-20260829-03`
- `FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10`
- `FPMS-DEMO-V6-UI-PARITY-CANDIDATE-CLOSE-20260826-11`
