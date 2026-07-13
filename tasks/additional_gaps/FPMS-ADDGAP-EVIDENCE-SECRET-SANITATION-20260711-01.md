# FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental final-close prerequisite
Executor role: Evidence Maintainer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Freeze the Task47 raw-secret hit paths, then mechanically replace only JWT bearer values and
credential values with `[REDACTED]`, preserving line count and all non-secret evidence text.

## Explicit Non-Closure

Do not change product/source/test behavior, command return codes, evidence conclusions, task status,
or any artifact file that is not in the frozen RED hit list. Do not regenerate historical tests.

## Dependencies

- Task47 `final_secret_scan` is RED and identifies raw JWT/credential material.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `tasks/additional_gaps/FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01.md`
- `artifacts/FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01/**`
- Only the exact pre-existing artifact paths frozen before editing in
  `artifacts/FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01/redaction_targets.txt`

No other file is authorized. The frozen target manifest is part of the allowlist and must contain
only path names, never secret values.

## Runtime Contracts

- Test-only evidence sanitation; product permission/status/envelope/UI/SQLite contracts unchanged.
- RED/GREEN scans report only path names and counts, never matched values.
- Normalized before/after hashes must prove that replacing recognized secret shapes is the only
  content change; line counts must remain identical.

## Verification Commands

- RED: path-only scan for raw JWT bearer and non-redacted credential shapes.
- GREEN: repeat the same path-only scan and require zero hits.
- Integrity: compare line counts and normalized hashes for every target.
- Scope: require every modified historical artifact path to occur in `redaction_targets.txt`.
- Evidence: canonical `lint` and `test` steps, atomic validation, independent review, and task gate.

## Evidence Path

- `artifacts/FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest and must pass review/evidence/gate independently.
Task47 must record it in the supplemental appendix.

## Done Definition

The target list and RED counts are preserved without values; only recognized secret substrings are
redacted; GREEN is zero; integrity/scope checks, independent review, evidence validation, and task
gate pass. Only then may this task be PASS.
