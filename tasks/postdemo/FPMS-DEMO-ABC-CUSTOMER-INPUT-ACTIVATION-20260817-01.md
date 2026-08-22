# FPMS-DEMO-ABC-CUSTOMER-INPUT-ACTIVATION-20260817-01

Status: BLOCKED
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "customer-decision", "runtime-input", "source-authority"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-CUSTOMER-INPUT-ACTIVATION-20260817-01.md

## Exact Closure Slice

Validate and activate one customer-supplied immutable local ABC runtime bundle against the already
implemented `fpms.demo-input-bundle/v1` and `fpms.demo-bundle-authority/v1` contracts. The bundle
must provide the exact internal DOCX template, required fictional lifecycle evidence PDFs, one
approved CNY service-price item, complete provenance, per-file SHA-256 values, and an independently
approved `authority.json` whose decision, manifest, source and file digests cross-bind exactly.
Persist the validated manifest and authority digests, execute the focused two-run local rehearsal,
and obtain independent High acceptance of that exact candidate and bundle.

## Explicit Non-Closure

No value, source, template, evidence, approval actor or approval timestamp may be inferred from the
temporary technical fixture. This task does not activate official fees, production templates,
legal/deadline authority, PostgreSQL/remote deployment, security remediation, product/release gates
or production release.

## Current Blocker

The customer-authoritative bundle bytes and approval receipt have not been supplied. The temporary
`DEMO_ONLY` fixture used by technical rehearsal is synthetic and cannot satisfy this task.

## Remaining Follow-Up Task IDs

- None inside the approved local ABC demo scope after this activation passes.

## Required External Inputs

1. One exact internal `.docx` template containing only the approved variables `case_no` and
   `client_name`, plus its size and SHA-256.
2. The exact fictional lifecycle evidence PDFs required by the selected local ABC capability set,
   each with role, metadata, size and SHA-256.
3. One approved `SERVICE_DEMO_PRICE` item with code, Chinese name, CNY amount, source reference,
   source version, source SHA-256 and the demo-only disclaimer.
4. `manifest.json` conforming to `fpms.demo-input-bundle/v1` and binding the frozen contract digest.
5. Independently approved `authority.json` conforming to `fpms.demo-bundle-authority/v1`, including
   `APPROVED`, approver, timestamp, exact customer decision digest, manifest digest, every source
   digest and every file digest.

## Allowed Files

- Customer-supplied immutable bundle directory outside the repository
- `artifacts/FPMS-DEMO-ABC-CUSTOMER-INPUT-ACTIVATION-20260817-01/**`

## Verification Commands

1. Run the bundle validator with both expected manifest and authority SHA-256 values.
2. Confirm missing, extra, stale, symlinked, digest-drifted or non-approved input fails before any
   business endpoint opens.
3. Run the focused visible-browser rehearsal twice on fresh isolated RUN_IDs with the exact bundle.
4. Obtain independent High review with zero P0/P1/P2 findings for this exact closure.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-CUSTOMER-INPUT-ACTIVATION-20260817-01/`

## Rollback

Stop the exact local runner PIDs and return the activation pointer to the previously validated
immutable bundle digest. Do not alter or delete historical bundle bytes or evidence.

## Done definition

The actual customer bundle is hash-bound, independently approved, validates fail-closed, and passes
two fresh local ABC rehearsals on the accepted candidate. Until then, status remains BLOCKED and no
`DEMO_READY` claim is permitted.
