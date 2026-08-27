# Case Lifecycle Three-Track Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the case-detail three-track wall of history with a customer-readable current-first summary while retaining the complete V6 history behind one explicit disclosure.

**Architecture:** Keep `CaseLifecycleOverlay.vue` as the sole owner of overlay fetching, revision-aware pagination, fact selection, warning visibility, and disclosure state. Add one stateless summary-card component and one shared Chinese display-mapping module; reuse the three existing detailed lane components unchanged except for importing the shared mapping functions. No API, store, backend, schema, fee arithmetic, or additional request is introduced.

**Tech Stack:** Vue 3 `<script setup>` + TypeScript, Element Plus, scoped CSS, existing Playwright mock/live harness, existing FPMS task evidence controller.

---

## Approved Inputs and Non-Negotiable Boundaries

- Design: `docs/superpowers/specs/2026-08-28-case-lifecycle-three-track-summary-design.md`
- Base: commit `90d9c56` plus approved design commit `27b20fc` on `codex/post-v6-mainpath-20260828`.
- Product implementation task: `FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01`.
- Use `@karpathy-guidelines`, `@superpowers:test-driven-development`, and
  `@atomic-evidence-gates` during execution.
- Do not modify API types, overlay endpoint semantics, backend code, database, lifecycle
  transition rules, fee calculations, permissions, runbooks, seed data, or the frozen V6
  worktree.
- Do not auto-fetch later overlay pages. While `overlay.hasMore` is true, only
  `centerSnapshot` may be presented as authoritative current state; all milestone-derived
  summary values use the approved incomplete-history message.
- Do not show balance or aggregate monetary amounts.
- Do not infer work from a state. “Next” comes only from explicit `OPEN` tasks.
- Do not expose `CUSTOMER_DECISION_GATE` or raw English status codes.

## File Responsibility Map

### Create

- `frontend/src/modules/cases/components/LifecycleSummaryCard.vue`
  - Stateless markup for one lane.
  - Renders fixed “现在是什么状态 / 最近发生了什么 / 下一步是什么” sections.
  - Accepts already translated text only; no API import, lifecycle logic, or local request.
- `frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts`
  - Owns the existing document activity, center state, and fee status Chinese mappings.
  - Exposes small fallback-safe display functions used by summary and existing lanes.
- `tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md`
  - Freezes this exact source/test allowlist and evidence commands before product edits.

### Modify

- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
  - Keeps fetch and pagination ownership.
  - Adds pure summary projection helpers/computed values.
  - Adds one `historyExpanded` state and one disclosure button.
  - Moves existing detailed grid and pagination inside the disclosed region.
  - Produces one deduplicated warning projection outside the collapsed history while retaining
    snapshot-versus-activity grouping.
- `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
  - Replaces the private activity-label table with the shared display function only.
- `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
  - Replaces the private center-state table with the shared display function only.
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
  - Replaces the private fee-status table with the shared display function only.

