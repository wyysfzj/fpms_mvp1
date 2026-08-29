# Client Detail Breadcrumb Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the customer UUID shown in the client-detail breadcrumb with the loaded customer name while preserving the UUID route.

**Architecture:** Reuse the existing Pinia `pageContext` seam already used by other detail pages. `ClientDetail.vue` owns setting and clearing its breadcrumb; `TopHeader.vue`, routing, APIs, and backend data remain unchanged.

**Tech Stack:** Vue 3, TypeScript, Pinia, Vue Router, Element Plus, Playwright.

**Execution Classification:** `shared_file_density=low`; `prereq_dependency_density=low`;
`be_fe_coupling=none`; `evidence_cost=medium`; `chosen_runbook=P0-single-lane-story`.

---

### Task 1: Client detail breadcrumb projection

**Files:**
- Create: `tasks/frontend/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01.md`
- Create: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-client-detail-breadcrumb.spec.ts`
- Modify: `frontend/src/modules/clients/pages/ClientDetail.vue`

- [ ] **Step 1: Materialize the exact atomic task**

Record the exact three-segment breadcrumb, UUID exclusion, context cleanup, allowed files, non-closure, focused verification, and separate Stage 00–11 request-level verification.

Before any test or product edit, validate the committed task and initialize evidence:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  check-task tasks/frontend/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  init FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 \
  --task-file tasks/frontend/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01.md \
  --allowlist tasks/frontend/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01.md \
  --allowlist frontend/src/modules/clients/pages/ClientDetail.vue \
  --allowlist FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-client-detail-breadcrumb.spec.ts
```

- [ ] **Step 2: Write the failing browser regression test**

Mock `/api/v1/auth/me`, two `/api/v1/clients/:id` responses, `/api/v1/cases`, and the contact list. Open the first detail page and assert the header breadcrumb text is exactly `客户管理 / 客户详情 / 澄岳智造技术（苏州）有限公司` and excludes the first UUID. Navigate away and then to the second detail page; assert the new customer name replaces the old context and excludes the second UUID.

Immediately after navigating from the first detail to `/clients`, assert the header no longer
contains either the first customer name or its UUID. This directly proves unmount cleanup before
the second detail load can overwrite stale state.

- [ ] **Step 3: Run the focused test to verify RED**

Start a dedicated Vite server in `frontend/` and retain its session for RED/GREEN only:

```bash
./node_modules/.bin/vite --host 127.0.0.1 --port 5188 --strictPort
```

The active `taskctl` receipt in this worktree is immutably bound to the main-repo path; do not edit
or impersonate that receipt. Run RED through the already-initialized standalone evidence wrapper
from repo root:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  run FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 red -- \
  env FPMS_BASE_URL=http://127.0.0.1:5188 \
  node FPMS_Automation_Skeleton_Pack/playwright_ts/node_modules/@playwright/test/cli.js \
  test src/tests/v8-client-detail-breadcrumb.spec.ts \
  --config=FPMS_Automation_Skeleton_Pack/playwright_ts/playwright.config.ts --workers=1
```

Expected: FAIL because the header currently renders `页面 / <client UUID>`.

- [ ] **Step 4: Implement the minimal projection**

In `ClientDetail.vue`:

```ts
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePageContext } from '../../../stores/pageContext'

const pageContext = usePageContext()
```

After `getClient(id)` succeeds:

```ts
pageContext.setBreadcrumb(['客户管理', '客户详情', client.value.name || '未命名客户'])
```

On unmount:

```ts
onUnmounted(() => {
  pageContext.clear()
})
```

- [ ] **Step 5: Verify GREEN and scoped checks**

Run the focused Playwright test as canonical `test`, scoped ESLint as canonical `lint`, then
record typecheck and the related V6 UI session contract through the same evidence wrapper. Run
`git diff --check` before review. Expected: all commands exit 0. Stop the dedicated Vite session
after the GREEN browser test.

Stage only the two implementation files so untracked test bytes are included in the candidate:

```bash
git add frontend/src/modules/clients/pages/ClientDetail.vue \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-client-detail-breadcrumb.spec.ts
```

Write a factual `summary.md` with status `AWAITING INDEPENDENT REVIEW`, then freeze the complete
staged candidate without claiming PASS:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  finalize FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 --status BLOCKED \
  --summary-file artifacts/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01/summary.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  run FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 scope -- \
  python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  validate FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 \
  --required-step lint --required-step test
```

- [ ] **Step 6: Obtain independent zero-finding review and close atomic evidence**

The reviewer must bind the final patch and report `Verdict: APPROVED`, `P0: 0`, `P1: 0`, and
`P2: 0`, including the SHA-256 of `git/diff.patch`. Save the report under the task artifact.
Record a successful `independent_review` step that checks the reviewer identity, unique verdict,
zero findings, and exact patch hash. Update the factual summary to terminal PASS, rerun `finalize`
on the unchanged staged candidate, and require all four successful steps:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  run FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 independent_review -- \
  python3 -c "from pathlib import Path; import hashlib; root=Path('artifacts/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01'); report=(root/'review/independent_review.md').read_text(); digest=hashlib.sha256((root/'git/diff.patch').read_bytes()).hexdigest(); required=['Reviewer-ID: client-breadcrumb-independent','Verdict: APPROVED','P0: 0','P1: 0','P2: 0']; assert all(report.count(item) == 1 for item in required); assert f'Patch-SHA256: {digest}' in report"
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  finalize FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 --status PASS \
  --summary-file artifacts/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01/summary.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py \
  validate FE-CLIENT-DETAIL-BREADCRUMB-20260829-01 \
  --required-step lint --required-step test --required-step scope \
  --required-step independent_review
```

Expected: `Task Gate PASS`. The taskctl incompatibility remains disclosed; no activation metadata
is copied, rewritten, or fabricated.

- [ ] **Step 7: Commit the task implementation**

```bash
git add tasks/frontend/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01.md \
  frontend/src/modules/clients/pages/ClientDetail.vue \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-client-detail-breadcrumb.spec.ts
git commit -m "fix(clients): show customer name in breadcrumb"
```

### Task 2: Requested full strict acceptance

**Files:**
- Create: `artifacts/demo-v6-strict-<commit>-20260829-run01/**`

- [ ] **Step 1: Freeze the clean candidate**

Record `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, and confirm `git status --short` is empty.

- [ ] **Step 2: Run complete Stage 00–11**

```bash
python3 scripts/run_demo_integrated_a_rehearsal.py --strict-ui \
  --profile TECHNICAL_REHEARSAL \
  --artifact <absolute-artifact-path> --runs 1
```

Expected: exit 0 and a strict PASS receipt bound to the frozen commit/tree.

- [ ] **Step 3: Verify the acceptance artifacts**

Confirm all 11 stage entries and screenshots exist; `network_errors` and `console_errors` are empty; cleanup removed the temporary run root and released ports 8000/5173.
