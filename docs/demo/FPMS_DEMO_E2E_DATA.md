# FPMS Demo E2E Happy Path Data

This document defines two manual-demo data sets derived from `FPMS_Automation_Skeleton_Pack/data` seed assets. Use a fresh run suffix for each rehearsal to avoid unique-code collisions.

Recommended run suffix for the first rehearsal:

```text
DEMOE2E001
```

All demo values below are examples. If a previous rehearsal has already used the same `case_no`, increment the suffix, for example `DEMOE2E002`.

## Source Assets

| Asset | Skeleton Source | Demo Use |
|---|---|---|
| Client | `DS-CL-001` 北京创新科技有限公司 | Main domestic client |
| Applicant 1 | `DS-AP-001` 北京创新科技有限公司, 法人, CN | Primary applicant for Demo Set 1 |
| Applicant 2 | `DS-AP-002` 张三, 自然人, CN | Backup applicant for Demo Set 2 |
| Formalities user | `DS-U-FM-01` | Case/document/task operations |
| Finance user | `DS-U-FI-01` | Fee, bill, payment, pay-list operations |
| Agent user | `DS-U-AG-01` | Main agent / commission participant |
| Supervisor user | `DS-U-SP-01` | Task supervision |
| A scenario case | `DS-CASE-A-001` | `NORMAL / IN_IN / INVENTION`, starts `NOT_FILED` |
| B scenario case | `DS-CASE-B-001` | `NORMAL / IN_IN / INVENTION`, starts `SUB_EXAM` |
| Apply fee rates | `DS-RATE-001/002/003` | Base official fee, service fee, excess claim fee |
| OA service rate | `DS-RATE-008` | OA service fee |
| OA notice template | `DS-TPL-DOC-001` | `OA_NOTICE`, official incoming document |
| OA reply template | `DS-TPL-DOC-002` | `OA_REPLY`, official outgoing reply |

## Demo Set 1

Primary happy-path case for A wave and B wave continuation.

| Field | Value |
|---|---|
| Demo set label | Demo Set 1 |
| Client | 北京创新科技有限公司 |
| Applicant | 北京创新科技有限公司 |
| Applicant type | ENTITY / 法人 |
| Country | CN |
| Case number | `DEMO-A1-DEMOE2E001` |
| Chinese title | 智能传感器控制方法 |
| English title | Intelligent Sensor Control Method |
| Case type | `NORMAL` |
| Patent category | `INVENTION` |
| Flow direction | `IN_IN` |
| Applicant kind | `ENTITY` |
| Receive date | `2026-04-20` |
| Filing / submitted date | `2026-04-22` |
| Application number | `202610000001.1` |
| Priority 1 | `CN-P2026-001`, priority date `2026-03-01` |
| Priority 2 | `CN-P2026-002`, priority date `2026-03-15` |
| Claim count | `12` |
| Spec pages | `30` |
| Claim pages | `4` |
| Draw pages | `6` |
| Manuscript words | `8500` |
| Fee reduction | `0.15` |
| Discount rate | `0.90` |
| Currency | `CNY` |
| Batch filing | `generate_list=true`, `apply_exam_now=true` |
| Apply fee draft | `APPLY_FEE`, rates `APPLY_BASE_GOV`, `APPLY_EXCESS_CLAIM`, `APPLY_SERVICE` |
| Official pay list | Type `APPLY`, planned pay date `2026-04-25` |
| AR bill | Bill date `2026-04-26`, due date `2026-05-26` |
| Payment | Pay date `2026-04-28`, amount equals or partially covers bill balance |
| Commission | Normal rule, service fee base, main/co-agent split visible |

Expected stable backend semantics already covered by A-wave automation:

- `TC-A-001` and `TC-A-002`: case, applicant, inventor, priority, bio/spec/control fields are persisted and retrievable.
- `TC-A-011`: batch filing moves selected cases to `WAITING_RECEIPT`, registers submission-list documents, and creates `APPLY_FEE_LIMIT` tasks.
- `TC-A-013` and `TC-A-014`: generated tasks expose base date, deadline, inner deadline, reminders, worker/supervisor, and task log semantics.
- `TC-A-015`: `APPLY_FEE` draft totals are calculated from configured rates, claim count, fee reduction, and service discount.
- `TC-A-017`, `TC-A-019`, `TC-A-021`, `TC-A-023`: pay list, official payment, bill, payment offset, case receipt, and commission are visible through backend-supported paths.

## Demo Set 2

Backup or parallel case for showing that the flow is not hard-coded to one applicant.

| Field | Value |
|---|---|
| Demo set label | Demo Set 2 |
| Client | 北京创新科技有限公司 |
| Applicant | 张三 |
| Applicant type | INDIVIDUAL / 自然人 |
| Country | CN |
| Case number | `DEMO-A2-DEMOE2E001` |
| Chinese title | 可拆卸连接结构 |
| English title | Detachable Connecting Structure |
| Case type | `NORMAL` |
| Patent category | `INVENTION` |
| Flow direction | `IN_IN` |
| Applicant kind | `INDIVIDUAL` |
| Receive date | `2026-04-21` |
| Filing / submitted date | `2026-04-23` |
| Application number | `202610000002.6` |
| Priority 1 | `CN-P2026-101`, priority date `2026-03-05` |
| Claim count | `10` |
| Spec pages | `18` |
| Claim pages | `3` |
| Draw pages | `4` |
| Manuscript words | `5200` |
| Fee reduction | `0.00` |
| Discount rate | `1.00` |
| Currency | `CNY` |
| Demo use | Backup A-wave path, or second case in batch filing selection |

## OA Continuation Data

Use Demo Set 1 after the case has reached the substantive-exam-ready state used by B-wave automation.

| Field | Value |
|---|---|
| OA case | `DEMO-A1-DEMOE2E001` or B-wave arranged case `CASE-B-<RUN_ID>-001` |
| OA incoming title | `OA来文-DEMOE2E001` |
| OA incoming template | `OA_NOTICE` |
| Direction | `OFFICIAL_IN` |
| Dispatch date | `2026-05-10` |
| Receive date | `2026-05-12` |
| Incoming registration number | `OA-DEMOE2E001` |
| Summary | `第一次审查意见通知书，需提交答复。` |
| Need reply | `true` |
| Official due date | `2026-08-20` |
| OA reply title | `OA答复-DEMOE2E001` |
| OA reply template | `OA_REPLY` |
| Reply date | `2026-06-01` |
| OA fee draft | `OA_FEE`, service item from `OA_SERVICE_STANDARD` |
| OA bill | Bill date `2026-06-03`, due date `2026-07-03` |
| OA payment | Pay date `2026-06-05` |

Expected stable backend semantics already covered by B-wave automation:

- `TC-B-001`: incoming OA document draft is created with editable required fields.
- `TC-B-002`: official due date overrides task deadline while preserving base date.
- `TC-B-004`: `OA_REPLY_LIMIT` task and task log are generated.
- `TC-B-006` and `TC-B-008`: reply document links to incoming OA, open reply task is marked done, and case status is restored.
- `TC-B-009` through `TC-B-012`: OA fee draft, official-payment path, OA AR bill/payment, and OA commission are visible.
- `TC-B-013`: changing `NeedReply` or deadline from the main document interface synchronizes task state/date with audit behavior.

## Deferred Demo Scope

`TC-B-005` 内部准备任务 is intentionally not part of this manual demo. It remains deferred in `BATCH-B-WAVE-CLOSE-AUDIT-01` and must not be presented as completed.
