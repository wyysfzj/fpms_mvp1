# FPMS Demo E2E Happy Path Script

This script is for a manual demo after backend and frontend are running locally. It uses the two data sets in `docs/demo/FPMS_DEMO_E2E_DATA.md` and the existing `FPMS_Automation_Skeleton_Pack` testcase assets.

## Demo Goal

Demonstrate a patent end-to-end happy path:

1. A wave: new case creation, batch filing, application fee task, fee draft, official pay list, bill, payment offset, and commission.
2. B wave: OA incoming document, reply deadline, OA reply, task write-off, OA fee, OA bill/payment, OA commission, and NeedReply/deadline update.

This demo covers:

- A wave: `TC-A-001`, `TC-A-002`, `TC-A-011`, `TC-A-013`, `TC-A-014`, `TC-A-015`, `TC-A-017`, `TC-A-019`, `TC-A-021`, `TC-A-023`
- B wave: `TC-B-001`, `TC-B-002`, `TC-B-004`, `TC-B-006`, `TC-B-008`, `TC-B-009`, `TC-B-010`, `TC-B-011`, `TC-B-012`, `TC-B-013`

Deferred and not demoed as complete:

- `TC-B-005` 内部准备任务

## Local URLs

| Service | URL |
|---|---|
| Frontend | `http://127.0.0.1:5173` |
| Backend API | `http://127.0.0.1:8000/api/v1` |
| Backend OpenAPI | `http://127.0.0.1:8000/openapi.json` |

Use the local demo account configured by the dev seed. Do not paste real credentials into this document or evidence artifacts.

## Pre-Demo Checklist

1. Confirm backend health:

```bash
curl -sS http://127.0.0.1:8000/healthz
curl -sS http://127.0.0.1:8000/openapi.json
```

2. Confirm frontend opens:

```text
http://127.0.0.1:5173
```

3. Confirm automation smoke can run with optional DB assert disabled:

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
FPMS_API_URL=http://127.0.0.1:8000/api/v1 \
FPMS_USERNAME=admin \
FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" \
FPMS_RUN_ID=LOCAL-RUN-DEMO-A-HAPPY-001 \
FPMS_DB_DSN= \
pytest tests/test_wave_a.py -k "TC-A-001 or TC-A-002 or TC-A-011 or TC-A-013 or TC-A-014 or TC-A-015 or TC-A-017 or TC-A-019 or TC-A-021 or TC-A-023" -q
```

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
FPMS_API_URL=http://127.0.0.1:8000/api/v1 \
FPMS_USERNAME=admin \
FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" \
FPMS_RUN_ID=LOCAL-RUN-DEMO-B-HAPPY-001 \
FPMS_DB_DSN= \
pytest tests/test_wave_b.py -k "TC-B-001 or TC-B-002 or TC-B-004 or TC-B-006 or TC-B-008 or TC-B-009 or TC-B-010 or TC-B-011 or TC-B-012 or TC-B-013" -q
```

## Part 1: Login

1. Open `http://127.0.0.1:5173/login`.
2. Enter the local demo username.
3. Enter the local demo password.
4. Click `登录`.
5. Confirm the system lands on the dashboard or main workbench.

Demo line:

> We start from the seeded local demo tenant. The same backend used by automation is now driving the manual UI demo.

## Part 2: A Wave New Case Mainline

### Step A1: Create Minimal Case

Testcase coverage: `TC-A-001`.

1. Open `案件管理` -> `新建案件`, or navigate to `/cases/new`.
2. Fill required fields with Demo Set 1:

| Field | Value |
|---|---|
| 案号 | `DEMO-A1-DEMOE2E001` |
| 案件类型 | `NORMAL` |
| 专利类型 | `INVENTION` |
| 流向 | `IN_IN` |
| 来源国家 | `CN` |
| 中文名称 | `智能传感器控制方法` |
| 收文日 | `2026-04-20` |
| 客户 | 北京创新科技有限公司 |
| 申请人 | 北京创新科技有限公司 |
| 主申请人 | 是 |

3. Click `保存`.
4. Confirm the success message.
5. Return to `案件列表` and search `DEMO-A1-DEMOE2E001`.
6. Open detail and confirm status is `NOT_FILED`.

