# FPMS Customer Demo Lifecycle V5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one standalone customer-facing lifecycle HTML successor that preserves the previous demo themes and visibly explains the recent evidence, two-OA, grant-source, SERVICE billing, payment, and offset improvements.

**Architecture:** This is one atomic HTML task, not a product feature tranche. It adds one self-contained HTML/CSS page and one small Python standard-library checker; the V3 reference page remains byte-identical and no runtime code or external asset is involved. Execution starts only after the governance activation preflight is genuinely PASS.

**Tech Stack:** Static HTML5, inline CSS, Python 3 standard library, local browser rendering.

---

## File Map

- Create `tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01.md`: exact atomic execution contract and non-closure.
- Create `docs/postdemo/demo-lifecycle-customer-v5.html`: complete customer-facing lifecycle page.
- Create `scripts/check_customer_demo_lifecycle_v5.py`: deterministic content, safety-boundary, immutability, and self-containment checks.
- Create `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/**`: RED/GREEN logs, render evidence, scoped patch, review, and receipt.
- Do not modify `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`.

## Shared Ownership and Dependency Boundary

- One owner performs the entire task; there are no parallel code lanes.
- The HTML, checker, task file, and evidence bundle are the only allowed writes.
- The task depends on `docs/superpowers/specs/2026-08-22-fpms-customer-demo-lifecycle-v5-design.md`.
- Governance activation is an external prerequisite. If its terminal PASS receipt is absent or
  does not bind the installed `AGENTS.md` and manifest bytes, stop with `BLOCKED`; do not repair
  governance inside this task.

### Task 1: Implement and verify the Lifecycle V5 successor

**Files:**

- Create: `tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01.md`
- Create: `docs/postdemo/demo-lifecycle-customer-v5.html`
- Create: `scripts/check_customer_demo_lifecycle_v5.py`
- Evidence: `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/**`
- Read only: `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`
- Read only: `docs/superpowers/specs/2026-08-22-fpms-customer-demo-lifecycle-v5-design.md`

- [ ] **Step 1: Run the governance activation preflight**

Run:

```bash
./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 doctor
```

Expected: terminal state `PASS`, with a receipt binding the installed `AGENTS.md` and
`docs/agents/manifest.json`. If absent or non-PASS, record the result and stop before creating
the implementation task or HTML.

- [ ] **Step 2: Materialize the single atomic HTML task**

Create the task file with:

- exact closure: one new static customer lifecycle page plus its checker;
- explicit non-closure: no V3 edit, runtime code, schema, customer bundle activation,
  official-fee/annuity calculation, deployment, production, product, or release claim;
- allowlist limited to the task, HTML, checker, and artifact tree;
- remaining follow-up IDs: `None`;
- required RED, test, lint, scope, visual/print, independent-review, task-gate, and evidence steps.

