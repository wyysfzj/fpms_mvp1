# FPMS Integrated Demo A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver one repeatable local demonstration in which one fictional client and one fictional case complete the prior V7 lifecycle journey and then the new runtime SERVICE input, unique AR bill, bank receipt and full offset journey.

**Architecture:** Preserve the accepted local ABC path and add a versioned integrated bundle successor rather than reinterpreting v1. A single visible Playwright contract drives public UI/API surfaces with dynamic identities; backend lifecycle/finance services remain the truth, while the runner creates only accounts/master data and disposable infrastructure. Each real RED becomes one separately materialized atomic task and no already-green product code is changed.

**Tech Stack:** FastAPI, SQLAlchemy/Alembic, SQLite, Vue 3/TypeScript/Element Plus, Playwright Chromium, Python evidence runner.

---

## Frozen inputs and boundaries

- Accepted design: `docs/superpowers/specs/2026-08-21-fpms-integrated-demo-a-design.md` at commit `d3d6cd4817284663edda257f7d606c82f994f1e4`.
- Design High review: `artifacts/FPMS-DEMO-INTEGRATED-A-DESIGN-HIGH-REVIEW-20260821-03/HIGH_REVIEW.md`, SHA-256 `6c70874e5060ddcea0a345d92e1573a66efb2ec078d870bbe3becbad75e0ed28`.
- Execution mode: inline, one atomic task at a time. Shared schemas, routers, frontend APIs/routes and SQLite-writing verification are serialized.
- No direct DB business writes, route mocks, request interception, lifecycle enrichment, fixed business IDs or skipped checkpoints.
- Synthetic input remains `SYNTHETIC_TEST_ONLY`; actual customer activation is an external gate.
- No production, PostgreSQL, remote deployment, security, broad product or release closure.

## File responsibility map

| Area | Exact files | Responsibility |
| --- | --- | --- |
| Integrated input contract | `backend/app/core/demo_bundle.py`, `backend/tests/test_demo_abc_runtime_bundle.py` | Parse both accepted ABC v1 and additive integrated-a-v1; expose immutable template/rate/evidence descriptors. |
| Runtime metadata/API | `backend/app/modules/fees/demo_service.py`, `backend/app/modules/fees/demo_service_schemas.py`, `backend/tests/test_demo_abc_runtime_bundle.py` | Return exact visible provenance without creating business facts. |
| Finance presentation | `frontend/src/modules/demo/pages/DemoAbc.vue`, `frontend/src/modules/demo/demo.api.ts`, `frontend/src/modules/demo/demo-contract.ts`, `frontend/tests/demo-abc-contract.mjs` | Display exact template/rate provenance and retain accepted finance actions. |
| Evidence review recovery | `frontend/src/api/documents.ts`, `frontend/src/modules/documents/components/AttachmentList.vue`, focused document review tests | Consume POST truth/reconcile unknown transport without masking deterministic rejection. |
| Canonical journey | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`, optional focused support beside that file | Execute IA-00…IA-18 on one dynamic case using public surfaces. |
| Static browser contract | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs` | Reject mocks, DB writes, enrichment, fixed business IDs and skips; require every checkpoint token. |
| Local runner/evidence | `scripts/run_demo_integrated_a_rehearsal.py`, `backend/scripts/run_local_demo_abc.py` only if a generic profile seam is required, focused runner test | Create two fresh runs, start services, run headed Chromium, export lifecycle/finance postconditions and clean exact roots. |
| Atomic governance | `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-*.md`, task-local `artifacts/**` | Exact closure, RED/GREEN, allowlists, review and acceptance evidence. |

### Task 1: Materialize the full integrated browser contract and prove RED

**Task ID:** `FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01`

**Files:**
- Create: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- Create: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
- Create: `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01.md`
- Evidence: `artifacts/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01/**`

- [ ] **Step 1: Write the static contract first**

Require every literal `IA-00` through `IA-18`; reject `page.route(`, `route.fulfill(`,
`SessionLocal`, `sqlite3`, `pdP1LiveSeed`, `enrich`, `test.skip`, `markSkeleton` and fixed UUIDs.
Require two login identities, the single dynamic `caseId`, bundle-role upload mapping, lifecycle
tuple assertions, the four superseded-task mutations and final finance assertions.

- [ ] **Step 2: Run the static contract and observe RED**

Run:

```bash
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs
```

Expected: FAIL because the integrated browser spec does not yet exist.

- [ ] **Step 3: Add the contract-complete Playwright scenario**

Start from the tested helpers in `addgap-final-real-path.spec.ts` and
`demo-abc.live-backend.spec.ts`, but use one client and one case. The spec must:

