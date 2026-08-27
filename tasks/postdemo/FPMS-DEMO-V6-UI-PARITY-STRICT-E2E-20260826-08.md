# FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "ui", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08.md
Chosen runbook: `P0-e2e-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`,
  Task 08 only, under the active lean overlay.
- Accepted Ordinal 07 HEAD: `50509d40bc4bbefbbb8eb2072c95e5af31af73d1`.
- Accepted prerequisite Task 08R HEAD: `04e2b19f2e7e882eb78eb3f6541fa50aca5755b1`;
  the Stage 07 preview now provides the approved same-Session read-only audit projection.
- Accepted prerequisite Task 08S HEAD: `58cd1e7369d8f4f7dc96bfa8ca75346a08129bf9`;
  the normal case detail now exposes the approved read-only primary-contact projection.
- Accepted prerequisite Task 08T HEAD: `11c1879858cc811e801bc9a4e067d4403f5d0898`;
  a fresh case now returns the approved empty receipt summary without a console error.
- Accepted prerequisite Task 08U HEAD: `36c8a2349b75184e20cd2ae0a10e720e3786f143`;
  the Stage 03 frozen locator metadata now matches the accepted normal-UI seams.
- Accepted prerequisite Task 08V HEAD: `30b3478b7a6eedb0a3a3631a511c1ae1994f04b7`;
  reviewed non-final `ELECTRONIC_RECEIPT` evidence is now eligible in the normal visible receipt selector.
- Accepted prerequisite Task 08W HEAD: `482d4f8a29f6ed11fc2e091b6aca05971edc4954`;
  ordinary document detail views now defer the grant-candidate request until the visible grant review action.
- Accepted prerequisite Task 08X HEAD: `7c899e1a310cf1f520d4769d8a033dd31b216149`;
  the normal document detail now exposes the reviewed OA-notice binding/action and avoids incomplete deadline previews.
- Accepted prerequisite Task 08Y HEAD: `f931d001b225946ad341431599e6a64d69579e76`;
  the lifecycle evidence control now receives the parent-loaded OA template code on real document detail views.
- Accepted prerequisite Task 08Z HEAD: `075f6b49c8cc3669478d812413147e95d5b9803e`;
  three reviewed current OA reply roles now aggregate into one eligible visible reply-document candidate.

## Exact Closure Slice

Add one strict automated 01–11 browser journey and its anti-bypass/receipt gates. It must drive only
normal visible UI controls, passively observe network results, emit the frozen V6 ledgers and strict
receipt, and leave the existing A rehearsal separately runnable.

## Exact Behavior

1. A transitive-import static gate rejects request fixtures, `APIRequestContext`, `page.request`,
   direct fetch/axios/Node HTTP, SQL/ORM/backend scripts, evaluate/dynamic injection, mocks, and
   `/demo/abc` anywhere reachable from the strict spec.
2. The strict journey uses only normal navigation and visible fill/select/click/file-upload actions,
   plus passive response observation. Every business mutation maps to exactly one visible
   `action_id`; an unmatched, duplicated, hidden, or directly issued mutation fails.
3. The journey covers stages 01–11 and emits `ui-input-ledger.json`, `ui-output-ledger.json`,
   `ui-mutation-ledger.json`, screenshots, network/console arrays, and a strict
   `fpms.demo-v6-ui-parity/v1` PASS receipt.
4. Stage 07 proves preview no-write and the GOV 900+50=950 identities/digests. Stage 08 proves exact
   SERVICE 1500→1800 supersession, adjustment snapshots/digests, link transfer, domain purity, and
   locked GOV/SERVICE drafts. Stage 09 proves one GOV PayList, two pending-evidence payments totaling
   950, stable replay, and no SERVICE leakage. Stage 10 proves receipt does not settle, then
   1200/600 partial and final offsets, exactly two receipts/two offsets, and no GOV leakage. Stage 11
   is read-only and proves both authoritative chains, pending GOV evidence, settled SERVICE, and no
   new mutation.
5. The receipt comparator rejects actor reuse, shared run/database, candidate/tree/contract/bundle
   drift, missing/extra schema fields, non-whitelisted differences, missing action/screenshot/
   mutation correlation, and any network or console error. It accepts only one HUMAN plus one
   different-account CODEX receipt.
6. The runner gains only the plan-owned `--strict-ui` automated lane and receipt integration. Existing
   A and the headed manual/Codex UI-session path remain unchanged.

## Explicit Non-Closure

- No product endpoint, schema, migration, seed fact, fee/lifecycle rule, permission, security,
  customer bundle, Runbook/docs freeze, actor execution, candidate push, release, Docker support,
  generic workflow framework, or rewrite of the existing A runner.
- Do not use APIs/DB/scripts to perform business mutations, import the hybrid journey, split the
  demo into resumable subsystems, or run broad/release suites.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08.md`
- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10.md`
- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CANDIDATE-CLOSE-20260826-11.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-static-contract.mjs`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `scripts/compare_demo_v6_ui_receipts.py`
- `backend/tests/test_demo_v6_ui_session.py`
- `backend/tests/test_demo_v6_ui_receipt_comparator.py`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08/**`

## Verification Commands

```bash
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-static-contract.mjs
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python -m pytest -q \
  tests/test_demo_v6_ui_session.py tests/test_demo_v6_ui_receipt_comparator.py \
  tests/test_demo_integrated_a_runner.py)
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python \
  scripts/run_demo_integrated_a_rehearsal.py --profile TECHNICAL_REHEARSAL \
  --strict-ui --runs 1 --headless --artifact /tmp/fpms-demo-v6-strict-ui-task08
git diff --check
```

RED must be the first missing static restriction, action/mutation association, matrix field, or
comparator rejection. GREEN is one complete strict automated receipt plus all named negative
fixtures rejected. Remove only the exact verified temporary run root after evidence is captured.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-RUNBOOK-FREEZE-20260826-09`, blocked until this task is accepted.
- `FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10`, acceptance only after Task 09 candidate.
- `FPMS-DEMO-V6-UI-PARITY-CANDIDATE-CLOSE-20260826-11`, release-last close only.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, deferred until after the demo.

## Done Definition

The strict UI-only 01–11 automated journey passes from a fresh run, the anti-bypass and comparator
negative fixtures reject, A remains runnable, focused gates and exact scope pass, and an independent
zero-finding review plus atomic evidence accept the exact task range.

## Rollback

Run `git revert --no-edit <accepted-task-range>`. Ordinal 07 remains accepted and Ordinal 09 remains
blocked.