### Modify: focused Playwright contracts

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts`
  - New first-screen summary, one disclosure, ordering, responsive geometry, no extra GET.
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
  - Incomplete-history truth, disclosure before paging, automatic summary refresh at final page.
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`
  - Visible warnings while collapsed, stable dedupe, hidden customer gates.
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`
  - Open the history disclosure before asserting unchanged detailed facts.
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
  - Assert incomplete first-screen summary, then disclose before the existing three-page traversal.
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
  - Add one local `expandLifecycleHistory(page)` helper and call it only before the six existing
    detailed-lane inspection groups. Do not change business values, stage order, or mutation bindings.

No other file is authorized. If another test fails because it directly depends on detailed
lane visibility, stop and add that exact file to the task contract before editing it.

## Task 1: Materialize the Atomic Implementation Contract

**Files:**

- Create: `tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md`

- [ ] **Step 1: Write the task contract before product edits**

Use these exact contract facts:

```markdown
Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "lifecycle", "lineage", "ui"]
chosen_runbook: P0-frontend-heavy-story
```

Exact closure: implement the approved current-first summary, disclosure, warning dedupe,
pagination honesty, Chinese mapping reuse, and responsive layout.

Explicit non-closure: backend/API/types/schema/store/state-machine/fee arithmetic/balance/
permissions/demo data/runbook/frozen V6 worktree/unrelated UI cleanup.

The allowed files are exactly the source and Playwright paths in the File Responsibility Map,
the task file, and `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/**`.

Freeze these controller-compatible evidence commands in the task file:

```bash
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 lint git diff --check -- frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/LifecycleSummaryCard.vue frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 test shasum -a 256 frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/LifecycleSummaryCard.vue frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/verification.md artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/typecheck.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/eslint.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/build.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/v6-static-contract.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/mapping-baseline/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/mapping-after/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/focused-red/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/focused-green/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/compatibility/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/live-overlay/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/strict-pass-receipt.json artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/network-errors.json artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/console-errors.json artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/playwright.log
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 scope python3 scripts/evidence_scope.py finalize FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01
```

Run `git diff --check` immediately before each implementation commit; run the recorded latest lint
after the final source/test edit and before the final implementation commit so it observes those
working-tree bytes. The committed mapping extraction retains its own successful pre-commit check
in the task summary.

- [ ] **Step 2: Start evidence before any source/test edit**

Run:

```bash
./scripts/taskctl FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 start \
  --task-file tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md
```

Expected: JSON state `IMPLEMENTING`; baseline lists the existing untracked colleague guide as
external dirt and no product path as task-owned baseline.

- [ ] **Step 3: Confirm the frozen V6 worktree is untouched**

Run:

```bash
git -C .worktrees/demo-v6-ui-parity-20260826 status --short --branch
```

Expected: no new path from this implementation task.

## Task 2: Extract Existing Chinese Display Mappings Without Behavior Change

**Files:**

- Create: `frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts`
- Modify: `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
- Modify: `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
- Modify: `frontend/src/modules/cases/components/FeeObligationLane.vue`
- Test: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- Test: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
- Test: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`

- [ ] **Step 1: Run the existing detailed-lane baseline**

Run:

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/mapping-baseline" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-overlay-center-lane.spec.ts \
  src/tests/v8-overlay-document-lane.spec.ts \
  src/tests/v8-overlay-fee-lane.spec.ts
```

Expected: PASS before the extraction.

- [ ] **Step 2: Create the shared mapping module**

Move the existing constant entries byte-for-byte into the new module. Export only these
functions and their supporting value types:

```ts
export function centerStateText(value: string | null, emptyText = '-'): string {
  if (value === null) return emptyText
  return CENTER_STATE_LABELS[value as CenterState] ?? '未识别状态'
}

export function activityTypeText(
  activityType: string,
  fallback = '活动类型待确认',
): string {
  return ACTIVITY_TYPE_LABELS[activityType] ?? fallback
}

export function feeStatusText(value: string | null): string {
  if (!value) return '暂无'
  return FEE_STATUS_TEXT[value.toUpperCase()] ?? '未识别状态'
}
```

Do not rename enum values, add translations, or change fallbacks in this task.
Existing detailed lanes use the default `-`; summary snapshot values call
`centerStateText(value, '暂无')`.

- [ ] **Step 3: Replace each lane’s private mapping function**

- `DocumentEvidenceLane.vue`: call `activityTypeText(milestone.activityType)`.
- `LifecycleCenterLane.vue`: call `centerStateText(...)` for snapshot and axis values.
- `FeeObligationLane.vue`: call `feeStatusText(...)` everywhere the old `statusText` was used.
- Leave filtering, ordering, obligation merging, markup, testids, and CSS unchanged.

- [ ] **Step 4: Run typecheck and the unchanged lane tests**

Run:

```bash
npm --prefix frontend run typecheck
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/mapping-after" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-overlay-center-lane.spec.ts \
  src/tests/v8-overlay-document-lane.spec.ts \
  src/tests/v8-overlay-fee-lane.spec.ts
```

Expected: PASS; detailed text remains identical.

- [ ] **Step 5: Commit the behavior-neutral extraction**

```bash
git add \
  frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts \
  frontend/src/modules/cases/components/DocumentEvidenceLane.vue \
  frontend/src/modules/cases/components/LifecycleCenterLane.vue \
  frontend/src/modules/cases/components/FeeObligationLane.vue \
  tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md
git commit -m "refactor(cases): share lifecycle display labels"
```

## Task 3: Write the Summary and Disclosure RED Contracts

**Files:**

- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`

- [ ] **Step 1: Extend the first-screen contract fixture**

In `v8-case-detail-three-lane.spec.ts`, replace the empty milestone fixture with a compact
complete fixture containing:

- two references to the same current `evidence_version_id` plus one distinct pending version;
- one older and one newer DOCUMENT milestone;
- confirmed and unconfirmed center changes;
- duplicate `OPEN` task facts plus later/earlier deadlines;
- one earlier global OPEN task and one later FEE-only OPEN task so the fee card cannot accidentally
  use the global candidate;
- GOV CNY and SERVICE CNY/USD obligations;
- one unknown activity code to prove no English fallback.

Assert:

```ts
await expect(page.getByTestId('lifecycle-summary-grid')).toBeVisible()
await expect(page.getByTestId('lifecycle-summary-document')).toContainText('当前文件版本 2 份')
await expect(page.getByTestId('lifecycle-summary-document')).toContainText('已复核 1、待复核 1')
await expect(page.getByTestId('lifecycle-summary-lifecycle')).toContainText('实质审查')
await expect(page.getByTestId('lifecycle-summary-fee')).toContainText('官费：CNY 1 项')
await expect(page.getByTestId('lifecycle-summary-fee')).toContainText('服务费：CNY 1 项、USD 1 项')
await expect(page.getByTestId('lifecycle-summary-document')).toContainText('提交答复材料')
await expect(page.getByTestId('lifecycle-summary-document')).toContainText('2026-09-10')
await expect(page.getByTestId('lifecycle-summary-lifecycle')).toContainText('提交答复材料')
await expect(page.getByTestId('lifecycle-summary-fee')).toContainText('核对官费缴费任务')
await expect(page.getByTestId('lifecycle-summary-fee')).not.toContainText('提交答复材料')
await expect(page.getByTestId('lifecycle-summary-document')).toContainText('审查意见答复已递交')
await expect(page.getByTestId('lifecycle-summary-document')).toContainText('2026-08-20')
await expect(page.getByTestId('lifecycle-summary-lifecycle')).toContainText('实质审查 → 审查意见答复')
await expect(page.getByTestId('lifecycle-summary-lifecycle')).not.toContainText('未确认的更高序列变化')
await expect(page.getByTestId('lifecycle-summary-fee')).toContainText('官费 · 授权登记官费义务')
await expect(page.getByTestId('lifecycle-summary-fee')).toContainText('2026-08-22')
await expect(page.getByText('现在是什么状态', { exact: true })).toHaveCount(3)
await expect(page.getByText('最近发生了什么', { exact: true })).toHaveCount(3)
await expect(page.getByText('下一步是什么', { exact: true })).toHaveCount(3)
await expect(page.getByTestId('lifecycle-history-details')).toHaveCount(0)
```

Also assert no raw English state/activity code, no “客户余额”, and no amount total.
Add one empty overlay case that asserts null center values render “暂无”, and all three next slots
render “暂无明确下一步” when there is no OPEN task.

The fixture must place an eligible older and newer milestone in each lane, plus a still-higher
unconfirmed center change. These assertions prove DOCUMENT and FEE choose the highest sequence in
their lane while LIFECYCLE chooses the highest sequence confirmed change, not merely array order.

- [ ] **Step 2: Freeze one disclosure and responsive geometry**

At 1024px viewport, evaluate the three card bounding boxes and assert equal `y`. Resize to
860px and assert strictly increasing `y`. Restore desktop width, click “查看完整历史”, assert
detail order `document/lifecycle/fee`, button text becomes “收起完整历史”, and the overlay GET
count remains exactly one. Click “收起完整历史” and assert the detail region is removed, summary
remains visible, and the overlay GET count is still exactly one.

- [ ] **Step 3: Freeze partial-pagination honesty**

In `v8-case-detail-overlay-cursor.spec.ts`:

- before disclosure, assert three occurrences of “尚有历史未加载，完整状态待确认” in each
  milestone-derived slot: document current/latest/next, lifecycle latest/next, and fee
  current/latest/next (eight occurrences total); assert the center current snapshot still shows
  Chinese state;
- assert “加载更多生命周期记录” is absent while history is collapsed;
- click “查看完整历史” before using the existing load-more flow;
- after the terminal page changes `has_more` to false, assert the incomplete message disappears
  and the summary reflects the final highest sequence;
- keep all existing revision, cursor, dedupe, retry, and no-mutation assertions.

- [ ] **Step 4: Freeze warning dedupe outside collapsed history**

In `v8-case-detail-gates-warnings.spec.ts`, add the same customer-visible warning object to both
top-level `warnings` and `milestones[].warnings`. Assert exactly one rendered row for its stable
key, ordinary warnings visible before disclosure, all customer decision warnings absent, detail
container absent, and one overlay GET only.

- [ ] **Step 5: Run RED**

Run:

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/focused-red" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-case-detail-three-lane.spec.ts \
  src/tests/v8-case-detail-overlay-cursor.spec.ts \
  src/tests/v8-case-detail-gates-warnings.spec.ts
```

Expected: FAIL because summary testids, disclosure, degradation text, and warning dedupe do not
exist. Record the exact failure; do not weaken the assertions.

## Task 4: Implement the Minimal Summary UI

**Files:**

- Create: `frontend/src/modules/cases/components/LifecycleSummaryCard.vue`
- Modify: `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- Re-test: the three RED contracts from Task 3

- [ ] **Step 1: Build the stateless summary card**

Use this public prop shape; do not pass raw overlay objects:

```ts
const props = defineProps<{
  testId: string
  kicker: string
  title: string
  statusLabel: string
  currentLines: readonly string[]
  latestText: string
  latestAt: string | null
  nextText: string
  nextAt: string | null
  footnote?: string
  emphasis?: boolean
}>()
```

The template renders exactly three labeled sections. Use `data-testid="<testId>"`; use current
CSS variables; central emphasis is a 2px primary top border, not a different component. Render
`footnote` after the three sections when provided.

- [ ] **Step 2: Add deterministic pure projection helpers to the overlay component**

Keep helpers in `CaseLifecycleOverlay.vue`; do not create a store/composable/helper module.
Implement these exact rules:

```ts
const INCOMPLETE_HISTORY = '尚有历史未加载，完整状态待确认'

function latestMilestone(milestones, lane) {
  return milestones
    .filter((item) => item.lane === lane)
    .reduce((latest, item) => !latest || item.sequence > latest.sequence ? item : latest, null)
}

function currentEvidenceVersions(milestones) {
  const byId = new Map()
  for (const milestone of milestones) {
    for (const evidence of milestone.documentEvidence) {
      byId.set(evidence.version.evidenceVersionId, evidence.version)
    }
  }
  return [...byId.values()].filter((version) => version.isCurrent)
}
```

The real implementation must retain TypeScript types and also implement:

- review counts in `APPROVED`, `PENDING`, `REJECTED` display order;
- status priority `REJECTED > PENDING > all APPROVED`;
- task dedupe by `taskId`, later fact wins, earliest `dueDate`, then `internalDueDate`, then stable
  first appearance;
- document and lifecycle cards use the same global OPEN-task candidate; the fee card calls the same
  selector with only `lane === 'FEE'` milestones;
- latest confirmed center change by highest sequence with at least one changed axis;
- latest obligation by `obligationId`, then counts by `feeDomain` and currency; blank currency is
  “币种待确认”; no `Number(payableAmount)` or amount sum;
- FEE “latest” as deduplicated Chinese fee domain + obligation type, or “费用事实已更新”;
- all unknown codes use approved Chinese fallbacks.

The fee card always receives `footnote="服务费余额以客户账单页为准"`. No other card receives a
balance statement.

If `overlay.hasMore` is true, return `INCOMPLETE_HISTORY` before performing any
milestone-derived claim. `centerSnapshot` remains available.

- [ ] **Step 3: Replace the warning double-render with one stable projection**

Build a stable key from:

```ts
[kind, code, activityId ?? '', sourceObjectType ?? '', sourceObjectId ?? '', message].join('|')
```

Process activity warnings from accumulated milestones first. Then add only unmatched top-level
warnings whose `activityId` does not identify an accumulated milestone. Apply the existing
customer visibility predicate before inserting and preserve first occurrence. Render one warning
wrapper outside history, with the existing “当前快照警告” child group for unmatched top-level items
and one “活动局部警告” child group per activity. Do not render the same stable key in both groups.
When `hasMore`, label the wrapper “当前已加载警告”.

When accumulating a valid next page, preserve top-level warnings without duplicate loss:

```ts
warnings: mergeWarnings(current.warnings, nextPage.warnings),
```

Do not change cursor, revision, or milestone validation.

- [ ] **Step 4: Add the summary, disclosure, and responsive layout**

Template order:

1. existing meta;
2. `lifecycle-summary-grid` with document/lifecycle/fee cards;
3. deduplicated warning section;
4. one button with `data-testid="lifecycle-history-toggle"`, `aria-expanded`, and
   `aria-controls="lifecycle-history-details"`;
5. `v-if="historyExpanded"` detail region containing the existing grid, load-more error, and
   pagination unchanged.

Use `v-if`, not merely opacity or off-screen CSS, so collapsed detail contains no focusable child.
Toggling must not call `loadOverlay` or `loadMoreOverlay`.

CSS breakpoints:

```css
.lifecycle-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 1099px) and (min-width: 900px) {
  .lifecycle-summary-grid { gap: 10px; }
}

@media (max-width: 899px) {
  .lifecycle-summary-grid,
  .overlay-grid { grid-template-columns: 1fr; }
}
```

Remove the old 1100px rule that stacked the detailed grid prematurely; use the approved 900px
threshold for both summary and expanded history.

- [ ] **Step 5: Run GREEN**

Run the Task 3 command again with `PLAYWRIGHT_HTML_OUTPUT_DIR` changed from `focused-red` to
`focused-green`.

Expected: PASS. Specifically: one GET before any load-more click, three summary cards, one
disclosure, partial-history degradation, final summary refresh, warning dedupe, and no mutation.
The contract must also assert the fee card contains “服务费余额以客户账单页为准” and no card
contains a numeric customer balance.

## Task 5: Preserve Existing Detailed-Lane and V6 Contracts

**Files:**

- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`

- [ ] **Step 1: Update detailed-lane tests only at the visibility boundary**

After each case page loads, add:

```ts
await page.getByTestId('lifecycle-history-toggle').click()
await expect(page.getByTestId('lifecycle-history-details')).toBeVisible()
```

Keep every existing detailed fact assertion unchanged. This proves the old V6 content still exists
after one explicit user action.

- [ ] **Step 2: Update the three-page live overlay contract**

Before disclosure assert the three summary cards and incomplete-history truth. Click disclosure,
then retain the exact three request URLs, revision binding, 200/200/1 sequence pages, hidden gate
diagnostics, and no fulfilled-route assertions.

- [ ] **Step 3: Add one V6 parity helper**

Inside `demo-v6-ui-parity.live-backend.spec.ts`, define one local helper:

```ts
async function expandLifecycleHistory(page: Page): Promise<void> {
  const details = page.getByTestId('lifecycle-history-details')
  if (await details.count() === 0) {
    await page.getByTestId('lifecycle-history-toggle').click()
  }
  await expect(details).toBeVisible()
}
```

Call it immediately before the six existing detailed evidence/fee lane inspection groups. Do not add a
click when a stage reads only summary or another tab. Do not change actor, business input, expected
money, mutation bindings, stage numbering, or receipt logic.

- [ ] **Step 4: Run the focused compatibility suite**

Run:

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/compatibility" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-case-detail-three-lane.spec.ts \
  src/tests/v8-case-detail-overlay-cursor.spec.ts \
  src/tests/v8-case-detail-gates-warnings.spec.ts \
  src/tests/v8-overlay-center-lane.spec.ts \
  src/tests/v8-overlay-document-lane.spec.ts \
  src/tests/v8-overlay-fee-lane.spec.ts
```

Expected: PASS.

- [ ] **Step 5: Run the real backend overlay traversal once**

Run:

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/live-overlay" \
python3 scripts/run_v8_lifecycle_overlay_live_isolated.py
```

Expected: PASS with three stable pages and no unexpected application response or mutation.

- [ ] **Step 6: Commit the UI and compatibility tests**

Before staging, run the exact canonical `lint` evidence command frozen in Task 1. It must observe
the final uncommitted UI/test bytes and return rc 0. Also run `git diff --check` against the mapping
extraction commit range and record that rc in the later verification report.

```bash
git add \
  frontend/src/modules/cases/components/CaseLifecycleOverlay.vue \
  frontend/src/modules/cases/components/LifecycleSummaryCard.vue \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts
git commit -m "feat(cases): add current-first lifecycle summary"
```

## Task 6: Final Verification, One V6 Rehearsal, and Evidence Close

**Files:**

- Evidence only: `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/**`

- [ ] **Step 1: Run scoped static checks**

```bash
mkdir -p artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs
script -q artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/typecheck.log \
  npm --prefix frontend run typecheck
script -q artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/eslint.log \
  /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/components/CaseLifecycleOverlay.vue src/modules/cases/components/LifecycleSummaryCard.vue src/modules/cases/components/lifecycleOverlayDisplay.ts src/modules/cases/components/DocumentEvidenceLane.vue src/modules/cases/components/LifecycleCenterLane.vue src/modules/cases/components/FeeObligationLane.vue --max-warnings 0'
script -q artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/build.log \
  npm --prefix frontend run build
git diff --check HEAD~2..HEAD
```

Expected: all rc 0. BSD `script` propagates the child rc and retains the actual terminal output.
Do not run repo-wide backend pytest or broad unrelated Playwright.

- [ ] **Step 2: Run the V6 static UI contract**

```bash
script -q artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/v6-static-contract.log \
  node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
```

Expected: PASS; no output or a success result, rc 0.

- [ ] **Step 3: Run exactly one fresh strict V6 rehearsal**

The strict runner requires a completely clean candidate. The pre-existing untracked colleague guide
is outside this task and must not be absorbed. Before the rehearsal, verify it is the only status
entry, record its SHA-256, move that exact file to a `mktemp -d` parking directory, and install a
shell trap that restores it. If any other dirty path exists, stop instead of hiding it.

Create the artifact outside the repo and run:

```bash
set -euo pipefail
test "$(git status --porcelain=v1 -uall | wc -l | tr -d ' ')" = "1"
test "$(git status --porcelain=v1 -uall)" = "?? docs/postdemo/demo-v6-colleague-clone-start-guide.md"
FPMS_GUIDE_SHA="$(shasum -a 256 docs/postdemo/demo-v6-colleague-clone-start-guide.md | cut -d ' ' -f 1)"
FPMS_GUIDE_PARK="$(mktemp -d)"
mv docs/postdemo/demo-v6-colleague-clone-start-guide.md "$FPMS_GUIDE_PARK/"
trap 'mv "$FPMS_GUIDE_PARK/demo-v6-colleague-clone-start-guide.md" docs/postdemo/; rmdir "$FPMS_GUIDE_PARK"' EXIT
test -z "$(git status --porcelain=v1 -uall)"
FPMS_STRICT_ATTEMPT=1
FPMS_STRICT_ROOT="$(pwd)/artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01"
FPMS_SUMMARY_V6_ARTIFACT="$FPMS_STRICT_ROOT/strict-v6-attempt-$FPMS_STRICT_ATTEMPT"
test ! -e "$FPMS_SUMMARY_V6_ARTIFACT"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL \
  --strict-ui \
  --headless \
  --runs 1 \
  --artifact "$FPMS_SUMMARY_V6_ARTIFACT"
test -f "$FPMS_SUMMARY_V6_ARTIFACT/run1/strict-pass-receipt.json"
mv "$FPMS_SUMMARY_V6_ARTIFACT" "$FPMS_STRICT_ROOT/strict-v6-pass"
mv "$FPMS_GUIDE_PARK/demo-v6-colleague-clone-start-guide.md" docs/postdemo/
rmdir "$FPMS_GUIDE_PARK"
trap - EXIT
test "$FPMS_GUIDE_SHA" = "$(shasum -a 256 docs/postdemo/demo-v6-colleague-clone-start-guide.md | cut -d ' ' -f 1)"
```

Expected: rc 0 and `strict-v6-pass/run1/strict-pass-receipt.json`. Run once only. If attempt 1
fails, leave `strict-v6-attempt-1` intact, let the trap restore the guide, diagnose and commit the
first concrete summary/disclosure incompatibility, rerun only its affected targeted test, then
repeat the clean-candidate parking sequence with `FPMS_STRICT_ATTEMPT=2`. Attempt 2 writes to
`strict-v6-attempt-2`; only a successful attempt is renamed to `strict-v6-pass`. Never delete or
overwrite the failed attempt. No third full rehearsal is authorized, and external/governance noise
does not justify a retry.

- [ ] **Step 4: Obtain findings-only review before freezing the candidate**

Dispatch one independent reviewer against the current spec, task, source, tests, and actual command
results while controller state is still `IMPLEMENTING`. If it reports findings, fix only those
findings and rerun the affected focused checks. Continue until it reports ZERO FINDINGS; do not
create a formal review lease yet.

- [ ] **Step 5: Refresh task evidence and prepare the immutable review candidate**

Create `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/verification.md`
with `apply_patch`. Record every actual command from Tasks 2–6, its observed rc, pass/fail counts
where emitted, and the exact strict receipt path. Do not write PASS for a command that was not run.
The report must include the behavior-neutral mapping baseline/after checks, expected RED failure,
focused GREEN, compatibility suite, live traversal, typecheck, scoped ESLint, build, V6 static
contract, and strict rehearsal.

The canonical lint record already exists from immediately before the final implementation commit.
Now run the exact canonical `test` command frozen in Task 1; it hashes all final source/test bytes,
the verification report, strict PASS receipt, network/console error ledgers, and Playwright log.
Then run the exact canonical `scope` command. Write
`artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/summary.md` with the actual
focused/live/V6 commands and rc values. Then run:

```bash
./scripts/taskctl FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 prepare-review
./scripts/taskctl FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 review lease independent \
  --reviewer case-lifecycle-summary-independent
```

Expected: candidate fingerprint and generation 1 lease. Do not change source, tests, task, summary,
or scoped patch after this point.

- [ ] **Step 6: Bind the zero-finding review and submit the canonical report**

Independent reviewer must check:

- spec alignment and no new facts;
- `hasMore` degradation and no auto-pagination;
- evidence/task/warning dedupe;
- no float amount aggregation or balance;
- no customer gate or English status exposure;
- old detailed content and V6 business values unchanged;
- no new request on disclosure;
- responsive 3-column/1-column threshold.

Expected review: `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`, bound to the current patch.

The reviewer writes the unbound canonical report at:

```text
artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/review/independent_review.md
```

with fields:

```text
Reviewer-ID: case-lifecycle-summary-independent
Verdict: APPROVED
P0: 0
P1: 0
P2: 0
```

The leased reviewer identity submits it:

```bash
TASKCTL_ACTOR=case-lifecycle-summary-independent \
  ./scripts/taskctl FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 \
  review submit independent \
  --report artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/review/independent_review.md
```

The leased reviewer first confirms the candidate fingerprint corresponds to the same bytes reviewed
at ZERO FINDINGS, then submits the report. If the fingerprint or bytes differ, do not submit; report
the stale candidate rather than editing a prepared candidate in place.

- [ ] **Step 7: Close the atomic task**

```bash
./scripts/taskctl FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 close
./scripts/taskctl FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 doctor
git status --short --branch
```

Expected: terminal `PASS`; no implementation-task dirt. The pre-existing untracked colleague guide
may remain only if it is still the exact baseline external file.

## Stop Conditions

Stop the affected lane and report before expanding scope if any of these occur:

- an authoritative “current/latest/next” value requires a new API or auto-fetching all pages;
- a requested amount requires decimal aggregation or customer balance data;
- a task action must be inferred from lifecycle or fee status;
- warning truth requires exposing `CUSTOMER_DECISION_GATE`;
- implementation needs a store, schema, state-machine, permission, backend, or detailed-lane
  behavior change;
- a failing test is unrelated to the exact visibility/disclosure contract;
- the strict V6 rehearsal fails outside the changed case-detail summary/disclosure surface.

Do not absorb these into this task. Preserve the approved summary slice and create a separately
approved follow-up only if the user still wants the additional behavior.
