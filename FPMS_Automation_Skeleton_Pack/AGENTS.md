# FPMS automation instructions for Codex

## Scope

This directory contains structured FPMS QA assets.
Treat these files as the source of truth for automation intent:

- `docs/source/FPMS_SPEC_2_0.md`
- `docs/source/FPMS_SPEC2_0_Test_Cases_E2E.md`
- `data/manifests/*.yaml`
- `data/testcases/**/*.yaml`
- `data/boundary/*.yaml`
- `data/seeds/*.yaml`

## Working rules

1. Do not rename testcase IDs, boundary IDs, manifests, or schema files.
2. Do not delete structured YAML/JSON assets.
3. Only remove skeleton markers for handlers you fully implemented.
4. Keep selectors in page objects or shared helpers, not scattered across handlers.
5. Prefer pytest for API / service / DB assertions.
6. Prefer Playwright for UI flow, export, upload, download, and permission visibility.
7. All dynamic unique values must use `FPMS_RUN_ID` / `runtime.run_id`.
8. Preserve the handler-router-data mapping.
9. Favor minimal, reviewable changes over broad refactors.
10. When environment behavior differs between warning and blocking, make the assertion configurable or clearly documented.

## Validation rules

After each batch:
- run `python3 scripts/validate_assets.py`
- run targeted pytest for the changed wave
- run targeted Playwright specs for the changed wave
- summarize implemented cases, changed files, and remaining blockers

## Implementation order

Recommended order:
- W0
- A
- B
- G0
- D
- C
- E
- F
- G
- H
- X
- boundary

## Strong guardrails

Never “solve” a task by:
- changing testcase IDs
- weakening router logic to bypass execution
- mass-removing skeleton markers without real implementation
- replacing assertions with trivial truthy checks
