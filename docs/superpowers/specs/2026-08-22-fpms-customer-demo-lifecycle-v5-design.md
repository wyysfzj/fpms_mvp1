# FPMS Customer Demo Lifecycle V5 Design

**Status:** Approved by customer direction; planning document only  
**Date:** 2026-08-22  
**Target successor:** `docs/postdemo/demo-lifecycle-customer-v5.html`  
**Reference page:** `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`

## Goal

Create a new standalone Chinese HTML page for a customer-facing FPMS demo. The page tells
one continuous story for one customer and one patent case, preserves the themes covered by
the earlier lifecycle demo, and visibly highlights the capabilities added in recent weeks.

The page explains business outcomes. It does not expose IA checkpoint numbers, API paths,
test terminology, internal evidence gates, or engineering implementation details.

## Authority and Claim Boundary

Content follows this order:

1. The user's approved customer-facing narrative.
2. `docs/superpowers/specs/2026-08-21-fpms-integrated-demo-a-design.md`.
3. The accepted Integrated A final technical rehearsal and Task 10A catalog alignment.
4. The earlier lifecycle HTML only as a visual and coverage reference.

The earlier page is not authoritative for current legal status, official fee values, or
relative deadline calculation. V5 must not copy its fixed official-fee amounts or convert
missing authority into zero.

Required page boundary statements:

- The demo uses fictional data in a controlled local technical rehearsal.
- Every displayed demo template and SERVICE amount is labelled at its point of use as
  `合成测试输入（SYNTHETIC_TEST_ONLY，非客户授权）`.
- Filing preparation is not a claim of official submission.
- A reviewed grant-registration notice moves the case into grant-registration processing;
  it does not by itself claim that the patent is granted or in force.
- The configured demo financial path is SERVICE receivable only.
- Missing official-fee, annuity, and formal customer-template authority is displayed as
  `待配置`, never as `0`, `已缴`, or `已完成`.
- The conclusion is limited to the demonstrated customer journey, not product, release, or
  production approval.

## Chosen Approach

Use a single customer story line with nine stages. Keep the old file unchanged and create a
new successor. Each stage has four concise fields:

1. customer-visible action;
2. system-visible result;
3. one safety or truth boundary where needed;
4. a `最近新增` badge only when the recent Integrated A work materially changed that stage.

A short `之前 / 现在` comparison near the end summarizes the value of the recent work
without turning the page into an engineering changelog.

## Page Structure

### 1. Hero

Title: `从案件建立，到证据闭环，再到客户回款`.

Subtitle: one customer, one case, one traceable journey.

Visible boundary badges:

- `本地技术演示`
- `虚构演示数据`
- `官费未配置不写入`

### 2. Journey Overview

Show the nine stages as a horizontal or wrapping progress line. On narrow screens it becomes
a single-column sequence. The overview links visually to the detailed cards below but does
not require JavaScript navigation.

### 3. Nine Customer Stages

| Stage | Customer-facing story | Observable result | Recent-change highlight |
| --- | --- | --- | --- |
| 01 客户与案件 | Create the client, primary contact, and one patent case from zero. | The same dynamic client/case identities continue through the page. | Fresh-run demo with zero pre-created lifecycle, draft, bill, or payment objects. |
| 02 文件与递交准备 | Select the demo template and resolve the filing work package. | Repeating resolve returns the same package; preparation is not official filing. The template is labelled `合成测试输入（SYNTHETIC_TEST_ONLY，非客户授权）`. | Bundle classification/ID/version/manifest hash and template code/file hash are visible as separate provenance groups. |
| 03 受理与审查 | Process reviewed filing receipt, acceptance, preliminary examination, publication, and substantive-examination evidence. | Each transition is driven by reviewed evidence, with stable case/file lineage. | The 60-row official-document catalog distinguishes executable and reference-only types. |
| 04 第一轮 OA | Record the confirmed deadline, create one linked OA response package, then archive the correct receipt. | OA task stays open after response creation and only the target task closes after the correct receipt. | Exact deadline appears consistently; wrong-case or wrong-source receipts return no business write. |
| 05 第二轮 OA | Run a separate second OA with its own notice, deadline, response package, task, and receipt. | OA1 and OA2 identities never collapse or reuse each other. | Complete independent second-OA lineage and closure. |
| 06 授权登记准备 | Review the grant-registration notice, replace it with a newer reviewed source when needed, reject four mutations on the superseded task, and record `PAY` only on the current grant task. | The case enters grant-registration processing and the superseded task becomes immutable. The grant-task `PAY` instruction creates no official-fee amount and no fee draft. | Durable source replacement, supersession lineage, four old-task mutation gates, and one current-task instruction. |
| 07 服务费草单 | Separately select the configured demo SERVICE item, record `PAY` on the SERVICE obligation, create one linked draft, and lock it. | The draft shows exact service amount/currency and is labelled `合成测试输入（SYNTHETIC_TEST_ONLY，非客户授权）`; official-fee fields show `未配置`. | SERVICE rate item code/source ref/source version/source SHA-256 remains visible; no missing amount becomes zero. |
| 08 客户账单与回款 | Create one unique AR bill (`唯一 AR 账单`) from the locked draft, record one bank receipt, and offset it to the bill. | One bill becomes `已结清 / 余额 0`; payment becomes `已全额核销 / 未核销 0`; the active offset is unique. | Idempotent unique billing, truthful payment state, authoritative amount/currency after reload. |
| 09 后续运维边界 | Explain where official fees, annual fees, and formal customer templates will enter after approved runtime input is supplied. | The customer sees an explicit activation boundary, not fabricated data. | Runtime-input readiness replaces hard-coded legal/fee assumptions. |

