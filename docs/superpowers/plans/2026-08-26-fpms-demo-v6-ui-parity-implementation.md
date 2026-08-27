# FPMS Demo V6 HUMAN / CODEX UI 等价实施计划

> 执行时必须使用 `superpowers:executing-plans`、TDD 和 atomic evidence gate；严格按 ordinal
> 串行执行。任何 ordinal 不得吸收相邻修复。

**目标：** 保留现有 A 技术回归，并新增 B-HUMAN、B-CODEX 两条真实 UI-only 路径；两位操作者
从各自全新空业务库开始，通过相同正常页面输入同值、点击同类按钮，得到规范化相同的 11 阶段结果。

**批准设计：** `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`，exact commit
`5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`，独立复审 `APPROVED`。

**技术边界：** Vue 3 + TypeScript + Element Plus 正常页面；现有 FastAPI/SQLite/command endpoint；
Playwright 只在 STRICT_UI_TECHNICAL 路径驱动 UI，在 HUMAN/CODEX 路径只被动观察页面事件、网络和
截图。禁止 `APIRequestContext`、直接 HTTP/DB、`/demo/abc`、预造业务对象和内部 ID 抄写。

**不闭合：** 正式客户/官方来源激活、生产、安全加固、Docker V6 化、云部署、通用 recorder、
业务状态机/schema/migration 变更、release ref 推广。已知 migration-head 测试期望漂移只允许
Ordinal 00 修改一个测试常量；它不修改 migration graph 或运行时 schema。

## 最小架构与执行顺序

```text
00 migration-head test alignment
 -> 01 versioned contract
 -> 02 setup-only session
 -> 03 visible boundary + passive observer
 -> 04 lifecycle/OA normal UI (03..05)
 -> 05 grant evidence + normal UI (06)
 -> 06 fee normal UI (07..09)
 -> 07 billing normal UI (10)
 -> 08 strict UI journey + AST/runtime gates + receipt comparator (01..11)
 -> 09 frozen runbook/docs candidate + candidate-branch publish
 -> 10 HUMAN/CODEX fresh-run receipts against frozen SHA
 -> 11 read-only candidate close (release remains separate and last)
```

不建立通用工作流或第二套业务 client。已有 endpoint、wrapper、page 和 runner 能复用就原地窄幅扩展。
Tasks 02、08 共享 controller，Tasks 04–07 可能触碰同一 frontend API 文件，因此全部串行。

## 跨任务冻结合同

唯一合同为
`FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`，schema id
`fpms.demo-v6-ui-parity/v1`。每条 input/output 必须含 design 冻结的 stage、field、classification、
value rule、route、visible control/source selector、normalization、required；07–11 的每个权威断言均为
独立 required 字段。validator 拒绝缺项、多项、重复项、分类/locator 漂移和未授权差异。

每个实现任务 00–09 形成独立 candidate commit，独立 reviewer 绑定 exact commit/tree 后给出
`P0/P1/P2 = 0/0/0`。Acceptance gates 10–11 不改 repository bytes，始终绑定 Task 09 冻结的
candidate SHA/tree。每个 evidence root 至少含 `task.json`、`summary.md`、`git/diff.patch`、
`git/rev.txt`、`git/status.txt`、`commands.jsonl`、`review/HIGH_REVIEW.md`、`checksums.sha256`。

Task 00 开始前，本 exact plan commit 必须取得独立 `0/0/0` review，并由客户明确批准执行。
任何已接受实现 ordinal 的 literal rollback 为 `git revert --no-edit <exact-task-sha>`；禁止
destructive reset/checkout。若该 ordinal 创建了 disposable demo run，失败时保留证据；成功时也
只能按该 task 收据验证过的 exact run root 清理。

