# FPMS Integrated Demo A Implementation Plan

> Execute with `superpowers:executing-plans`, TDD and the atomic evidence gate, one ordinal at a time.

**Goal:** one repeatable local demo where one fictional client/case completes the prior V7
lifecycle and the new runtime SERVICE input → locked draft → unique AR bill → bank receipt → offset.

**Authority:** accepted design
`docs/superpowers/specs/2026-08-21-fpms-integrated-demo-a-design.md` at
`d3d6cd4817284663edda257f7d606c82f994f1e4`; approved High report
`artifacts/FPMS-DEMO-INTEGRATED-A-DESIGN-HIGH-REVIEW-20260821-03/HIGH_REVIEW.md`
(SHA-256 `6c70874e5060ddcea0a345d92e1573a66efb2ec078d870bbe3becbad75e0ed28`);
written acceptance `docs/product/v8/customer-decisions/2026-08-21-integrated-demo-a-written-spec-acceptance.txt`.

**Non-closure:** customer activation, official-fee truth, production, PostgreSQL, remote deployment,
security, broad/product/release gates. Synthetic input is always `SYNTHETIC_TEST_ONLY`.

## Frozen cross-task contract

Canonical spec:
`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`.
It owns IA-00…IA-18 and one dynamic client/case. Historical `addgap-final-real-path.spec.ts` is
reference-only and never edited. Canonical controller:
`scripts/run_demo_integrated_a_rehearsal.py`, created in Task 1 before the first behavioral RED:

```text
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact <absolute-dir> --runs <1|2> [--headless]
```

For every ordered manifest role, the browser must persist and assert:

```text
role -> manifest path/hash/metadata -> visible-UI attachment id/content hash
     -> different-reviewer APPROVED evidence-version id/content hash
     -> exact consuming lifecycle command/result
```

All 12 files use the visible `AttachmentList` upload control and `setInputFiles`; a separate
reviewer browser context uses the visible review control. Direct attachment/review request calls
are forbidden. `evidence-role-map.json` proves: final submission → external-submission command and
activity; receipt/acceptance/preliminary/publication/substantive roles → their exact stored command
evidence; `FILING_FINAL_SUBMISSION` is the exact final-submission role; OA1/OA2 notice/receipt →
distinct reviewed ids/hashes, sequences, packages and tasks; grant original/replacement → their
reviewed ids/hashes and supersession lineage. OA2 also has its complete
`official_due_date / official_due_date_source / CONFIRMED` triple.

The static contract rejects `page.route`, `route.fulfill`, direct attachment/review request calls,
`SessionLocal`, `sqlite3`, enrichment, `test.skip`, `markSkeleton` and fixed business UUIDs. It
requires IA-00…18, all 12 roles, both actors, role-map fields, four old-task mutations and every
exact final-state field.

Each ordinal owns only its listed paths. Zero-product-diff still commits its task card, focused
test/contract and evidence. A failure outside the exact owners stops and materializes a separate
suffix task; it never widens the current allowlist.

Every ordinal uses the exact task/evidence/commit contract below. Each evidence root must contain
`task.json`, `summary.md`, `git/diff.patch`, `git/rev.txt`, `git/status.txt`, `commands.jsonl`,
`review/HIGH_REVIEW.md` and `checksums.sha256`; the review binds the exact candidate commit/tree and
returns `0/0/0` before the commit shown for that ordinal is accepted.

| Ordinal | Exact task path | Exact evidence root | Literal commit command |
| --- | --- | --- | --- |
| 1 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01/` | `git commit -m "test(demo): freeze integrated scheme A journey"` |
| 2 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02/` | `git commit -m "feat(demo): add integrated input bundle contract"` |
| 3 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03/` | `git commit -m "feat(demo): show integrated input provenance"` |
| 4 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04/` | `git commit -m "fix(documents): reconcile evidence review commands"` |
| 5 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05/` | `git commit -m "test(demo): close integrated filing and first OA"` |
| 6 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06/` | `git commit -m "test(demo): close receipt gates and second OA"` |
| 7 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07/` | `git commit -m "fix(demo): preserve grant authority boundary"` |
| 8 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08/` | `git commit -m "test(demo): connect finance to integrated case"` |
| 9 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09/` | `git commit -m "test(demo): harden integrated rehearsal controller"` |
| 10 | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10.md` | `artifacts/FPMS-DEMO-INTEGRATED-A-FINAL-REHEARSAL-20260821-01/` | `git commit -m "chore(demo): freeze integrated final acceptance"` |

## Task 1 — Browser contract plus executable RED

**ID:** `FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01`

**Files:** create canonical live spec; create
`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`;
create controller; create `backend/tests/test_demo_integrated_a_runner.py`; create exact task card;
evidence `artifacts/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01/**`.

- [ ] Static/runner RED, then minimal one-run controller and contract-complete spec:

```bash
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_integrated_a_runner.py
/Users/cfcc/Library/Python/3.11/bin/ruff check scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py
```