Validate:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01.md
```

Expected: `Atomic task check PASS`.

- [ ] **Step 3: Start the v2 task and capture scope before HTML/checker edits**

Run:

```bash
./scripts/taskctl FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 start --task-file tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01.md
```

Expected: v2 state is `IMPLEMENTING`, the task/allowlist is bound, and the exact tracked and
untracked baseline is captured by the repository scope producer.

- [ ] **Step 4: Write the failing checker first**

Create `scripts/check_customer_demo_lifecycle_v5.py` with Python standard-library modules only.
Freeze these core values:

```python
EXPECTED_V3_SHA256 = "2feab06c4399811dae7bed1a10f3d2f983435b00a24a8faa77402d91e0d547b8"
EXPECTED_STAGES = [
    ("01", "客户与案件"),
    ("02", "文件与递交准备"),
    ("03", "受理与审查"),
    ("04", "第一轮 OA"),
    ("05", "第二轮 OA"),
    ("06", "授权登记准备"),
    ("07", "服务费草单"),
    ("08", "客户账单与回款"),
    ("09", "后续运维边界"),
]
EXPECTED_STAGE_FRAGMENTS = {
    "01": ["同一客户", "同一案件", "零预置业务对象"],
    "02": ["递交准备不等于官方递交", "Bundle classification/ID/version/manifest hash", "template code/file hash"],
    "03": ["已复核证据", "60 类官文目录", "可执行", "仅参考"],
    "04": ["确认期限", "OA 答复包", "任务保持开放", "正确回执", "错案/错来源回执零写入"],
    "05": ["独立通知", "独立期限", "独立答复包", "独立任务", "独立回执"],
    "06": ["授权登记处理中", "不表示专利已生效", "来源替换", "旧任务不可修改", "当前授权任务 PAY", "不生成官费金额或草单"],
    "07": ["SERVICE", "SERVICE 义务 PAY", "锁定草单", "官费未配置", "rate item code", "source ref", "source version", "source SHA-256"],
    "08": ["唯一 AR 账单", "银行回款", "核销", "已结清", "余额 0", "已全额核销", "未核销 0"],
    "09": ["官费", "年费", "正式客户模板", "待配置", "未在本次演示中执行"],
}
REQUIRED_BOUNDARIES = [
    "本地技术演示",
    "虚构演示数据",
    "官费未配置不写入",
    "待配置",
    "未在本次演示中执行",
    "合成测试输入（SYNTHETIC_TEST_ONLY，非客户授权）",
]
REQUIRED_NONCLAIMS = [
    "递交准备不等于官方递交",
    "授权登记处理中，不表示专利已生效",
    "官费与年费未配置，不写入任何金额或完成状态",
    "本页面不代表产品、生产或发布批准",
]
REQUIRED_RECENT_CHANGES = [
    "模板版本、来源和哈希可见",
    "60 类官文目录",
    "错案/错来源回执零写入",
    "两轮 OA 完整隔离",
    "来源替换",
    "服务费来源可见，官费保持待配置",
    "唯一 AR 账单",
    "客户回款",
    "核销",
]
EXPECTED_LANES = ["案件状态", "文件与证据", "客户财务"]
EXPECTED_DELTAS = [
    ("页面和宽泛阶段可以展示", "证据、期限、任务与工作包形成可追踪链"),
    ("故事以单轮 OA 为主", "两轮 OA 各自保留独立身份与回执"),
    ("错误或歧义操作难以解释", "错来源回执与过期任务拒绝且不写业务数据"),
    ("费用示例容易被理解为固定真值", "服务费显示来源，未知官费保持待配置"),
    ("财务流程停在草单附近", "锁定草单、唯一账单、银行回款与核销闭环"),
]
EXPECTED_PRESENTER_ORDER = [
    "客户/案件和递交准备",
    "递交回执、受理和审查证据",
    "第一轮 OA",
    "第二轮 OA",
    "授权来源替换和当前任务指示",
    "服务费草单、账单、回款和核销",
    "官费、年费和正式模板待配置边界",
]
FORBIDDEN_POSITIVE_CLAIMS = [
    "已经完成官方递交",
    "已经获得生效专利权",
    "官费已经缴纳",
    "年费维护已经完成",
    "生产已就绪",
    "产品已发布",
]
```

Use `html.parser.HTMLParser` to assert:

- exact section order: hero, overview, nine stages, three traceability lanes, five-row delta,
  seven-step presenter strip, and scope boundary;
- exactly nine ordered `article.stage-card[data-stage]` elements, each containing nonempty
  `.stage-action`, `.stage-result`, `.stage-boundary`, and `.stage-highlight` containers and
  the design-frozen text fragments for that stage;
- exactly three lanes, the exact five `EXPECTED_DELTAS` pairs, and the exact seven-item
  `EXPECTED_PRESENTER_ORDER` sequence;
- no script element, external source, stylesheet, font, image, or network URL;
- stage 02 and stage 07 each contain one `.synthetic-value` wrapper holding the displayed value
  and its child `.synthetic-label` with the exact non-customer-authorized label;
- stage 06 distinguishes current grant-task `PAY` from stage-07 SERVICE-obligation `PAY` and
  says the grant-task instruction creates no official-fee amount or draft;
- stage 09 contains no currency symbol, `CNY`, or numeric `元` amount, and no fixed
  official-fee/annuity amount appears anywhere outside the labelled stage-07 synthetic wrapper;
- visible text contains every required non-claim and none of `FORBIDDEN_POSITIVE_CLAIMS`;
- a custom non-void tag stack rejects unexpected closing tags and unclosed elements, while the
  browser render remains the conformance check for CSS/layout;
- the V3 SHA-256 remains exact.

Record the RED:

```bash
./scripts/evidence_run.sh FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 red python3 scripts/check_customer_demo_lifecycle_v5.py
```

Expected: nonzero because the V5 HTML does not yet exist.

The checker also exposes `--self-test`. After the HTML exists, it mutates the in-memory document
to remove/swap a stage, replace a delta pair, move a synthetic label outside its value wrapper,
insert a fixed stage-09 fee, insert a script/external URL, insert a positive false claim, and
unbalance a tag. Every mutation must be rejected; a surviving mutation makes `--self-test`
return nonzero.

- [ ] **Step 5: Implement the minimal standalone HTML/CSS page**

Create `docs/postdemo/demo-lifecycle-customer-v5.html` with this structure:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FPMS 客户全流程演示 V5</title>
    <style>/* self-contained responsive and print CSS */</style>
  </head>
  <body>
    <header class="hero" data-section="hero">...</header>
    <main>
      <section class="journey-overview" data-section="overview">...</section>
      <section class="stage-grid" data-section="stages"><!-- nine ordered stage cards; each has four field containers --></section>
      <section class="traceability-lanes" data-section="lanes">...</section>
      <section class="recent-delta" data-section="delta"><!-- five exact delta rows --></section>
      <section class="presenter-strip" data-section="presenter">...</section>
      <section class="scope-boundary" data-section="boundary">...</section>
    </main>
  </body>
</html>
```

Content rules:

- Copy the approved design wording and non-claims, not memory or V3 fee values.
- Use one customer and one case as the uninterrupted visual story.
- Keep bundle, template, and rate provenance in separate accepted groups.
- Put the exact synthetic label beside the demo template and SERVICE amount.
- Use `最近新增` only for accepted changes.
- Keep official fees, annuity, and formal customer templates in stage 09 as `待配置` and
  `未在本次演示中执行`.
- Use HTML/CSS only; no JavaScript or external dependency.
- Add responsive CSS for 1440 px and 390 px widths plus `@media print`.

- [ ] **Step 6: Run deterministic GREEN and scoped checks**

Run:

```bash
./scripts/evidence_run.sh FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 test python3 scripts/check_customer_demo_lifecycle_v5.py
./scripts/evidence_run.sh FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 checker_sensitivity python3 scripts/check_customer_demo_lifecycle_v5.py --self-test
./scripts/evidence_run.sh FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 lint python3 -m py_compile scripts/check_customer_demo_lifecycle_v5.py
./scripts/evidence_run.sh FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 diff_check git diff --check -- tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01.md docs/postdemo/demo-lifecycle-customer-v5.html scripts/check_customer_demo_lifecycle_v5.py
./scripts/evidence_run.sh FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 scope python3 scripts/evidence_scope.py finalize FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01
```

Expected: checker and mutation sensitivity print PASS; compilation and diff checks return 0; the
canonical scope producer captures tracked and untracked allowlist changes, rejects every outside
path, and writes the baseline-subtracted scoped patch.

- [ ] **Step 7: Render desktop, narrow, and print output**

Serve only `docs/postdemo` on loopback:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/postdemo
```

Create the visual evidence directory, then use the already-installed Playwright CLI with exact
viewport sizes and `--full-page`:

```bash
mkdir -p artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/visual
FPMS_Automation_Skeleton_Pack/playwright_ts/node_modules/.bin/playwright screenshot --browser chromium --viewport-size "1440,1000" --full-page http://127.0.0.1:8765/demo-lifecycle-customer-v5.html artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/visual/desktop-1440.png
FPMS_Automation_Skeleton_Pack/playwright_ts/node_modules/.bin/playwright screenshot --browser chromium --viewport-size "390,844" --full-page http://127.0.0.1:8765/demo-lifecycle-customer-v5.html artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/visual/mobile-390.png
FPMS_Automation_Skeleton_Pack/playwright_ts/node_modules/.bin/playwright pdf --browser chromium --paper-format A4 http://127.0.0.1:8765/demo-lifecycle-customer-v5.html artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/visual/print.pdf
```

Capture and retain:

- `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/visual/desktop-1440.png`;
- `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/visual/mobile-390.png`;
- `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/visual/print.pdf`.

Record the exact viewport sizes, device scale factor 1, full-page image dimensions, and file
SHA-256s. Inspect the complete top-to-bottom page in both PNGs and every PDF page for ordered
stages, Simplified Chinese, recent-change badges, point-of-use labels, and stage 09. In the same
Chromium build, assert at both viewport widths that `document.documentElement.scrollWidth <=
document.documentElement.clientWidth` and every stage-card bounding box stays within the viewport.
Stop the server and prove port 8765 has no listener.

- [ ] **Step 8: Commit the exact candidate**

Run:

```bash
git add -- tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01.md docs/postdemo/demo-lifecycle-customer-v5.html scripts/check_customer_demo_lifecycle_v5.py
git commit -m "docs: add customer demo lifecycle v5"
```

Record the commit, tree, three source hashes, V3 hash, and clean status in the evidence summary.

- [ ] **Step 9: Obtain independent High review**

The reviewer binds the exact candidate commit/tree and inspects the HTML and all render artifacts.
Review covers old-theme/new-change coverage, lifecycle/lineage/fee truth, synthetic labels,
provenance grouping, visual quality, checker sensitivity, V3 immutability, and three-file scope.

Freeze the candidate and submit the independent review through the active controller:

```bash
./scripts/taskctl FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 prepare-review
./scripts/taskctl FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 review lease independent --reviewer lifecycle-v5-high-reviewer
./scripts/taskctl FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 review submit independent --report artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01/review/independent.md
```

Acceptance requires:

```text
Verdict: APPROVED
P0: 0
P1: 0
P2: 0
```

Any finding returns only to the affected step; do not redesign or absorb adjacent work.

- [ ] **Step 10: Finalize evidence and report the narrow result**

After the accepted independent review, execute the controller's serialized close:

```bash
./scripts/taskctl FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 close
./scripts/taskctl FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01 doctor
```

Expected: terminal state `PASS`, task and atomic gates have returned 0, the reviewed scoped patch
is unchanged, exact source scope is clean, and no listener remains.

Final claim: only the standalone customer Lifecycle V5 documentation artifact is complete and
verified. Do not claim customer runtime activation, official-fee/annuity execution, deployment,
production, product, or release approval.