| Ordinal | Task path | Evidence root | Commit |
| --- | --- | --- | --- |
| 00 | `tasks/postdemo/FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00.md` | `artifacts/FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00/` | `git commit -m "test(migrations): align V6 expected head"` |
| 01 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01/` | `git commit -m "test(demo): freeze V6 UI parity contract"` |
| 02 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02/` | `git commit -m "feat(demo): add setup-only UI session"` |
| 03 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03/` | `git commit -m "feat(demo): expose synthetic UI session boundary"` |
| 04 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04/` | `git commit -m "feat(demo): close lifecycle UI inputs"` |
| 05 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05/` | `git commit -m "feat(demo): close grant UI inputs"` |
| 06 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06/` | `git commit -m "feat(demo): close fee UI inputs"` |
| 07 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07/` | `git commit -m "feat(demo): close billing UI inputs"` |
| 08 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08/` | `git commit -m "test(demo): prove V6 strict UI journey"` |
| 09 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-RUNBOOK-FREEZE-20260826-09.md` | `artifacts/FPMS-DEMO-V6-UI-PARITY-RUNBOOK-FREEZE-20260826-09/` | `git commit -m "docs(demo): freeze V6 UI parity runbook"` |
| 10 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10.md` | external immutable receipt roots | **NO COMMIT — bind Task 09 candidate** |
| 11 | `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CANDIDATE-CLOSE-20260826-11.md` | external immutable close root | **NO COMMIT — bind Task 09 candidate** |

Task 00 must PASS and receive exact-commit independent review before Task 01 starts. Tasks 10–11
task cards and comparator code are committed no later than Task 09; their execution cannot change
the candidate tree.

## Task 00 — Migration-head test alignment prerequisite

**Files:** modify only `backend/tests/test_v8_official_rate_book_schema.py`; create exact task card.

1. RED evidence is the current focused failure: the test constant expects
   `v8_w6_service_price_book_01` while `alembic heads` and the valid unique graph return
   `demo_v6_gov_payment_operation_01`.
2. GREEN changes only `CURRENT_HEAD` to `demo_v6_gov_payment_operation_01`; migration files,
   revision links and runtime code are forbidden.
3. Gate and literal commit:

```bash
(cd backend && /tmp/fpms-demo-python-20260817/bin/python -m alembic heads)
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q \
  backend/tests/test_v8_official_rate_book_schema.py
git diff --check
git add backend/tests/test_v8_official_rate_book_schema.py \
  tasks/postdemo/FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00.md
git commit -m "test(migrations): align V6 expected head"
```

Expected GREEN: exactly one Alembic head named `demo_v6_gov_payment_operation_01` and the focused
test file passes. Independent review must prove one-line product-test alignment and zero migration
diff. Rollback reverts this commit; Task 01 remains blocked.

## Task 01 — Versioned contract and validator

**Files:** create the JSON contract and
`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs`; create exact
task card. No product file.

1. RED: validator fixture variants prove one missing field, duplicate field, wrong classification,
   unknown difference and collapsed 07–11 assertion all fail.
2. GREEN: materialize the exact stage 01–11 inputs/outputs and the allowed-difference whitelist.
3. Gate:

```bash
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
git diff --check
git add FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01.md
git commit -m "test(demo): freeze V6 UI parity contract"
```

4. Expected RED is one named invalid fixture rejected per rule; GREEN is all positive contract rows
   accepted and every negative fixture rejected. Independent exact-commit review follows. Rollback
   removes only the contract and validator.

## Task 02 — Setup-only persistent UI session

**Files:** modify `scripts/run_demo_integrated_a_rehearsal.py`,
`backend/app/modules/fees/demo_service.py`, `backend/app/modules/fees/demo_service_schemas.py`;
create `backend/tests/test_demo_v6_ui_session.py` and task card.

1. RED: `ui-session` starts a unique run root/database, migrates and seeds only system/runtime
   sources, exposes candidate/run/bundle/authority identity, and leaves the complete business set 0.
   Default A CLI/output/two-run behavior must remain byte-contract compatible.
2. GREEN: add one narrow `--ui-session --actor HUMAN|CODEX --artifact <absolute>` branch using the
   existing bundle/env/credential/start/stop functions. It launches normal services and a headed
   browser, prints redacted credentials and pre-registers one passive finalize binding that can only
   write observer artifacts. It preserves the run on STOP/failure, and only cleans an exact validated
   run root after explicit successful finalization.