- login visibly as operator and obtain a separate reviewer session;
- create client/contact/case with dynamic suffix;
- execute and label all IA checkpoints;
- upload only files located through the integrated manifest role mapping;
- review every lifecycle evidence version with the separate reviewer;
- use exact first/second OA due-date triples and distinct IDs;
- stop grant flow after current-task `PAY`, with zero activated official-fee carriers;
- continue through the existing demo SERVICE/locked-draft/bill/payment/offset UI;
- save per-checkpoint JSON plus key screenshots.

- [ ] **Step 4: Run the static contract GREEN**

Expected: PASS, with no browser/backend execution yet.

- [ ] **Step 5: Run one current-candidate browser attempt and preserve behavioral RED**

Run the existing local runner with the integrated spec selected explicitly. Expected first failure:
the accepted v1 bundle lacks `integrated-a-v1` roles/metadata. If it fails earlier, record the first
actual checkpoint and do not infer later failures.

- [ ] **Step 6: Commit only the test contract**

```bash
git add FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.* tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01.md
git commit -m "test(demo): freeze integrated scheme A journey"
```

### Task 2: Add the integrated runtime-bundle successor

**Task ID:** `FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02`

**Files:**
- Modify: `backend/app/core/demo_bundle.py`
- Modify: `backend/tests/test_demo_abc_runtime_bundle.py`
- Create: `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02.md`
- Evidence: `artifacts/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02/**`

- [ ] **Step 1: Add failing parser tests**

Test the exact 12 ordered roles, sequence-2 metadata, grant original/replacement metadata,
pairwise-distinct hashes, 13 authority file digests and old-v1 compatibility. Test missing/extra
role, sequence fallback, hash alias, wrong supersedes role and schema confusion as fail-closed.

- [ ] **Step 2: Run focused RED**

```bash
source /tmp/fpms-demo-python-20260817/bin/activate
pytest -q backend/tests/test_demo_abc_runtime_bundle.py -k integrated
```

Expected: FAIL because only `fpms.demo-input-bundle/v1` and eight roles are accepted.

- [ ] **Step 3: Implement the minimal version dispatch**

Keep the current v1 constants and validator byte-compatible. Add an exact integrated-a-v1 role
table and metadata validator. Extend the immutable snapshot with evidence descriptors containing
role/path/hash/metadata; do not expose mutable manifest dictionaries. Both versions keep the same
path, visible-marker, authority, size/hash and forbidden-root protections.

- [ ] **Step 4: Run focused GREEN and Ruff**

```bash
pytest -q backend/tests/test_demo_abc_runtime_bundle.py
/Users/cfcc/Library/Python/3.11/bin/ruff check backend/app/core/demo_bundle.py backend/tests/test_demo_abc_runtime_bundle.py
```

- [ ] **Step 5: Re-run the browser contract**

Expected next RED must advance beyond IA-00. Preserve its exact checkpoint/log before Task 3.

- [ ] **Step 6: Independent review and atomic commit**

Commit message: `feat(demo): add integrated input bundle contract`.

### Task 3: Expose exact provenance on the visible finance chapter

**Task ID:** `FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03`

**Files:**
- Modify: `backend/app/modules/fees/demo_service.py`
- Modify: `backend/app/modules/fees/demo_service_schemas.py`
- Modify: `frontend/src/modules/demo/pages/DemoAbc.vue`
- Modify only if decoder contract requires it: `frontend/src/modules/demo/demo.api.ts`
- Modify: `frontend/tests/demo-abc-contract.mjs`
- Create: `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03.md`
- Evidence: `artifacts/FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03/**`

- [ ] **Step 1: Add failing API/UI contract assertions**

Assert visible labels and exact values for bundle ID/version/manifest hash, template code/file SHA,
rate item/source ref/source version/source SHA and disclaimer. Assert `未配置` for official fees and
that no official fee value enters the total.

- [ ] **Step 2: Run RED**

Expected: backend already returns most fields; frontend contract fails on absent rate source SHA
and explicit official-fee boundary.

- [ ] **Step 3: Implement only missing presentation fields**

Do not add an admin upload system or persistent activation table. Render immutable values returned
by `/fees/demo-service-item`; keep hashes selectable/wrappable and preserve Simplified Chinese.

- [ ] **Step 4: Run GREEN**

```bash
node frontend/tests/demo-abc-contract.mjs
cd frontend && npm run typecheck
cd frontend && npx eslint src/modules/demo/pages/DemoAbc.vue src/modules/demo/demo.api.ts
```

- [ ] **Step 5: Independent review and commit**

Commit message: `feat(demo): show integrated input provenance`.

### Task 4: Close public evidence upload/review reconciliation for the integrated path

**Task ID:** `FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04`

