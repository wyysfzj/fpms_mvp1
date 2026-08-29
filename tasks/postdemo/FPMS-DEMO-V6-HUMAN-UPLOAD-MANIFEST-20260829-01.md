# FPMS-DEMO-V6-HUMAN-UPLOAD-MANIFEST-20260829-01

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "lineage", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-HUMAN-UPLOAD-MANIFEST-20260829-01.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

For setup-only HUMAN/CODEX UI sessions, materialize the frozen runtime evidence files under the
external session artifact and write one non-secret `upload-manifest.json` that gives an operator
the exact file path and frozen evidence metadata needed for ordinary browser uploads.

## Explicit Non-Closure

No document upload shortcut, API/SQL write, business value change, evidence digest change,
production bundle support, UI redesign, security hardening, release, or actor acceptance.

## Allowed Files

- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_integrated_a_runner.py`
- `tasks/postdemo/FPMS-DEMO-V6-HUMAN-UPLOAD-MANIFEST-20260829-01.md`

## Done Definition

- Setup-only sessions expose copied evidence only inside `<artifact>/upload-files`.
- `<artifact>/upload-manifest.json` contains no credential and binds each row to the copied path,
  evidence key, Chinese title, document metadata, size, and SHA-256.
- Every copied path remains inside the artifact, exists for the life of the UI session, and matches
  the frozen bundle digest.
- The existing strict and technical rehearsal paths remain unchanged.

## Verification Commands

- `cd backend && .venv/bin/python -m pytest -q tests/test_demo_integrated_a_runner.py`
- `backend/.venv/bin/ruff check --no-fix scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py`
- `git diff --check`

## Evidence Path

- `artifacts/FPMS-DEMO-V6-HUMAN-UPLOAD-MANIFEST-20260829-01/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-COLLEAGUE-DOCS-ALIGNMENT-20260829-02`
- `FPMS-DEMO-V6-HISTORICAL-DOC-RETIREMENT-20260829-03`