3. Extend the existing read-only preflight response only with run id, candidate commit/tree,
   authority SHA, contract version and complete business-table counts. Freeze the entire
   system/runtime-seed allowlist to exactly: `t_user`, `t_role`, `t_role_perm`, `t_user_role`,
   `t_doc_template`, `t_task_template`, `t_fee_rate_book`, `t_fee_rate`. Every table in
   `Base.metadata.tables` outside that exact allowlist is automatically business, including
   `T_GrantFeeTask` and every OfficialWorkPackage checklist/manifest/receipt child table; query each
   in sorted table-name order and fail if any count is nonzero. The backend test proves the derived
   key set equals `sorted(Base.metadata.tables - SYSTEM_RUNTIME_TABLE_ALLOWLIST)` so a future table
   cannot be silently classified as system/runtime. Task 03 parser requires exactly that complete
   derived key set.
4. Gate:

```bash
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q \
  backend/tests/test_demo_v6_ui_session.py backend/tests/test_demo_integrated_a_runner.py
/Users/cfcc/Library/Python/3.11/bin/ruff check \
  scripts/run_demo_integrated_a_rehearsal.py backend/app/modules/fees/demo_service.py \
  backend/app/modules/fees/demo_service_schemas.py backend/tests/test_demo_v6_ui_session.py
git diff --check
git add scripts/run_demo_integrated_a_rehearsal.py backend/app/modules/fees/demo_service.py \
  backend/app/modules/fees/demo_service_schemas.py backend/tests/test_demo_v6_ui_session.py \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02.md
git commit -m "feat(demo): add setup-only UI session"
```

5. Expected RED identifies the first missing count/session field; GREEN proves every count is zero,
   default A tests remain green and STOP preserves the exact run. Independent review binds the
   commit. Rollback restores the old CLI and preflight projection; A remains the fallback.

## Task 03 — Visible synthetic boundary and passive observer

**Files:** modify `frontend/src/api/http.ts`, `frontend/src/App.vue`,
`frontend/src/modules/demo/demo.contract.ts`, `frontend/src/modules/demo/pages/DemoInputs.vue`;
create `frontend/src/modules/demo/demoUiSession.ts`,
`frontend/src/components/demo/DemoBoundaryBanner.vue`,
`frontend/tests/demo-v6-ui-session-contract.mjs`, and task card.

1. RED: only a freshly validated `SYNTHETIC_TEST_ONLY` preflight with the exact complete Task 02
   count-key set activates the banner and observer;
   reload preserves the exact run/candidate/authority tuple; tuple drift or missing session disables
   all V6-only controls and records STOP.
2. GREEN: store the validated preflight tuple in `sessionStorage`; show the fixed Simplified Chinese
   boundary on every normal page. Install a local-demo-only passive observer around existing Axios:
   capture the preceding visible click/submit (route, role, label/testid, action id), method/path,
   normalized payload digest, status and console/network failures. It never issues, retries or
   changes a request and never stores auth secrets or raw personal fields.
   `/demo/inputs` also exposes `完成并导出本轮证据`, a non-business control that invokes the headed
   session's pre-registered finalize binding; it writes ledgers/screenshots to the external artifact
   root and performs no API call or business mutation.
3. Gate:

```bash
node frontend/tests/demo-v6-ui-session-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/api/http.ts src/App.vue src/modules/demo/demo.contract.ts \
  src/modules/demo/pages/DemoInputs.vue src/modules/demo/demoUiSession.ts \
  src/components/demo/DemoBoundaryBanner.vue)
git add frontend/src/api/http.ts frontend/src/App.vue frontend/src/modules/demo/demo.contract.ts \
  frontend/src/modules/demo/pages/DemoInputs.vue frontend/src/modules/demo/demoUiSession.ts \
  frontend/src/components/demo/DemoBoundaryBanner.vue \
  frontend/tests/demo-v6-ui-session-contract.mjs \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03.md
git commit -m "feat(demo): expose synthetic UI session boundary"
```

4. Expected RED names the missing exact-count parser or action correlation; GREEN accepts only the
   fresh bound session and passive matching requests. Independent review follows. Rollback disables
   only the local session boundary/observer.

## Task 04 — Normal lifecycle/OA inputs for stages 03–05

**Files:** modify `frontend/src/modules/cases/pages/FilingPreparation.vue`,
`frontend/src/modules/documents/pages/DocumentDetail.vue`,
`frontend/src/modules/documents/pages/OAReplyPackage.vue`,
`frontend/src/modules/officialWorkflows/components/ReceiptArchivePanel.vue`,
`frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`,
`frontend/src/api/officialWorkflows.ts`, `frontend/src/api/officialWorkflows.types.ts`;
create `frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue`,
`frontend/tests/demo-v6-lifecycle-ui-contract.mjs`, and task card.