- [ ] Executable behavioral RED (expected first missing integrated bundle; preserve actual first):

```bash
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task01 --runs 1 --headless
```

- [ ] Review/evidence, remove only that temp root, then commit:

```bash
git add FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01.md
git commit -m "test(demo): freeze integrated scheme A journey"
```

## Task 2 — Integrated bundle successor

**ID:** `FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02`

**Files:** modify `backend/app/core/demo_bundle.py`,
`backend/tests/test_demo_abc_runtime_bundle.py`, controller and runner test; create exact task card;
evidence `artifacts/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02/**`.

- [ ] RED: exact 12 roles, OA2, grant original/replacement, pairwise hashes, 13 authority digests,
v1 compatibility, missing/extra/alias/schema-confusion fail closed.

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_abc_runtime_bundle.py -k integrated
```

- [ ] Implement exact schema dispatch/immutable descriptors and synthetic fixture builder; no
business writes. GREEN and advance real RED beyond IA-00:

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_abc_runtime_bundle.py backend/tests/test_demo_integrated_a_runner.py
/Users/cfcc/Library/Python/3.11/bin/ruff check backend/app/core/demo_bundle.py backend/tests/test_demo_abc_runtime_bundle.py scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task02 --runs 1 --headless
```

- [ ] Review/evidence/cleanup; commit `feat(demo): add integrated input bundle contract` with only
the four source/test files and exact task card.

## Task 3 — Visible provenance

**ID:** `FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03`

**Files:** `backend/app/modules/fees/demo_service.py`, `demo_service_schemas.py`,
`frontend/src/modules/demo/pages/DemoAbc.vue`, `frontend/src/modules/demo/demo.api.ts`,
`frontend/tests/demo-abc-contract.mjs`, exact task card; evidence
`artifacts/FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03/**`.

- [ ] RED/GREEN: visible bundle id/version/manifest hash, template code/file SHA, rate item/source
ref/source version/source SHA, disclaimer, and official fee `未配置` excluded from total.

```bash
node frontend/tests/demo-abc-contract.mjs
cd frontend && npm run typecheck
cd frontend && npx eslint src/modules/demo/pages/DemoAbc.vue src/modules/demo/demo.api.ts
```

- [ ] Review/evidence; commit `feat(demo): show integrated input provenance` with exact files.

## Task 4 — Evidence command reconciliation

**ID:** `FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04`

**Files:** `frontend/src/api/documents.ts`,
`frontend/src/modules/documents/components/AttachmentList.vue`; create
`frontend/tests/document-evidence-review-contract.mjs`; exact task card; evidence
`artifacts/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04/**`.

- [ ] RED/GREEN: POST truth, unknown-transport reconciliation with one immutable key/timestamp,
deterministic 4xx not masked by GET, self-review/wrong-case/hash-drift no-write.

```bash
node frontend/tests/document-evidence-review-contract.mjs
cd frontend && npm run typecheck
cd frontend && npx eslint src/api/documents.ts src/modules/documents/components/AttachmentList.vue
```

- [ ] If already green, record zero-product-diff; otherwise reconcile only unknown transport.
Review/evidence; commit `fix(documents): reconcile evidence review commands` with exact files.

## Task 5 — Filing and first OA

**ID:** `FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05`

**Files:** canonical spec; create `backend/tests/test_demo_integrated_first_oa.py`; exact possible
owners `backend/app/modules/cases/service.py`, `backend/app/modules/official_workflows/service.py`,
`backend/app/modules/official_workflows/filing_evidence_resolver.py`,
`backend/app/modules/documents/lifecycle_evidence_adapters.py`; exact task card; evidence
`artifacts/FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05/**`.

