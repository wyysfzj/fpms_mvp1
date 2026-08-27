# FPMS-DEMO-V6-FRESH-CLONE-EGG-INFO-CLEANLINESS-20260827-09S

Status: ACTIVE
Risk-Tier: MEDIUM
Closure-Tags: ["demo", "handoff"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-FRESH-CLONE-EGG-INFO-CLEANLINESS-20260827-09S.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Keep a GitHub fresh clone clean after the documented editable backend dependency install by
removing generated `backend/fpms_api.egg-info` metadata from version control and ignoring Python
package metadata directories.

## Explicit Non-Closure

No product behavior, dependency version, packaging configuration, database, UI, receipt, lifecycle,
fee, deployment, or release change.

## Allowed Files

- `.gitignore`
- `backend/fpms_api.egg-info/*` (index removal only)
- `tasks/postdemo/FPMS-DEMO-V6-FRESH-CLONE-EGG-INFO-CLEANLINESS-20260827-09S.md`

## Done Definition

The five generated metadata files are no longer tracked, `pip install -e ".[dev]"` succeeds in a
fresh clone, and the clone remains clean afterward.