1. RED: no raw attachment/document/internal ID input; current same-case approved evidence only;
   filing manual submission complete has visible timestamp/note; acceptance, preliminary start/pass,
   publication and substantive start use the current reviewed evidence; OA1/OA2 bind different
   visible reply documents and receipt attachments.
2. GREEN: add one visible `记录人工递交完成` action using the existing external-operation endpoint;
   replace receipt attachment-ID text input with a filename/role selector; add a focused document
   evidence action panel over existing lifecycle endpoints; add OA reply-document selector over
   existing `linkOaReplyDocument`. No backend lifecycle/service change.
3. Focused gates:

```bash
node frontend/tests/demo-v6-lifecycle-ui-contract.mjs
node frontend/tests/document-evidence-review-contract.mjs
node frontend/tests/oa-reply-checklist-actions.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/cases/pages/FilingPreparation.vue \
  src/modules/documents/pages/DocumentDetail.vue src/modules/documents/pages/OAReplyPackage.vue \
  src/modules/documents/components/DocumentLifecycleEvidenceActions.vue \
  src/modules/officialWorkflows/components/ReceiptArchivePanel.vue \
  src/api/documents.ts src/api/documents.types.ts src/api/officialWorkflows.ts \
  src/api/officialWorkflows.types.ts)
git add frontend/src/modules/cases/pages/FilingPreparation.vue \
  frontend/src/modules/documents/pages/DocumentDetail.vue \
  frontend/src/modules/documents/pages/OAReplyPackage.vue \
  frontend/src/modules/officialWorkflows/components/ReceiptArchivePanel.vue \
  frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue \
  frontend/src/api/documents.ts frontend/src/api/documents.types.ts \
  frontend/src/api/officialWorkflows.ts frontend/src/api/officialWorkflows.types.ts \
  frontend/tests/demo-v6-lifecycle-ui-contract.mjs \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04.md
git commit -m "feat(demo): close lifecycle UI inputs"
```

4. Expected RED is the first missing visible selector/action; GREEN proves the same-case reviewed
   evidence path and no raw ID control. Existing wrong-case/unreviewed/hash-drift backend tests
   remain GREEN. Independent review binds the commit. Rollback removes only the new normal UI seams.

## Task 05 — Normal grant input for stage 06

**Files:** modify `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`,
`frontend/src/api/grantFees.ts`, `frontend/src/api/grantFees.types.ts` and the Task 04 shared file
`frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue`; create
`frontend/tests/demo-v6-grant-ui-contract.mjs` and task card. Task 05 is serialized after Task 04
and is the only later owner of that shared component.

1. RED: the original and replacement grant notices can each be selected by visible title/role and
   confirmed only from the current same-case APPROVED evidence; the old task becomes read-only,
   current confirmed task exposes `标记等待客户`; superseded/unconfirmed tasks never do; PAY remains
   exactly once and existing correction/preview actions remain unchanged.
2. GREEN: extend the Task 04 evidence action panel with a grant-notice mode that calls the existing
   `/grant-fee-tasks/{task_id}/lifecycle/grant-notice` endpoint using the source-bound reviewed
   evidence version/hash. Render it from the current task row without exposing IDs. Also expose the
   existing `mark_waiting_client` action conditioned on `allowed_actions` and confirmed lineage.
   Do not add endpoint, state or customer-decision panel.
3. Gate:

```bash
node frontend/tests/demo-v6-grant-ui-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/grantFees/pages/GrantFeeTaskList.vue \
  src/modules/documents/components/DocumentLifecycleEvidenceActions.vue \
  src/api/grantFees.ts src/api/grantFees.types.ts)
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q \
  backend/tests/test_demo_integrated_grant.py backend/tests/test_demo_v6_grant_official_fee.py \
  backend/tests/test_v8_grant_notice_lifecycle_api.py \
  backend/tests/test_v8_grant_evidence_accepted_dispatch.py
git add frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue \
  frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue \
  frontend/src/api/grantFees.ts frontend/src/api/grantFees.types.ts \
  frontend/tests/demo-v6-grant-ui-contract.mjs \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05.md
git commit -m "feat(demo): close grant UI inputs"
```