**Files:**
- Modify only on demonstrated RED: `frontend/src/api/documents.ts`
- Modify only on demonstrated RED: `frontend/src/modules/documents/components/AttachmentList.vue`
- Add focused test beside the existing document evidence-review frontend contract
- Create: `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04.md`
- Evidence: `artifacts/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04/**`

- [ ] **Step 1: Add failing transport/reviewer tests**

Cover operator upload, different reviewer APPROVE, authoritative POST response, dropped response
reconciliation with the same immutable key, and deterministic 4xx without GET masking. Self-review,
wrong case and changed timestamp/key payload must make no lifecycle write.

- [ ] **Step 2: Run RED and identify whether the current accepted fix already closes it**

If all focused tests pass, create zero-product-diff evidence and do not edit the two product files.
Otherwise preserve the exact failing trace.

- [ ] **Step 3: Apply the minimum reconciliation change**

Consume the POST projection. Only unknown transport outcomes may query durable evidence state; do
not turn 400/409 into an old success. Reuse one timestamp and idempotency key for one UI intent.

- [ ] **Step 4: Run focused tests, typecheck and scoped lint**

- [ ] **Step 5: Independent review and commit (or zero-diff PASS)**

### Task 5: Execute one-case filing and first-OA lifecycle

**Task ID:** `FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05`

**Files:**
- Primary test owner: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- Modify product files only when a focused RED identifies the exact owner under
  `backend/app/modules/official_workflows/**`, `backend/app/modules/documents/**`,
  `backend/app/modules/cases/**` or the corresponding frontend page/API.
- Create the exact task card after the first failing checkpoint freezes the allowlist.

- [ ] **Step 1: Run IA-01…IA-06 against a fresh database**

Assert client/contact/case, 60-row catalog, existing-first filing package, every filing prerequisite
projection, first OA five-surface due-date triple, reused OA resolve and OA_OUT with task still OPEN.

- [ ] **Step 2: For each first failure, write a focused backend/frontend RED before product code**

Do not combine unrelated lifecycle events. If more than one owner fails, materialize sequential
`-05A`, `-05B` tasks rather than widening an allowlist.

- [ ] **Step 3: Implement the minimum owner-local fix and run its focused GREEN**

- [ ] **Step 4: Re-run IA-01…IA-06 from a new run ID**

Expected: PASS without direct DB writes, fixed business IDs or enrichment.

- [ ] **Step 5: Independent review and atomic commit(s)**

### Task 6: Close receipt gates and the independent second OA

**Task ID:** `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`

**Files:**
- Primary test owner: integrated Playwright spec.
- Likely focused owners, only after RED: `backend/app/modules/official_workflows/service.py`,
  `backend/app/modules/documents/lifecycle_evidence_adapters.py`, relevant schemas/API and focused
  tests; frontend OA/document pages only for an observed UI blocker.

- [ ] **Step 1: Run IA-07…IA-09**

Cross-case and same-case-wrong-source receipts must preserve counts/state. Correct receipt archives
only its package/task. Sequence-2 notice must use its own bundle hash, exact due-date triple and new
source/package/task/OA_OUT/receipt identities; sequence-1 reuse and incomplete triple must no-write.

- [ ] **Step 2: Write one owner-local RED for the first actual failure**

- [ ] **Step 3: Implement minimum GREEN and rerun the focused contract**

- [ ] **Step 4: Re-run IA-07…IA-09 on a new run ID**

- [ ] **Step 5: Independent review and atomic commit(s)**

### Task 7: Preserve grant replacement while removing the historical fee shortcut

**Task ID:** `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`

**Files:**
- Primary test owner: integrated Playwright spec.
- Likely focused owners, only after RED: `backend/app/modules/grant_fees/**`, document grant adapter,
  `frontend/src/api/grantFees.ts`, grant task pages and focused tests.

- [ ] **Step 1: Run IA-10…IA-12**

Create original and replacement documents from distinct bundle evidence hashes. Assert exact
grant-registration projection, old/new lineage, one actionable task, four old-task mutation gates,
current-task PAY once and zero activated official-fee item/obligation/draft/payable carriers.

- [ ] **Step 2: Preserve expected historical RED**

The old `addgap-final-real-path.spec.ts` directly generates a grant draft. Update its contract only
after the new test proves the customer/source boundary: PAY may persist, but missing official-fee
authority cannot create a payable draft.

- [ ] **Step 3: Implement the smallest fail-closed correction if current behavior writes a draft**

Do not infer an official amount from the SERVICE rate or synthetic notice. Return `409
CONFIG_REQUIRED`/no-write for the official draft lane while leaving the separate service path
available.

- [ ] **Step 4: Run focused grant lifecycle/lineage/instruction regressions and scoped lint**