- [ ] RED/GREEN IA-01…06: client/contact/case, exact 60-row catalog, existing-first filing,
prerequisites, reviewed submission binding/activity, OA1 five-surface triple, reused package,
OA_OUT with task OPEN.

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_integrated_first_oa.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task05 --runs 1 --headless
```

- [ ] Edit only an exact failing owner or record zero-product-diff; review/evidence/cleanup; commit
`test(demo): close integrated filing and first OA` with the listed files.

## Task 6 — Receipt gates and OA2

**ID:** `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`

**Files:** canonical spec; create `backend/tests/test_demo_integrated_second_oa.py`; exact possible
owners `backend/app/modules/official_workflows/service.py`,
`backend/app/modules/documents/lifecycle_evidence_adapters.py`,
`backend/app/modules/documents/api.py`; exact task card; evidence
`artifacts/FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06/**`.

- [ ] RED/GREEN IA-07…09: two invalid receipt classes no-write; valid receipt closes only target;
OA2 uses mapped sequence-2 notice/receipt ids/hashes, complete triple and distinct identities;
sequence-1 reuse/incomplete triple no-write.

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_integrated_second_oa.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task06 --runs 1 --headless
```

- [ ] Exact owner or zero-product-diff; review/evidence/cleanup; commit
`test(demo): close receipt gates and second OA` with listed files.

## Task 7 — Grant replacement boundary

**ID:** `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`

**Files:** canonical spec; create `backend/tests/test_demo_integrated_grant.py`; exact possible owners
`backend/app/modules/grant_fees/service.py`, `api.py`, `schemas.py`,
`backend/app/modules/documents/lifecycle_evidence_adapters.py`, `frontend/src/api/grantFees.ts`;
exact task card; evidence `artifacts/FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07/**`.

- [ ] RED/GREEN IA-10…12: mapped original/replacement reviewed ids/hashes reach dispatch; exact
lineage; one actionable task; four old-task mutations 409/no-write; current PAY once; zero official
fee item/obligation/draft/payable.

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_integrated_grant.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task07 --runs 1 --headless
```

- [ ] Missing official-fee authority stays CONFIG_REQUIRED/no-write. Exact owner or zero-product-
diff; review/evidence/cleanup; commit `fix(demo): preserve grant authority boundary`.

## Task 8 — Same-case finance

**ID:** `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`

**Files:** canonical spec; `frontend/src/modules/demo/pages/DemoAbc.vue`, `demo.api.ts`;
`backend/app/modules/fees/demo_service.py`, `demo_service_schemas.py`;
`backend/tests/test_demo_abc_runtime_service_draft.py`,
`test_demo_abc_unique_ar_bill.py`, `test_demo_abc_payment_offset.py`; exact task card; evidence
`artifacts/FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08/**`.

- [ ] RED/GREEN IA-13…17 on IA-02 case: one SERVICE obligation/LOCKED draft, manifest amount,
unique/reused bill, bank receipt, one offset, SETTLED/FULLY_ALLOCATED, zero balances, matching
CaseReceipt, route identity after reload; official fee unavailable, not zero.

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_abc_runtime_service_draft.py backend/tests/test_demo_abc_unique_ar_bill.py backend/tests/test_demo_abc_payment_offset.py
node frontend/tests/demo-abc-contract.mjs
cd frontend && npm run typecheck
cd frontend && npx eslint src/modules/demo/pages/DemoAbc.vue src/modules/demo/demo.api.ts
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task08 --runs 1 --headless
```

- [ ] Exact owner or zero-product-diff; review/evidence/cleanup; commit
`test(demo): connect finance to integrated case`.

## Task 9 — Two-run controller

**ID:** `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`

**Files:** controller, `backend/tests/test_demo_integrated_a_runner.py`, exact task card; evidence
`artifacts/FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09/**`.

- [ ] RED/GREEN: clean pin, two roots/business identity sets, headed mode, IA 19/19, maps, exact
postconditions, redacted commands, screenshots, checksums, cleanup and no listeners.

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q backend/tests/test_demo_integrated_a_runner.py
/Users/cfcc/Library/Python/3.11/bin/ruff check scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task09 --runs 2 --headless
```

- [ ] Review/evidence/cleanup; commit `test(demo): harden integrated rehearsal controller`.

## Task 10 — Final acceptance

**ID:** `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

**Files:** create exact final task card; evidence
`artifacts/FPMS-DEMO-INTEGRATED-A-FINAL-REHEARSAL-20260821-01/**`; independent report
`artifacts/FPMS-DEMO-INTEGRATED-A-FINAL-HIGH-REVIEW-20260821-01/HIGH_REVIEW.md`.

- [ ] Commit task card first as `chore(demo): freeze integrated final acceptance`.
- [ ] Run only Tasks 2–9 focused gates, then two fresh **headed** runs:

```bash
python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-final --runs 2
```

- [ ] Both have distinct IDs, IA 19/19, and exact authoritative state:

```text
lifecycle_status = GRANT_REGISTRATION_IN_PROGRESS
lifecycle_stage = GRANT_REGISTRATION
application_status = APPLICATION_PENDING
source_state = CONFIRMED
legacy_display = GRANT_PENDING
bill_status = SETTLED
payment_status = FULLY_ALLOCATED
bill_balance = 0.00 CNY
payment_unapplied = 0.00 CNY
```

- [ ] Check hashes/screenshots/maps/no-write negatives; redact secrets/PII/full HAR; clean exact
temp root; prove clean tree/no 8000/5173 listeners. Independent High must bind exact candidate/tree/
evidence and return APPROVED 0/0/0.
- [ ] Claim only `INTEGRATED_TECHNICAL_REHEARSAL_PASS`; customer bundle activation remains external.

## Serial rule

Order `1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10`. SQLite/shared files are serialized. Each:
RED → minimum GREEN → focused verification → exact scope → independent High 0/0/0 → evidence →
commit. Completed ordinals are not repeated. Transport ambiguity reconciles durable state. A new
owner creates one exact suffix task, not redesign. Three failed reviews of the same contract stop
for customer input.