4. Expected RED identifies the missing reviewed-notice action before the waiting-client action;
   GREEN proves original/replacement lineage and one current PAY. Independent review follows.
   Rollback reverts only the grant mode and one state button/handler.

## Task 06 — Normal fee inputs for stages 07–09

**Files:** modify `frontend/src/modules/cases/components/CaseFeesTab.vue`,
`frontend/src/modules/annuity/pages/PayListDetail.vue`,
`frontend/src/modules/annuity/pages/GovPaymentCreate.vue`,
`frontend/src/modules/demo/demo.api.ts`; create
`frontend/tests/demo-v6-fee-ui-parity-contract.mjs` and task card.

1. RED: stage 07 preview/confirm is clicked in existing grant UI; case fees exposes V6-only
   `生成服务费义务`; PAY/draft/adjust/lock stay on existing normal pages; GovPayment success offers
   `登记下一行` and `返回当前清单` without internal IDs.
2. GREEN: call the existing GET-first `createDemoServiceObligation` only from the visible case-fees
   action under the validated session tuple; add navigation aids only. Do not change fee endpoint,
   source, amount, adjustment, lock or GovPayment semantics.
3. Gate:

```bash
node frontend/tests/demo-v6-fee-ui-parity-contract.mjs
node frontend/tests/demo-abc-command-reconcile.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/cases/components/CaseFeesTab.vue \
  src/modules/annuity/pages/PayListDetail.vue src/modules/annuity/pages/GovPaymentCreate.vue \
  src/modules/demo/demo.api.ts)
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q \
  backend/tests/test_demo_v6_fee_ui_contract.py backend/tests/test_demo_v6_gov_payment.py \
  backend/tests/test_demo_v6_grant_official_fee.py
git add frontend/src/modules/cases/components/CaseFeesTab.vue \
  frontend/src/modules/annuity/pages/PayListDetail.vue \
  frontend/src/modules/annuity/pages/GovPaymentCreate.vue \
  frontend/src/modules/demo/demo.api.ts frontend/tests/demo-v6-fee-ui-parity-contract.mjs \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEES-20260826-06.md
git commit -m "feat(demo): close fee UI inputs"
```

4. Expected RED identifies the missing case-fees action/navigation; GREEN preserves existing
   endpoint/replay results. Independent review follows. Rollback removes the one fee action and
   navigation aids.

## Task 07 — Normal billing inputs for stage 10

**Files:** modify `frontend/src/modules/billing/pages/BillCreate.vue`,
`frontend/src/modules/billing/pages/PaymentCreate.vue`,
`frontend/src/modules/billing/pages/PaymentList.vue`, `frontend/src/api/billing.ts`,
`frontend/src/modules/demo/demo.api.ts`, `frontend/src/modules/demo/demo.contract.ts`;
create `frontend/tests/demo-v6-billing-ui-parity-contract.mjs` and task card.

1. RED: SERVICE draft is visibly identified; bill no/date/due date are visible; payment amount,
   pay no/date, `BANK_TRANSFER`, bank ref and remark persist; offset date is visible. First
   1,200.00 offset yields `PARTIALLY_SETTLED`/600.00; only refreshed visible balance supplies the
   second 600.00; final state is `SETTLED`/0.00.
2. GREEN: under the validated session tuple, normal forms use narrow extensions of existing
   `createDemoBill`, `createDemoBankReceipt` and `createDemoFullOffset`. Extend payment wrapper to
   accept the visible amount; extend parsers for partial/final states. Standard non-V6 endpoints and
   form behavior remain unchanged.
3. Focused recovery RED/GREEN: commit-drop GET-first reconcile, exact replay same object and payload
   drift 409/no-write for bill/payment/offset; no client-side blind retry.
4. Gate:

