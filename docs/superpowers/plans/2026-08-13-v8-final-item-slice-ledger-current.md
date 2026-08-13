# V8 Final Item-to-Slice Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Row282 with a current Git-native, item-level ledger for all 302 effective product graph nodes while preserving Row283 and production configuration non-closure.

**Architecture:** A focused Python contract derives the 283 catalog items from the frozen catalog and verifies every item against the current coverage ledger. A JSON output adds the exact nineteen external product nodes through an explicit identity-to-story mapping, plus separate audit-only lineage and configuration residuals. The candidate is independently reviewed before one coverage-ledger adoption.

**Tech Stack:** Python 3.11, pytest, JSON, Git tree fingerprints, repository lean coverage checker.

---

### Task 1: Freeze Row282 latest-wins contract

**Files:**
- Modify: `tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md`
- Reference: `docs/superpowers/specs/2026-08-13-v8-final-item-slice-ledger-current-design.md`

- [ ] Add a latest-wins appendix preserving the original closure but replacing taskctl/artifact mechanics with the current C3 candidate/review/ledger protocol.
- [ ] Freeze the exact 19 external identities, `302/216/86` counts, CONFIG_REQUIRED residual and Row283 non-closure.
- [ ] Freeze this exact Foundation external identity → supporting current-story table. Each
      supporting story already owns the exact current product/test paths for that identity;
      Row282 records the mapping without taking ownership of those paths or using a
      representative substitute:

| External identity | Supporting current story IDs |
| --- | --- |
| `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01` | `V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-CURRENT-ADOPTION` |
| `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` | `V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION` |
| `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01` | `V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION` |
| `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01` | `V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01` | `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` | `V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` | `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION`, `V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION` |
| `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01` | `V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01` | `V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION`, `V8-FULL-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION` |
| `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01` | `V8-FILING-LIFECYCLE-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01` | `V8-FILING-LIFECYCLE-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` | `V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION` |
| `FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01` | `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01` | `V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01` | `V8-D4-08-OA-STRUCTURED-ATTACHMENT-PROMOTION` |
| `FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01` | `V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-CURRENT-ADOPTION` |
| `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01` | `V8-CNIPA-ANNUITY-RATE-CANDIDATE-CURRENT-ADOPTION` |
| `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01` | `V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-CURRENT-ADOPTION` |
| `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01` | `V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-CURRENT-VERIFICATION` |
- [ ] Freeze the exact allowlist and verification commands.
- [ ] Run `git diff --check -- tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md`.
- [ ] Commit the task card together with the RED contract in Task 2.

### Task 2: Write the failing item-level contract

**Files:**
- Create: `backend/tests/test_v8_final_item_slice_ledger.py`

- [ ] Require the output JSON and close story with their exact schema/mappings; the initial run must fail specifically with `FileNotFoundError` because the required output is absent.
- [ ] Assert catalog hash and immutable counts `283/197/86`.
- [ ] Assert all catalog rows 1–281 resolve to current stories and Row282 resolves only after adoption; Row283 remains pending.
- [ ] Assert the exact 19 external identities and explicit accepted-story mappings.
- [ ] Assert every mapped story is current, reachable, reviewed, fingerprinted and has nonempty tests.
- [ ] Assert configuration residuals, overlay audit lineage and Row283 non-closure.
- [ ] Run `cd backend && .venv/bin/pytest -q tests/test_v8_final_item_slice_ledger.py` and record the missing-output `FileNotFoundError` RED.
- [ ] Commit task card + RED test.

### Task 3: Materialize the minimum derived ledger

**Files:**
- Create: `docs/product/v8/final-item-slice-ledger.json`
- Create: `docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md`
- Modify: `backend/tests/test_v8_final_item_slice_ledger.py`

- [ ] Generate 283 catalog entries by joining catalog rows to the current coverage ledger without copying product behavior.
- [ ] Add the exact 19 explicit external entries and their accepted story IDs.
- [ ] Add separate audit-only Delta-1..4/G1/G2 lineage.
- [ ] Add exact production configuration residuals and `FINAL_CLOSE_PENDING` Row283 state.
- [ ] Run the focused test and make all pre-adoption cases pass.
- [ ] Run `cd backend && .venv/bin/ruff check tests/test_v8_final_item_slice_ledger.py`.
- [ ] Run `python3 -m json.tool docs/product/v8/final-item-slice-ledger.json >/dev/null`.
- [ ] Let `ROW282_BASE` be the full SHA before Task 1 and run `git diff --check "$ROW282_BASE"..HEAD -- tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md backend/tests/test_v8_final_item_slice_ledger.py docs/product/v8/final-item-slice-ledger.json docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md`.
- [ ] Commit only the candidate files; do not include coverage-ledger or reviewer receipt.
- [ ] Freeze the review range as `ROW282_BASE..ROW282_CANDIDATE_SHA`. The approved design and this approved plan precede `ROW282_BASE` and are excluded from the candidate fingerprint.

### Task 4: Bind candidate fingerprint and ledger adoption patch

**Files:**
- Modify: `docs/product/v8/coverage-ledger.json`
- Test: `backend/tests/test_v8_final_item_slice_ledger.py`

- [ ] Compute the exact candidate-path Git tree fingerprint at `ROW282_CANDIDATE_SHA` over exactly the task card, focused test, output JSON and close story.
- [ ] Change only Row282 to `CURRENT_VERIFIED`, add one Row282 story, and leave Row283 pending.
- [ ] Assert the candidate SHA, exact paths, tree fingerprint, review ref, counts and residuals.
- [ ] Run `cd backend && .venv/bin/pytest -q tests/test_v8_final_item_slice_ledger.py`.
- [ ] Run `cd backend && .venv/bin/ruff check tests/test_v8_final_item_slice_ledger.py`.
- [ ] Run `python3 -m json.tool docs/product/v8/final-item-slice-ledger.json >/dev/null && python3 -m json.tool docs/product/v8/coverage-ledger.json >/dev/null`.
- [ ] Run `python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha "$ROW282_CANDIDATE_SHA"`.
- [ ] Run `git diff --check "$ROW282_BASE".."$ROW282_CANDIDATE_SHA" -- tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md backend/tests/test_v8_final_item_slice_ledger.py docs/product/v8/final-item-slice-ledger.json docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md` and `git diff --check -- docs/product/v8/coverage-ledger.json`.
- [ ] Record `git diff --binary -- docs/product/v8/coverage-ledger.json | shasum -a 256`; the reviewer receipt must bind this sole-ledger patch hash.
- [ ] Keep the ledger patch uncommitted for independent review.

### Task 5: Independent High review and adoption

**Files:**
- Create by reviewer: `docs/product/v8/reviews/V8-FINAL-ITEM-SLICE-LEDGER-CURRENT-ADOPTION.md`
- Commit after review: `docs/product/v8/coverage-ledger.json`

- [ ] Independent reviewer audits the cumulative `ROW282_BASE..ROW282_CANDIDATE_SHA` range plus the separately hashed uncommitted sole-ledger patch and reruns focused pytest, Ruff and inventory.
- [ ] Require final `APPROVED`, P0/P1/P2 `0/0/0`; the reviewer commits only the receipt after approval.
- [ ] Commit only the reviewed coverage-ledger adoption.
- [ ] After the separate reviewed ledger-only adoption commit, run `cd backend && .venv/bin/pytest -q tests/test_v8_final_item_slice_ledger.py` and `python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha HEAD`.
- [ ] Confirm the worktree contains only unrelated `backend/uv.lock`.
- [ ] Hand off to Row283; do not run the release gate inside Row282.
