# FPMS-DEMO-ABC-EVIDENCE-PROVENANCE-HARDENING-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["browser", "demo", "evidence", "provenance", "runtime-input"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-EVIDENCE-PROVENANCE-HARDENING-20260817-01.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Controlling design: `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md` §9.
- Independent findings: `P1-8`, `P1-9`, `P2-3`.
- Dependencies: commits `fc3c381`, `ef0d84c`, `3da45be`, `f429247`.

## Exact Closure Slice

Provide one bounded technical-rehearsal controller that creates an unmistakably
`SYNTHETIC_TEST_ONLY` bundle, binds each run to exact HEAD/tree and bundle digests, starts the local
runner, captures runner/child PIDs and port listeners, runs the single visible Chromium ABC spec,
exports read-only SQLite postconditions, shuts down exact processes, removes only the exact run root,
redacts credentials and checksums every acceptance-critical artifact. Run it twice with distinct
RUN_IDs. Repair the corrupt historical reconstruction patch, populate blank historical summaries and
append a non-destructive FINANCE-UI result reconciliation.

## Explicit Non-Closure

No customer-authorized input, production, PostgreSQL, remote hosting, security, broad Playwright,
product/release gate or release claim. Historical raw result rows remain immutable.

## Allowed Files

- `scripts/run_demo_abc_rehearsal.py`
- `scripts/rebuild_demo_abc_evidence.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `tasks/postdemo/FPMS-DEMO-ABC-EVIDENCE-PROVENANCE-HARDENING-20260817-01.md`
- `tasks/postdemo/FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-02.md`
- `artifacts/FPMS-DEMO-ABC-*/**`

## Verification Commands

1. Static checks prove recorded commands contain no credential values and critical-file checksums are
   complete.
2. Historical reconstruction verifier recomputes every stored patch hash/length and finds no blank
   summary fields.
3. Two fresh headed Chromium runs use different RUN_IDs and each produces one SETTLED bill, one
   FULLY_ALLOCATED line, one active offset/receipt and three completed durable finance commands.
4. Exact candidate/tree, synthetic authority class, PIDs/listeners, DB export and cleanup are present
   and checksum-valid.

## Rollback

Revert the atomic script/task commit. Evidence artifacts are ignored and may be removed only by their
exact artifact path; run roots are removed only after postcondition export.

## Done definition

Evidence is mechanically bound, credential-redacted, complete and reproducible twice; independent
High acceptance remains required, while actual customer input remains a separate blocked gate.