```bash
node frontend/tests/demo-v6-billing-ui-parity-contract.mjs
node frontend/tests/demo-abc-command-reconcile.mjs
node frontend/tests/demo-abc-finance-decoder.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/billing/pages/BillCreate.vue \
  src/modules/billing/pages/PaymentCreate.vue src/modules/billing/pages/PaymentList.vue \
  src/api/billing.ts src/modules/demo/demo.api.ts src/modules/demo/demo.contract.ts)
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q \
  backend/tests/test_demo_abc_unique_ar_bill.py backend/tests/test_demo_abc_payment_offset.py
git add frontend/src/modules/billing/pages/BillCreate.vue \
  frontend/src/modules/billing/pages/PaymentCreate.vue \
  frontend/src/modules/billing/pages/PaymentList.vue frontend/src/api/billing.ts \
  frontend/src/modules/demo/demo.api.ts frontend/src/modules/demo/demo.contract.ts \
  frontend/tests/demo-v6-billing-ui-parity-contract.mjs \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-BILLING-20260826-07.md
git commit -m "feat(demo): close billing UI inputs"
```

5. Expected RED is the first missing visible V6 field/partial parser; GREEN proves both 1,200/600
   states and recovery negatives. Independent review follows. Rollback restores standard forms;
   persisted finance objects require no migration rollback because tests use disposable run roots.

## Task 08 — Strict UI-only 01–11 journey and anti-bypass gates

**Files:** create
`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`,
`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-static-contract.mjs`;
modify `scripts/run_demo_integrated_a_rehearsal.py`,
`backend/tests/test_demo_v6_ui_session.py`; create `scripts/compare_demo_v6_ui_receipts.py`,
`backend/tests/test_demo_v6_ui_receipt_comparator.py`, exact Task 08 card and the read-only
acceptance-gate task cards for Tasks 10–11.

1. RED AST gate traverses the full transitive import closure and rejects request fixture,
   `APIRequestContext`, `page.request`, Node/axios/fetch clients, SQL/ORM/backend scripts,
   `evaluate`/dynamic injection, mocks and `/demo/abc`.
2. GREEN journey uses only `page.goto`, visible locators, `fill/select/click/setInputFiles` and passive
   `waitForResponse`. Each POST/PUT/PATCH/DELETE must match one observer `action_id`; otherwise fail.
3. Emit `ui-input-ledger.json`, `ui-output-ledger.json`, `ui-mutation-ledger.json`, screenshots,
   network/console arrays and strict pass receipt. Enforce the complete design section 7 matrix,
   including preview transaction no-write table set, adjustment snapshots/links/header states,
   GOV/SERVICE identities/equalities and exactly two Payment/Offset objects.
4. Receipt comparator RED/GREEN: reject actor reuse, same run/database, candidate/contract/bundle
   drift, missing/extra field, non-whitelisted difference, missing screenshot/action correlation and
   any network/console error; accept only one HUMAN plus one different-account CODEX receipt.
5. A remains separately runnable and unchanged. Gate:

```bash
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-static-contract.mjs
/tmp/fpms-demo-python-20260817/bin/python -m pytest -q \
  backend/tests/test_demo_v6_ui_session.py backend/tests/test_demo_v6_ui_receipt_comparator.py \
  backend/tests/test_demo_integrated_a_runner.py
python3 scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL --strict-ui --runs 1 --headless \
  --artifact /tmp/fpms-demo-v6-strict-ui-task08
git add FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-static-contract.mjs \
  scripts/run_demo_integrated_a_rehearsal.py scripts/compare_demo_v6_ui_receipts.py \
  backend/tests/test_demo_v6_ui_session.py backend/tests/test_demo_v6_ui_receipt_comparator.py \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08.md \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10.md \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CANDIDATE-CLOSE-20260826-11.md
git commit -m "test(demo): prove V6 strict UI journey"
```

6. Expected RED is the first forbidden import/unassociated mutation or comparator mismatch; GREEN
   is one complete strict receipt plus all negative fixtures rejected. Remove only the verified temp
   root, then independent review. Rollback removes strict lane B/comparator and leaves A available.

## Task 09 — Freeze Runbook/docs and immutable candidate

**Files:** update only `README.md`, `docs/postdemo/demo-lifecycle-customer-v6.html`,
`docs/postdemo/demo-lifecycle-customer-v6-runbook.md`,
`docs/postdemo/demo-lifecycle-customer-v6-seed-data.md`,
`docs/postdemo/demo-v6-clone-deploy-handoff.md`; create Task 09 card. No actor receipt is generated
or committed here.

1. STOP until the owner of `.worktrees/demo-abc-e2e-20260815` has committed the five exact doc paths
   to a clean, independently reviewed source commit and released ownership. Record that source SHA in
   the Task 09 card. Use `git cherry-pick --no-commit <source-sha>`; any conflict stops the task.
