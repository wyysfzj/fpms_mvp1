# FPMS-DEMO-V6-MANUAL-UPLOAD-ROLE-GUARD-20260829-05

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "lineage", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-MANUAL-UPLOAD-ROLE-GUARD-20260829-05.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Prevent ordinary document UI uploads from being confirmed without an attachment role, and make
the V6 colleague-facing Runbook state the exact mapping from all twelve frozen evidence keys to
the existing Chinese attachment-role options.

## Explicit Non-Closure

No evidence model or enum change, no backend validation change, no upload API change, no lifecycle
or fee behavior change, no UI redesign, and no unrelated documentation cleanup.

## Allowed Files

- `frontend/src/modules/documents/components/AttachmentList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- `docs/postdemo/demo-lifecycle-customer-v6-runbook.md`
- `docs/postdemo/demo-v6-colleague-clone-start-guide.md`
- `tasks/postdemo/FPMS-DEMO-V6-MANUAL-UPLOAD-ROLE-GUARD-20260829-05.md`

## Done Definition

- The upload confirmation action is disabled until both a file and an existing attachment role
  are selected.
- The confirmation handler independently refuses an empty attachment role.
- The strict V6 UI test proves the disabled state before selecting the role.
- The Runbook maps all twelve frozen evidence keys to `合并PDF`, `电子申请回执`, or
  `官方通知书PDF` and fixes the operator order as file first, role second, confirm last.
- The colleague Quickstart points manual operators to that mandatory mapping.

## Verification Commands

- `backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py --strict-ui --runs 1 --headless --artifact <fresh-path>`
- `npm run typecheck --prefix frontend`
- `npm run lint --prefix frontend -- --quiet`
- `git diff --check`

## Evidence Path

- `artifacts/FPMS-DEMO-V6-MANUAL-UPLOAD-ROLE-GUARD-20260829-05/`

## Remaining Follow-Up Task IDs

- None