- [ ] **Step 5: Re-run IA-10…IA-12 and obtain independent review**

### Task 8: Connect the accepted ABC finance chapter to the same lifecycle case

**Task ID:** `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`

**Files:**
- Modify only if RED: `frontend/src/modules/demo/pages/DemoAbc.vue`,
  `frontend/src/modules/demo/demo.api.ts`, accepted demo finance backend services and focused tests.
- Primary test owner: integrated Playwright spec.

- [ ] **Step 1: Run IA-13…IA-17 using the IA-02 case ID**

Assert one SERVICE obligation, one LOCKED draft, exact bundle amount, unique/reused bill, unique
bank receipt, one active offset, settled/fully allocated zero balances and matching case receipt.
Reload all touched pages and assert the displayed IDs match the current route object.

- [ ] **Step 2: Run accepted ABC focused tests before editing**

If they and the integrated slice pass, record a zero-diff PASS. Otherwise add only the failing
same-case/provenance/route assertion and follow RED→GREEN.

- [ ] **Step 3: Run frontend contracts, typecheck, scoped ESLint and focused backend finance tests**

- [ ] **Step 4: Independent review and atomic commit (or zero-diff PASS)**

### Task 9: Build the canonical integrated two-run rehearsal controller

**Task ID:** `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`

**Files:**
- Create: `scripts/run_demo_integrated_a_rehearsal.py`
- Add focused runner test under `backend/tests/` or `scripts/tests/` following current repository style.
- Create: `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09.md`

- [ ] **Step 1: Write runner contract RED**

Require exact candidate clean pin, integrated bundle schema, two distinct run roots and business
identity sets, headed mode, IA 19/19 results, lifecycle tuples, evidence-role mappings, finance
counts/states, screenshots, redacted commands, checksums and cleanup/no-listener receipts.

- [ ] **Step 2: Implement by extracting only the reusable mechanics from `run_demo_abc_rehearsal.py`**

Do not mutate/delete old evidence. Use a new artifact family and exact run-root prefix. Export DB
postconditions read-only after the browser exits; the browser remains the business writer.

- [ ] **Step 3: Run one diagnostic integrated rehearsal**

Expected: all IA checkpoints PASS or the exact first remaining task blocker is captured.

- [ ] **Step 4: Run focused runner tests and Ruff**

- [ ] **Step 5: Independent review and commit**

### Task 10: Final integrated acceptance

**Task ID:** `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

**Files:**
- Evidence only: `artifacts/FPMS-DEMO-INTEGRATED-A-FINAL-REHEARSAL-20260821-01/**`
- Final task card and independent High report artifacts.

- [ ] **Step 1: Run the canonical focused backend and frontend gate on the exact candidate**

No broad/product/release gate. Store literal commands, rc, duration, candidate commit/tree and
scoped results.

- [ ] **Step 2: Run two fresh headed Chromium rehearsals**

Both must show IA 19/19 PASS with different run/client/case/OA/task/draft/bill/payment/offset IDs.
Each ends at `GRANT_PENDING` lifecycle projection plus `SETTLED` bill,
`FULLY_ALLOCATED` payment and `0.00 CNY` balances; this is a registration-pending fictional story,
not patent-in-force truth.

- [ ] **Step 3: Validate evidence and cleanup**

All checksums pass; no credentials/PII/full HAR; worktree is clean; exact run roots removed; no
listeners remain on 8000/5173.

- [ ] **Step 4: Independent High review**

Reviewer must bind the exact candidate/patch/evidence and return `APPROVED`,
`P0/P1/P2 = 0/0/0` for the integrated local technical scope.

- [ ] **Step 5: Declare only the exact result**

Allowed claim: `INTEGRATED_TECHNICAL_REHEARSAL_PASS`. Customer-specific output remains blocked
until an actual customer-authorized runtime bundle passes the separate activation gate. Do not
claim product/release/production/security/PostgreSQL readiness.

## Execution order and stop rules

The strict order is `1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10`. Tasks 5–8 may produce zero-diff
evidence when the current implementation already satisfies their RED. They may not run in parallel
because they share the canonical browser spec and disposable SQLite verification lane.

At every task:

1. materialize exact task path/closure/non-closure/allowlist;
2. initialize evidence before product edits;
3. run and preserve correct RED;
4. implement the minimum GREEN;
5. run focused tests/lint/scope;
6. obtain independent High zero-finding review;
7. finalize evidence and commit before the next ordinal.

A newly discovered independent closure is assigned a suffix task and inserted immediately after its
parent ordinal. A transport failure is reconciled from durable evidence; completed ordinals are
never repeated. Three review iterations on the same unresolved contract stop for customer input;
test/runtime defects do not trigger redesign.