2. RED is a docs contract check proving the imported Runbook still describes hybrid API writes or
   lacks `fpms.demo-v6-ui-parity/v1`, the setup-only command, UI-only stop rules and actor receipt
   procedure. GREEN updates the docs to the exact V6 lifecycle order and classifies every field as
   EXPLICIT_INPUT/SOURCE_BOUND/APP_GENERATED.
3. Include manual and another-Codex commands, normal UI routes, passive observer/finalize control,
   expected visible result, validation, fact boundary and STOP condition for every stage. Generic
   Docker remains explicitly unsupported; the canonical local session path is the handoff.
4. Gate, commit, exact-commit independent review, then publish only a candidate branch:

```bash
python3 scripts/check_customer_demo_lifecycle_v6.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
git diff --check
git add README.md docs/postdemo/demo-lifecycle-customer-v6.html \
  docs/postdemo/demo-lifecycle-customer-v6-runbook.md \
  docs/postdemo/demo-lifecycle-customer-v6-seed-data.md \
  docs/postdemo/demo-v6-clone-deploy-handoff.md \
  tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-RUNBOOK-FREEZE-20260826-09.md
git commit -m "docs(demo): freeze V6 UI parity runbook"
git status --short --branch
git push origin HEAD:refs/heads/codex/demo-v6-ui-parity-candidate-20260826
```

Expected GREEN: clean Task 09 candidate SHA/tree, remote candidate branch resolves to exactly that
SHA, and all docs checks pass. The push occurs only after exact-commit `0/0/0` review; it is not a
release ref. From this point through Task 11 no tracked or untracked bytes may be added to the
candidate clone. Rollback deletes only the remote candidate branch and reverts Task 09; actor runs
must not begin after rollback. Literal remote rollback is
`git push origin --delete codex/demo-v6-ui-parity-candidate-20260826`, followed by the global exact
Task 09 `git revert` command.

## Acceptance Gate 10 — Independent HUMAN and CODEX receipts

**Repository writes:** none. Task cards and comparator were already committed by Task 08. Each actor
uses a different clean clone of the remote Task 09 candidate and an absolute receipt root outside the
clone. The current Codex account cannot substitute for the independent CODEX actor.

1. Each actor performs fresh clone/install and starts the passive headed session. The browser
   observer may listen, screenshot and finalize but may not click/fill or issue/retry a mutation.
   The actor ends the run through the visible non-business `完成并导出本轮证据` control.
2. Exact commands, with actor-specific roots and no shared database/run id:

```bash
git clone https://github.com/wyysfzj/fpms_mvp1.git "$ACTOR_CLONE"
git -C "$ACTOR_CLONE" checkout --detach "$CANDIDATE_SHA"
cd "$ACTOR_CLONE/backend" && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
cd "$ACTOR_CLONE/frontend" && npm ci
cd "$ACTOR_CLONE/FPMS_Automation_Skeleton_Pack/playwright_ts" && npm ci && npx playwright install chromium
cd "$ACTOR_CLONE" && backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --ui-session --actor HUMAN \
  --artifact "$HUMAN_RECEIPT_ROOT"
cd "$ACTOR_CLONE" && backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --ui-session --actor CODEX \
  --artifact "$CODEX_RECEIPT_ROOT"
```

The HUMAN and CODEX commands run in different clones/machines/accounts; the block shows the common
syntax, not permission to execute both from one actor.

3. Compare only after both report PASS:

```bash
mkdir -p "$ACTOR_ACCEPTANCE_ROOT"
CANDIDATE_JSON="$ACTOR_ACCEPTANCE_ROOT/candidate.json"
test -z "$(git -C "$ACTOR_CLONE" status --porcelain)"
CANDIDATE_TREE="$(git -C "$ACTOR_CLONE" rev-parse 'HEAD^{tree}')"
printf '{"commit":"%s","tree":"%s","status":"CLEAN"}\n' \
  "$CANDIDATE_SHA" "$CANDIDATE_TREE" > "$CANDIDATE_JSON"
backend/.venv/bin/python scripts/compare_demo_v6_ui_receipts.py \
  --candidate "$CANDIDATE_JSON" \
  --human "$HUMAN_RECEIPT_ROOT/pass-receipt.json" \
  --codex "$CODEX_RECEIPT_ROOT/pass-receipt.json" \
  --output "$ACTOR_ACCEPTANCE_ROOT/comparison.json"
```