Expected result:

- Case is saved.
- Applicant relation is persisted.
- Created audit fields are present.
- Case is searchable.

### Step A2: Fill Complete Case Fields

Testcase coverage: `TC-A-002`.

1. In the case edit page for `DEMO-A1-DEMOE2E001`, fill additional fields:

| Area | Field | Value |
|---|---|---|
| Basic | 英文名称 | `Intelligent Sensor Control Method` |
| Basic | 申请号 | `202610000001.1` |
| Applicant | 申请人 | 北京创新科技有限公司 |
| Inventor | 发明人 | `李明` |
| Priority | 优先权 1 | `CN-P2026-001`, `2026-03-01` |
| Priority | 优先权 2 | `CN-P2026-002`, `2026-03-15` |
| Bio deposit | 保藏单位 | use seeded bio-deposit unit if present |
| Spec | 权利要求数 | `12` |
| Spec | 说明书页数 | `30` |
| Spec | 权利要求页数 | `4` |
| Spec | 附图页数 | `6` |
| Spec | 说明书字数 | `8500` |
| Fee | 费减 | `0.15` |
| Fee | 折扣率 | `0.90` |

2. Click `保存`.
3. Reopen detail.
4. Confirm priorities, spec fields, fee/control fields, and audit fields are visible.

Demo line:

> The MVP closure keeps priority records as the source of truth. The demo can compute the earliest priority date from the priority list.

### Step A3: Prepare Batch Filing Selection

Testcase coverage: setup for `TC-A-011`.

1. Create or reuse two additional `NOT_FILED` domestic cases:

| Case | Applicant | Title |
|---|---|---|
| `DEMO-A2-DEMOE2E001` | 张三 | 可拆卸连接结构 |
| `DEMO-A3-DEMOE2E001` | 北京创新科技有限公司 | 智能阀门控制装置 |

2. Keep all three cases in `NOT_FILED`.
3. Confirm each case has at least one valid applicant.

### Step A4: Batch Filing

Testcase coverage: `TC-A-011`.

1. Open `案件管理` -> `批量递交`, or navigate to `/cases/batch-filing`.
2. Filter by:

| Field | Value |
|---|---|
| 案件类型 | `NORMAL` |
| 流向 | `IN_IN` |
| 收文日 | around `2026-04-20` |

3. Select the three demo cases.
4. Set:

| Field | Value |
|---|---|
| 递交日 | `2026-04-22` |
| 生成递交清单 | true |
| 立即实审 | true |

5. Click the batch submit action.
6. Confirm result summary:

- `success_count` equals selected count.
- `updated_case_ids` includes the selected cases.
- `document_ids` are returned or linked document records are visible.
- `created_task_ids` include generated application-fee deadline tasks.

7. Reopen `DEMO-A1-DEMOE2E001` and confirm status is `WAITING_RECEIPT`.

### Step A5: Application Fee Deadline Task

Testcase coverage: `TC-A-013`, `TC-A-014`.

1. Open `任务管理` -> `任务列表`, or navigate to `/tasks`.
2. Search by the demo case number or filter `Status=OPEN`.
3. Open the `APPLY_FEE_LIMIT` task.
4. Confirm:

| Field | Expected |
|---|---|
| BaseDate | submitted date / filing date according to template source |
| Deadline | calculated |
| InnerDeadline | calculated |
| Reminders | populated when template has offsets |
| Worker | assigned |
| Supervisor | assigned |
| Status | `OPEN` |
| Task log | creation log exists |

5. If demonstrating reassignment, update worker or supervisor and confirm the log entry.

### Step A6: Generate Application Fee Draft

Testcase coverage: `TC-A-015`.

1. Open `费用管理` -> `费用草单`, or navigate to `/fees/drafts`.
2. Click `新增` / `生成申请费草单` if available.
3. Select `DEMO-A1-DEMOE2E001`.
4. Use:

| Field | Value |
|---|---|
| Draft type | `APPLY_FEE` |
| Currency | `CNY` |
| Claim count | `12` |
| Fee reduction | `0.15` |
| Discount rate | `0.90` |

5. Generate the draft.
6. Confirm fee items:

- base official fee
- excess claim fee for claims beyond 10
- service fee

7. Confirm totals:

- government total
- service total
- total amount

Demo line:

> The calculation is rate-driven. Automation already asserts the concrete numeric semantics against the real backend.

### Step A7: Official Pay List And Government Payment

Testcase coverage: `TC-A-017`.

1. Open `官费清单`, or navigate to `/annuity/pay-lists`.
2. Create a pay list from the GOV items of the `APPLY_FEE` draft.
3. Set:

| Field | Value |
|---|---|
| Pay list type | `APPLY` |
| Planned pay date | `2026-04-25` |

4. Save or export the pay list if available.
5. Register official payment:

| Field | Value |
|---|---|
| Paid amount | planned amount |
| Paid date | `2026-04-25` |
| Invoice number | `GOV-DEMOE2E001` |

6. Confirm pay-list status is `PAID`.
7. Confirm the paid record appears in fee/payment queries.

### Step A8: Generate AR Bill

Testcase coverage: `TC-A-019`.

1. Open `账单管理` -> `账单列表`, or navigate to `/billing/bills`.
2. Create a bill from the `APPLY_FEE` draft.
3. Fill:

| Field | Value |
|---|---|
| Client | 北京创新科技有限公司 |
| Bill date | `2026-04-26` |
| Due date | `2026-05-26` |
| Currency | `CNY` |
| Discount rate | `0.90` |

4. Save.
5. Confirm:

- bill status is `UNSETTLED`
- bill items link to fee draft/items
- total gov/service/misc/amount/balance are stable

### Step A9: Customer Payment And Offset

Testcase coverage: `TC-A-021`.

1. Open `收款管理`, or navigate to `/billing/payments`.
2. Create payment:

| Field | Value |
|---|---|
| Client | 北京创新科技有限公司 |
| Pay no | `PAY-DEMOE2E001` |
| Pay date | `2026-04-28` |
| Amount | bill amount or partial amount |
| Currency | `CNY` |

3. Save payment.
4. Click `创建核销`.
5. Select:

| Field | Value |
|---|---|
| Payment | `PAY-DEMOE2E001` |
| Payment line | default line |
| Bill | application fee bill |
| Offset amount | full or partial payment amount |

6. Confirm:

- offset is created
- bill balance is reduced
- status becomes `PARTIALLY_SETTLED` or `SETTLED`
- case receipt shows receivable, received, and arrears state

### Step A10: Commission

Testcase coverage: `TC-A-023`.

1. Open `提成管理`, or navigate to `/commission`.
2. Search the demo case or bill.
3. Confirm:

- commission record exists for the service-fee base
- main/co-agent split is visible
- S1/S2 amounts are calculated
- `WaitPay` / `ForceSettle` initial values are visible
- record is available for settlement entry when conditions are met

## Part 3: B Wave OA Mainline

### Step B1: Register Incoming OA

Testcase coverage: `TC-B-001`, `TC-B-002`.

1. Open `文档管理` -> `中间文件向导`, or navigate to `/documents/wizard`.
2. Step 1: select the OA-ready demo case.
3. Select:

| Field | Value |
|---|---|
| Direction | `OFFICIAL_IN` |
| Template | `OA_NOTICE` |

4. Step 2: fill:

| Field | Value |
|---|---|
| Doc name | `OA来文-DEMOE2E001` |
| Dispatch date | `2026-05-10` |
| Receive date | `2026-05-12` |
| Incoming reg no | `OA-DEMOE2E001` |
| Summary | `第一次审查意见通知书，需提交答复。` |
| Need reply | true |
| Official due date | `2026-08-20` |

5. Save to draft or continue.
6. In Step 3, confirm the generated reply deadline uses official due date.

### Step B2: Generate OA Reply Task

Testcase coverage: `TC-B-004`.

1. Complete the incoming OA wizard flow.
2. Open `任务管理`.
3. Search for the case.
4. Confirm an `OA_REPLY_LIMIT` task exists.
5. Confirm worker, supervisor, status, and task creation log.

### Step B3: Register OA Reply

Testcase coverage: `TC-B-006`, `TC-B-008`.

1. Open `中间文件向导` again.
2. Select the same case.
3. Select:

| Field | Value |
|---|---|
| Direction | `OFFICIAL_OUT` |
| Template | `OA_REPLY` |
| Reply to | `OA来文-DEMOE2E001` |
| Doc name | `OA答复-DEMOE2E001` |
| Reply date | `2026-06-01` |

4. Upload or use a placeholder reply attachment if the UI requests one.
5. Submit.
6. Confirm:

- reply document links to incoming OA
- OA reply task is marked `DONE`
- task log has done/write-off action
- case status returns to `SUB_EXAM`

### Step B4: Generate OA Fee Draft

Testcase coverage: `TC-B-009`.

1. In the wizard Step 4, or in `费用草单`, generate an `OA_FEE` draft.
2. Confirm the service item from `OA_SERVICE_STANDARD`.
3. If a GOV OA item is configured, confirm it is also listed.
4. Confirm totals.

### Step B5: OA Official Pay List

Testcase coverage: `TC-B-010`.

1. If the `OA_FEE` draft includes GOV items, create an official pay list.
2. Register official payment.
3. Confirm only GOV items enter the official pay-list path.
4. Confirm SERVICE items remain billable.

If the current seed only creates service-fee OA drafts, explain that `TC-B-010` backend automation covers the GOV-item branch and proceed to OA billing.

### Step B6: OA Bill And Customer Payment

Testcase coverage: `TC-B-011`.

1. Open `账单管理`.
2. Generate an AR bill from the `OA_FEE` draft.
3. Fill:

| Field | Value |
|---|---|
| Bill date | `2026-06-03` |
| Due date | `2026-07-03` |
| Currency | `CNY` |

4. Save the bill.
5. Open `收款管理`.
6. Create payment:

| Field | Value |
|---|---|
| Pay no | `PAY-OA-DEMOE2E001` |
| Pay date | `2026-06-05` |
| Amount | OA bill amount |

7. Create offset against the OA bill.
8. Confirm bill balance and case receipt update.

### Step B7: OA Commission

Testcase coverage: `TC-B-012`.

1. Open `提成管理`.
2. Search by case or OA bill.
3. Confirm OA service fee enters the commission pipeline.
4. Confirm stage/source remark shows OA stage or equivalent trace.
5. Confirm split and settlement visibility.

### Step B8: NeedReply / Deadline Edit

Testcase coverage: `TC-B-013`.

1. Open `文档管理`.
2. Open `OA来文-DEMOE2E001`.
3. Change deadline to a new valid date and choose the update-task behavior if prompted.
4. Save.
5. Confirm the related task date changes and an audit/task-log entry is visible.
6. Change `NeedReply` to false on a separate rehearsal document if you want to demo task cancellation.
7. Confirm related task is cancelled/closed according to backend-supported behavior.

## Demo Close Script

Use this closing summary:

> The demo exercised the seeded FPMS patent happy path from case intake through filing, deadline task generation, fee draft, official payment, AR bill, client payment offset, and commission. It then continued through an OA incoming document, reply deadline, reply document, automatic task write-off, OA fee/bill/payment, OA commission, and NeedReply/deadline synchronization. The manual flow is backed by the same A/B wave pytest automation and local backend smoke evidence.

## Troubleshooting During Demo

| Symptom | Action |
|---|---|
| Unique case number conflict | Increment the run suffix, for example `DEMOE2E002`. |
| Applicant required error | Ensure every created case has at least one valid applicant. |
| Date/status validation error | Use submitted/filing dates on or after receive date. |
| Fee rate not found | Confirm dev seed ran and fee rates exist. |
| Backend unavailable | Restart backend and rerun seed. |
| Frontend stale data | Refresh page and rerun search. |
| Optional DB assert skipped | Acceptable for demo smoke when `FPMS_DB_DSN=` is explicit. |

## Evidence References

- A wave close audit: `docs/automation/close_audit/BATCH-A-WAVE-CLOSE-AUDIT-01.md`
- B wave close audit: `docs/automation/close_audit/BATCH-B-WAVE-CLOSE-AUDIT-01.md`
- Demo task evidence: `artifacts/BATCH-DEMO-E2E-HAPPY-PATH-01/summary.md`