### 4. Three Traceability Lanes

Keep the earlier page's useful three-lane mental model, but update the lane names and truth
semantics:

- `案件状态`: preparation, examination, OA, and grant-registration processing.
- `文件与证据`: attachment, reviewed version, deadline/source, response package, receipt,
  archive, and replacement lineage.
- `客户财务`: SERVICE obligation, locked draft, AR bill, bank receipt, and offset.

Official government fees and annual fees appear only in the stage-09 configuration boundary,
not in the executed financial lane.

### 5. Recent Weeks: Before / Now

The comparison contains exactly these customer-relevant messages:

| Before | Now |
| --- | --- |
| Pages and broad stages could be shown. | Evidence, deadlines, tasks, and work packages form one traceable chain. |
| A single OA example dominated the story. | Two OA rounds keep independent identities and receipts. |
| Incorrect or ambiguous actions were hard to explain. | Wrong receipt sources and superseded tasks fail without business writes. |
| Fee examples could look like fixed truth. | SERVICE pricing has visible provenance; unknown official fees remain unconfigured. |
| Billing stopped near draft creation. | Locked draft, unique bill, bank receipt, and offset reach an authoritative zero balance. |

Do not describe the recent work as a broad rewrite, production deployment, or general
security closure.

### 6. Live Demo Script Strip

The page ends with a compact presenter order:

1. customer/case and filing preparation;
2. reviewed filing/acceptance/examination evidence;
3. OA1 response and receipt closure;
4. OA2 independent closure;
5. grant source replacement and current PAY instruction;
6. SERVICE draft, AR bill, bank receipt, and offset;
7. explicit official-fee/annuity/runtime-input boundary.

## Visual Design

- Reuse the earlier page's clean, print-friendly visual language but simplify the number of
  simultaneous rows.
- Use a dark blue lifecycle color, teal evidence color, and amber finance color.
- Use one accent color for `最近新增` badges. Do not mark every card as new.
- Use `待配置` styling that is neutral and explicit, not warning-red and not success-green.
- Keep body text Simplified Chinese. Technical enum values may appear only as secondary
  evidence labels, never as the primary customer wording.
- Support desktop presentation, narrow browser widths, and print/PDF without clipped cards.
- Keep the document self-contained: HTML and CSS only, with no JavaScript, external network
  assets, or runtime API calls.

## Interaction and Error Handling

The page is an explanatory artifact, not a live control surface. It has no JavaScript,
mutation buttons, login dependency, network fetches, or local storage. The complete story is
always visible, readable, and printable.

If a field is not supported by the accepted rehearsal:

- show `待配置` for missing runtime input;
- show `未在本次演示中执行` for an out-of-scope operational step;
- omit the value rather than fabricate a date, amount, status, or authority.

## Verification Contract for the HTML Task

The follow-up task must verify:

1. The old V3 file is byte-identical before and after.
2. The new page contains exactly nine ordered stage cards.
3. All five `之前 / 现在` comparisons are present.
4. The page contains the required boundary phrases: `本地技术演示`, `虚构演示数据`,
   `官费未配置不写入`, `待配置`, `未在本次演示中执行`, and the point-of-use label
   `合成测试输入（SYNTHETIC_TEST_ONLY，非客户授权）` beside the template and SERVICE amount.
5. The page contains no fixed official-fee or annual-fee amount and no claim that filing,
   grant, payment, production, or release occurred outside the demonstrated facts.
6. The recent-change highlights cover evidence provenance, 60-row catalog, two OA rounds,
   no-write rejection, grant-source replacement, SERVICE-only pricing, unique bill, and
   payment offset.
7. HTML parses without errors, contains no JavaScript, external asset, or network dependency,
   and renders without horizontal clipping at desktop and narrow widths.
8. A rendered full-page screenshot and print/PDF check confirm the visual hierarchy and
   Simplified Chinese content.

## Non-Goals

- No edits to product runtime code or existing lifecycle HTML.
- No official-system automation, external submission, signature, payment, or email claim.
- No official-fee or annual-fee calculation.
- No customer runtime bundle activation.
- No security, deployment, production, product, or release closure.
- No replacement for the detailed Integrated A technical evidence ledger.