Expected GREEN: different actor identity, run id, run root and database; same candidate/tree,
contract v1 and bundle/authority digests; equal normalized input/output; complete action/mutation /
screenshot ledgers; network/console empty. Independent PROTECTED reviewer binds both immutable roots
and comparator output. On STOP/failure, preserve the exact root and return to the first failed
implementation ordinal; do not change candidate bytes or manufacture a replacement receipt.

## Acceptance Gate 11 — Fresh-clone candidate close; release remains separate

**Repository writes:** none. One independent monitor uses a third clean clone of the exact Task 09
candidate. It must not amend docs, task cards or evidence into the candidate.

```bash
git clone https://github.com/wyysfzj/fpms_mvp1.git "$FINAL_CLONE"
git -C "$FINAL_CLONE" checkout --detach "$CANDIDATE_SHA"
test "$(git -C "$FINAL_CLONE" rev-parse HEAD)" = "$CANDIDATE_SHA"
test -z "$(git -C "$FINAL_CLONE" status --porcelain)"

cd "$FINAL_CLONE/backend"
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/alembic heads
.venv/bin/alembic upgrade head
.venv/bin/pytest -q tests/test_v8_official_rate_book_schema.py \
  tests/test_demo_v6_ui_session.py tests/test_demo_v6_ui_receipt_comparator.py \
  tests/test_demo_v6_grant_official_fee.py tests/test_demo_v6_gov_payment.py \
  tests/test_demo_abc_unique_ar_bill.py tests/test_demo_abc_payment_offset.py \
  tests/test_demo_integrated_a_runner.py

cd "$FINAL_CLONE/frontend"
npm ci
npm run typecheck
node tests/demo-v6-ui-session-contract.mjs
node tests/demo-v6-lifecycle-ui-contract.mjs
node tests/demo-v6-grant-ui-contract.mjs
node tests/demo-v6-fee-ui-parity-contract.mjs
node tests/demo-v6-billing-ui-parity-contract.mjs

cd "$FINAL_CLONE/FPMS_Automation_Skeleton_Pack/playwright_ts"
npm ci
npx playwright install chromium
node src/tests/demo-v6-ui-parity-contract.mjs
node src/tests/demo-v6-ui-parity-static-contract.mjs

cd "$FINAL_CLONE"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL --runs 2 --headless --artifact "$FINAL_ROOT/a-two-runs"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL --strict-ui --runs 1 --headless \
  --artifact "$FINAL_ROOT/strict-run-1"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL --strict-ui --runs 1 --headless \
  --artifact "$FINAL_ROOT/strict-run-2"
backend/.venv/bin/python scripts/compare_demo_v6_ui_receipts.py \
  --candidate "$CANDIDATE_JSON" \
  --human "$HUMAN_RECEIPT_ROOT/pass-receipt.json" \
  --codex "$CODEX_RECEIPT_ROOT/pass-receipt.json" \
  --output "$FINAL_ROOT/actor-comparison.json"
python3 scripts/check_customer_demo_lifecycle_v6.py
test -z "$(git status --porcelain)"
```

Expected GREEN: unique Alembic head `demo_v6_gov_payment_operation_01`; every named command exits 0;
A 2/2 and strict UI 2/2 pass with distinct runs/databases and empty network/console arrays; actor
comparison passes; clone remains clean. Independent final PROTECTED review binds the candidate SHA,
all task reviews, external receipt checksums and close output with `P0/P1/P2 = 0/0/0`.

Do **not** promote a release ref here. Remote release/merge requires a later exact release task,
explicit authority, final release gate and rollback command; release remains last.

## Global stop conditions

Stop the affected task on any unapproved backend/schema/state change, source/amount drift, raw
internal-ID field, hidden write route, direct business API/DB use, observer-originated mutation,
first-load Network Error, console error, English new status, non-empty fresh database, reused run
root, stale candidate, missing independent actor receipt or failed independent review. Fix only the
first failing owner and rerun that ordinal; never broaden the task to adjacent cleanup.
