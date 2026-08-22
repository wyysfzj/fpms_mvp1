# Customer Demo Presentation Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep internal demo controls and decision diagnostics off the customer journey while showing the existing lifecycle facts in clear Simplified Chinese.

**Architecture:** Preserve all backend/API facts. Add one unlinked read-only input projection for the presenter, keep the existing mutation console reachable only by direct URL, and make the case lifecycle components a customer-safe projection through local display maps and warning filtering.

**Tech Stack:** Vue 3, TypeScript, Element Plus, Vue Router, Node source contracts, Playwright.

---

### Task 1: Freeze the customer-visible contract with RED tests

**Files:**
- Modify: `frontend/tests/demo-abc-contract.mjs`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`

- [ ] Change the demo source contract to require `/demo/inputs`, require `/demo/abc` to remain routable, and reject `ABC 演示台` or `/demo/abc` from `menu.ts`.
- [ ] Require the input page to use only `readDemoPreflight`, expose readiness/provenance/ten counts, and contain none of the create/lock/bill/payment/offset controls.
- [ ] Change center-lane expectations to Chinese labels and assert raw state/event codes and the source event ID are absent.
- [ ] Keep 29 decision gates in the mocked API response but require no customer-decision section, DG code, or customer-decision warning in the DOM; retain ordinary conflict/unverified warnings and zero writes.
- [ ] Change the cursor test to continue proving revision/cursor/milestone behavior while requiring the gate diagnostics to remain hidden and projection labels to be Chinese.
- [ ] Preserve real lifecycle-overlay API assertions for all decision gates while changing only its DOM assertions to require those internal diagnostics to be hidden.
- [ ] Change the four Integrated A customer-visible center-lane assertions to the Chinese display projection; leave its raw API/ledger assertions unchanged.
- [ ] Run the two focused commands from the story card and retain the expected failures against baseline `0a824db`.

### Task 2: Implement the minimum presentation boundary

**Files:**
- Modify: `frontend/src/constants/menu.ts`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/constants/labels.zh.ts`
- Create: `frontend/src/modules/demo/pages/DemoInputs.vue`
- Modify: `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- Modify: `frontend/src/modules/cases/components/LifecycleCenterLane.vue`

- [ ] Remove `demoAbcItem` and its two menu-group references; do not remove the `/demo/abc` route.
- [ ] Add the unlinked `/demo/inputs` route and Chinese route label.
- [ ] Implement `DemoInputs.vue` with one explicit read-only preflight action, provenance fields, `business_counts`, synthetic/customer-activation boundary text, and no mutation imports or buttons.
- [ ] Remove the decision-gate cards from `CaseLifecycleOverlay.vue`; filter only warnings whose kind or source object identifies a customer decision gate, while leaving other warnings unchanged.
- [ ] Add exhaustive display maps for the typed business/official/legal/verification states in `LifecycleCenterLane.vue`. Unknown values render `未识别状态`; raw event type and source event ID are not rendered.
- [ ] Run the focused tests until GREEN, then run frontend typecheck and scoped ESLint.

### Task 3: Align the customer runbook and verify the live screen

**Files:**
- Modify: `docs/postdemo/demo-lifecycle-customer-v5-runbook.md`

- [ ] Change Step 0 to `/demo/inputs` and state that it is a presenter-only preflight screen shown before customer operations.
- [ ] State that `/demo/abc` is an unshared presenter control surface; customer-visible verification uses normal case, fee draft, bill, payment and offset pages.
- [ ] In the existing running V5 environment, verify both navigation modes omit ABC, `/demo/inputs` is read-only, and the live case shows Chinese lifecycle facts without customer-decision diagnostics.
- [ ] Recheck the payment empty state by observing `/payments`, `/offsets`, `/clients`, and `/bills`; record rather than speculate if the non-reproducible transport cancellation returns.
- [ ] Commit the exact allowed-file scope once, then request independent High review of that commit.
