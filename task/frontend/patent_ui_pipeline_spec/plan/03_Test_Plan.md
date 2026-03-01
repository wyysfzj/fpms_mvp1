# Patent UI Pipeline Dashboard — Test Plan

**Author**: Test Agent
**Date**: 2026-02-22
**Ref**: `plan/01_Architect_Plan.md`, `PATENT_UI_PIPELINE_DASHBOARD_SPEC.md`, `reference/newpatent_static.html`

---

## 1. Scope

This test plan covers:
- **Backend API enrichment** (BE-01 through BE-04): automated pytest cases
- **Frontend pipeline dashboard**: manual smoke tests
- **Seed test data**: Simplified Chinese realistic data for demo / manual verification
- **Quality gate checklist**: step-by-step verification procedure

---

## 2. Backend API Tests (pytest)

All backend tests follow the existing patterns in `backend/tests/`:
- Fixtures: `client` (TestClient), `auth_headers` (Bearer token for admin)
- Assertions: status code, JSON key presence, value types
- Data setup: create prerequisite entities inline (client, case, task, bill, payment)

### 2.1 Test File: `backend/tests/test_pipeline_api.py`

This single file covers all four backend enrichment tasks. Each test is self-contained, creating its own prerequisite data.

---

#### Test 1: `test_bills_list_enriched`

**Covers**: BE-01 — Enrich `GET /api/v1/bills` response
**Purpose**: Verify that bill list items include `amount`, `balance`, `status`, `due_date`, `bill_date`, and `client_name`.

```python
from __future__ import annotations

from uuid import uuid4


def test_bills_list_enriched(client, auth_headers) -> None:
    """GET /api/v1/bills items must include enriched fields after BE-01."""
    # 1. Create a client
    client_payload = {
        "client_code": f"C-{uuid4().hex[:8]}",
        "name_cn": "腾讯科技(深圳)",
        "name_en": "Tencent Technology",
        "client_type": "CLIENT",
        "default_currency": "CNY",
        "is_active": True,
    }
    resp = client.post("/api/v1/clients", json=client_payload, headers=auth_headers)
    assert resp.status_code == 201
    client_id = resp.json()["id"]

    # 2. Create a bill with known fields
    bill_payload = {
        "client_id": client_id,
        "bill_no": f"BILL-{uuid4().hex[:6]}",
        "currency": "CNY",
        "status": "UNSETTLED",
        "bill_date": "2026-01-15",
        "due_date": "2026-02-15",
        "amount": "8500.00",
        "balance": "8500.00",
    }
    resp = client.post("/api/v1/bills", json=bill_payload, headers=auth_headers)
    assert resp.status_code == 201

    # 3. List bills and verify enriched fields
    resp = client.get("/api/v1/bills", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1

    # Find our bill
    bill = next((b for b in items if b["client_id"] == client_id), None)
    assert bill is not None

    # Enriched fields must be present
    assert "amount" in bill, "amount field missing from bill list item"
    assert "balance" in bill, "balance field missing from bill list item"
    assert "status" in bill, "status field missing from bill list item"
    assert "due_date" in bill, "due_date field missing from bill list item"
    assert "bill_date" in bill, "bill_date field missing from bill list item"
    assert "client_name" in bill, "client_name field missing from bill list item"

    # Verify values
    assert bill["status"] == "UNSETTLED"
    assert bill["client_name"] == "腾讯科技(深圳)"
    assert float(bill["amount"]) == 8500.00
    assert float(bill["balance"]) == 8500.00
```

---

#### Test 2: `test_payments_list_enriched`

**Covers**: BE-02 — Enrich `GET /api/v1/payments` response
**Purpose**: Verify that payment list items include `amount` and `currency`.

```python
def test_payments_list_enriched(client, auth_headers) -> None:
    """GET /api/v1/payments items must include amount and currency after BE-02."""
    # 1. Create a client
    client_payload = {
        "client_code": f"C-{uuid4().hex[:8]}",
        "name_cn": "小米移动",
        "name_en": "Xiaomi Mobile",
        "client_type": "CLIENT",
        "default_currency": "CNY",
        "is_active": True,
    }
    resp = client.post("/api/v1/clients", json=client_payload, headers=auth_headers)
    assert resp.status_code == 201
    client_id = resp.json()["id"]

    # 2. Create a payment
    payment_payload = {
        "client_id": client_id,
        "amount": "50000.00",
        "pay_no": f"PAY-{uuid4().hex[:6]}",
        "pay_date": "2026-02-10",
        "currency": "CNY",
    }
    resp = client.post("/api/v1/payments", json=payment_payload, headers=auth_headers)
    assert resp.status_code == 201

    # 3. List payments and verify enriched fields
    resp = client.get("/api/v1/payments", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1

    payment = next((p for p in items if p["client_id"] == client_id), None)
    assert payment is not None

    # Enriched fields
    assert "amount" in payment, "amount field missing from payment list item"
    assert "currency" in payment, "currency field missing from payment list item"

    # Verify values
    assert float(payment["amount"]) == 50000.00
    assert payment["currency"] == "CNY"
```

---

#### Test 3: `test_tasks_list_with_case_no`

**Covers**: BE-03 — Enrich task list with `case_no`
**Purpose**: Verify that `GET /api/v1/tasks` items include `case_no` from the linked case.

```python
def test_tasks_list_with_case_no(client, auth_headers) -> None:
    """GET /api/v1/tasks items must include case_no after BE-03."""
    # 1. Create a client
    client_payload = {
        "client_code": f"C-{uuid4().hex[:8]}",
        "name_cn": "蔚来汽车",
        "name_en": "NIO Auto",
        "client_type": "CLIENT",
        "default_currency": "CNY",
        "is_active": True,
    }
    resp = client.post("/api/v1/clients", json=client_payload, headers=auth_headers)
    assert resp.status_code == 201
    client_id = resp.json()["id"]

    # 2. Create a case with known case_no
    case_no = f"P2310-{uuid4().hex[:3]}"
    case_payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": "一种激光雷达避障系统",
    }
    resp = client.post("/api/v1/cases", json=case_payload, headers=auth_headers)
    assert resp.status_code == 201
    case_id = resp.json()["id"]

    # 3. Create a task linked to the case
    task_payload = {
        "case_id": case_id,
        "title": "答复第一次审查意见 (OA1)",
        "due_date": "2026-03-15",
    }
    resp = client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    assert resp.status_code == 201

    # 4. List tasks and verify case_no
    resp = client.get("/api/v1/tasks", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1

    task = next((t for t in items if t["case_id"] == case_id), None)
    assert task is not None

    assert "case_no" in task, "case_no field missing from task list item"
    assert task["case_no"] == case_no
```

---

#### Test 4: `test_cases_list_with_client_name`

**Covers**: BE-04 — Enrich case list with `client_name`
**Purpose**: Verify that `GET /api/v1/cases` items include `client_name` from the linked client.

```python
def test_cases_list_with_client_name(client, auth_headers) -> None:
    """GET /api/v1/cases items must include client_name after BE-04."""
    # 1. Create a client
    client_payload = {
        "client_code": f"C-{uuid4().hex[:8]}",
        "name_cn": "大疆创新",
        "name_en": "DJI Innovation",
        "client_type": "CLIENT",
        "default_currency": "CNY",
        "is_active": True,
    }
    resp = client.post("/api/v1/clients", json=client_payload, headers=auth_headers)
    assert resp.status_code == 201
    client_id = resp.json()["id"]

    # 2. Create a case linked to the client
    case_no = f"P2311-{uuid4().hex[:3]}"
    case_payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": "一种无人机多目标跟踪系统",
    }
    resp = client.post("/api/v1/cases", json=case_payload, headers=auth_headers)
    assert resp.status_code == 201

    # 3. List cases and verify client_name
    resp = client.get("/api/v1/cases", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1

    case = next((c for c in items if c["case_no"] == case_no), None)
    assert case is not None

    assert "client_name" in case, "client_name field missing from case list item"
    assert case["client_name"] == "大疆创新"
```

---

## 3. Simplified Chinese Test Data (for Seed / Demo)

All test data is derived from `reference/newpatent_static.html` and extended with realistic Chinese IP practice data.

### 3.1 Clients (客户)

| # | `client_code` | `name_cn` | `name_en` | `client_type` | `default_currency` |
|---|---|---|---|---|---|
| 1 | `C-TENCENT` | 腾讯科技(深圳) | Tencent Technology (Shenzhen) | CLIENT | CNY |
| 2 | `C-NIO` | 蔚来汽车 | NIO Automobile | CLIENT | CNY |
| 3 | `C-DJI` | 大疆创新 | DJI Innovation | CLIENT | CNY |
| 4 | `C-XIAOMI` | 小米移动 | Xiaomi Mobile | CLIENT | CNY |
| 5 | `C-HUAWEI` | 华为终端 | Huawei Terminal | CLIENT | CNY |
| 6 | `C-BYD` | 比亚迪电子 | BYD Electronics | CLIENT | CNY |

### 3.2 Cases (案件)

| # | `case_no` | `case_type` | `patent_category` | `client` (name_cn) | `title_cn` | `status` |
|---|---|---|---|---|---|---|
| 1 | `P2310-008` | NORMAL | INV | 蔚来汽车 | 一种激光雷达避障系统 | ACTIVE |
| 2 | `P2311-042` | NORMAL | INV | 大疆创新 | 一种无人机多目标跟踪系统 | ACTIVE |
| 3 | `P2312-005` | NORMAL | INV | 比亚迪电子 | 一种动力电池热管理系统 | ACTIVE |
| 4 | `P2401-017` | NORMAL | UTL | 腾讯科技(深圳) | 一种分布式数据库查询优化方法 | ACTIVE |
| 5 | `P2401-023` | NORMAL | INV | 华为终端 | 一种5G基站波束赋形方法及装置 | ACTIVE |
| 6 | `P2402-001` | NORMAL | DES | 小米移动 | 一种折叠屏手机外观设计 | ACTIVE |

### 3.3 Tasks (待办任务)

| # | `case_no` (via case) | `title` | `due_date` | `status` | Client (via case) |
|---|---|---|---|---|---|
| 1 | P2310-008 | 答复第一次审查意见 (OA1) | 2026-02-24 | OPEN | 蔚来汽车 |
| 2 | P2311-042 | 缴纳登记费 | 2026-03-08 | OPEN | 大疆创新 |
| 3 | P2312-005 | 新案撰写 | 2026-03-01 | OPEN | 比亚迪电子 |
| 4 | P2401-017 | 提交实质审查请求书 | 2026-03-15 | OPEN | 腾讯科技(深圳) |
| 5 | P2401-023 | 答复第二次审查意见 (OA2) | 2026-02-25 | OPEN | 华为终端 |
| 6 | P2402-001 | 准备优先权文件 | 2026-04-01 | OPEN | 小米移动 |

> **Deadline classification** (for Action Center badges):
> - Task 1 (P2310-008): 剩2天 → `badge urgent` (<=3 days)
> - Task 5 (P2401-023): 剩3天 → `badge urgent` (<=3 days)
> - Task 3 (P2312-005): 剩7天 → `badge warn` (<=7 days)
> - Tasks 2, 4, 6: > 7 days → `badge normal`

### 3.4 Bills (账单)

| # | `bill_no` | Client (name_cn) | `currency` | `status` | `amount` | `balance` | `bill_date` | `due_date` |
|---|---|---|---|---|---|---|---|---|
| 1 | BILL-2023-109 | 小米移动 | CNY | UNSETTLED | 8,500.00 | 8,500.00 | 2026-01-15 | 2026-02-19 |
| 2 | BILL-2023-112 | 华为终端 | CNY | UNSETTLED | 12,300.00 | 12,300.00 | 2026-02-01 | 2026-03-05 |
| 3 | BILL-2023-115 | 大疆创新 | CNY | SETTLED | 6,200.00 | 0.00 | 2025-12-10 | 2026-01-10 |

> **Financial Loop classification** (for Finance Panel):
> - Bill 1 (BILL-2023-109): UNSETTLED, due_date < today → `badge urgent`, "已逾期 3 天"
> - Bill 2 (BILL-2023-112): UNSETTLED, due_date >= today → `badge warn`, "待付款"
> - Bill 3 (BILL-2023-115): SETTLED → not shown in pending/overdue

### 3.5 Payments (回款)

| # | `pay_no` | Client (name_cn) | `currency` | `amount` | `pay_date` |
|---|---|---|---|---|---|
| 1 | PAY-2026-055 | 腾讯科技(深圳) | CNY | 50,000.00 | 2026-02-21 |
| 2 | PAY-2026-056 | 大疆创新 | CNY | 6,200.00 | 2026-01-05 |

> **Finance Panel display**:
> - Payment 1: green highlight, "待核销 Payment", "→ 关联账单 (Offset)"
> - Payment 2: already offset against BILL-2023-115 (optional display)

### 3.6 Fee Drafts (费用草稿) — for Pipeline Card 3

| # | `case_no` (via case) | Client (name_cn) | `currency` | `status` | Estimated Amount |
|---|---|---|---|---|---|
| 1 | P2310-008 | 蔚来汽车 | CNY | OPEN | 25,000.00 |
| 2 | P2401-017 | 腾讯科技(深圳) | CNY | OPEN | 38,000.00 |
| 3 | P2401-023 | 华为终端 | CNY | OPEN | 19,000.00 |

> Pipeline Card 3 total: ¥82,000 (¥82k)

---

## 4. Proposed Seed Data Additions

The following code block proposes additions to `backend/scripts/seed_dev.py`. These additions should be added as a new function `seed_demo_data(db)` called after `seed_admin_user(db)` in the `main()` function.

> **NOTE**: Do NOT modify `seed_dev.py` yet — this is a plan-only proposal.

```python
def seed_demo_data(db: Session) -> None:
    """Seed demo entities for Pipeline Dashboard. Idempotent."""
    from app.modules.masterdata.clients.models import Client
    from app.modules.cases.models import T_Case
    from app.modules.tasks.models import T_Task
    from app.modules.billing.models import Bill, Payment
    from app.modules.fees.models import FeeDraft, FeeItem, FeeRate
    from datetime import date
    from decimal import Decimal

    # ---- Clients ----
    demo_clients = [
        {"client_code": "C-TENCENT", "name_cn": "腾讯科技(深圳)", "name_en": "Tencent Technology (Shenzhen)", "client_type": "CLIENT", "default_currency": "CNY", "is_active": True},
        {"client_code": "C-NIO",     "name_cn": "蔚来汽车",       "name_en": "NIO Automobile",              "client_type": "CLIENT", "default_currency": "CNY", "is_active": True},
        {"client_code": "C-DJI",     "name_cn": "大疆创新",       "name_en": "DJI Innovation",              "client_type": "CLIENT", "default_currency": "CNY", "is_active": True},
        {"client_code": "C-XIAOMI",  "name_cn": "小米移动",       "name_en": "Xiaomi Mobile",               "client_type": "CLIENT", "default_currency": "CNY", "is_active": True},
        {"client_code": "C-HUAWEI",  "name_cn": "华为终端",       "name_en": "Huawei Terminal",             "client_type": "CLIENT", "default_currency": "CNY", "is_active": True},
        {"client_code": "C-BYD",     "name_cn": "比亚迪电子",     "name_en": "BYD Electronics",             "client_type": "CLIENT", "default_currency": "CNY", "is_active": True},
    ]

    created_clients = {}
    for c_data in demo_clients:
        existing = db.query(Client).filter(Client.client_code == c_data["client_code"]).first()
        if existing:
            created_clients[c_data["client_code"]] = existing.id
            continue
        c = Client(id=str(uuid4()), **c_data)
        db.add(c)
        db.flush()
        created_clients[c_data["client_code"]] = c.id

    # ---- Cases ----
    demo_cases = [
        {"case_no": "P2310-008", "case_type": "NORMAL", "patent_category": "INV", "flow_dir": "CN_DOMESTIC", "client_code": "C-NIO",     "title_cn": "一种激光雷达避障系统"},
        {"case_no": "P2311-042", "case_type": "NORMAL", "patent_category": "INV", "flow_dir": "CN_DOMESTIC", "client_code": "C-DJI",     "title_cn": "一种无人机多目标跟踪系统"},
        {"case_no": "P2312-005", "case_type": "NORMAL", "patent_category": "INV", "flow_dir": "CN_DOMESTIC", "client_code": "C-BYD",     "title_cn": "一种动力电池热管理系统"},
        {"case_no": "P2401-017", "case_type": "NORMAL", "patent_category": "UTL", "flow_dir": "CN_DOMESTIC", "client_code": "C-TENCENT", "title_cn": "一种分布式数据库查询优化方法"},
        {"case_no": "P2401-023", "case_type": "NORMAL", "patent_category": "INV", "flow_dir": "CN_DOMESTIC", "client_code": "C-HUAWEI",  "title_cn": "一种5G基站波束赋形方法及装置"},
        {"case_no": "P2402-001", "case_type": "NORMAL", "patent_category": "DES", "flow_dir": "CN_DOMESTIC", "client_code": "C-XIAOMI",  "title_cn": "一种折叠屏手机外观设计"},
    ]

    created_cases = {}
    for cs_data in demo_cases:
        existing = db.query(T_Case).filter(T_Case.case_no == cs_data["case_no"]).first()
        if existing:
            created_cases[cs_data["case_no"]] = existing.id
            continue
        client_code = cs_data.pop("client_code")
        cs = T_Case(id=str(uuid4()), client_id=created_clients[client_code], status="ACTIVE", **cs_data)
        db.add(cs)
        db.flush()
        created_cases[cs_data["case_no"]] = cs.id

    # ---- Tasks ----
    demo_tasks = [
        {"case_no": "P2310-008", "title": "答复第一次审查意见 (OA1)",    "due_date": date(2026, 2, 24)},
        {"case_no": "P2311-042", "title": "缴纳登记费",                 "due_date": date(2026, 3, 8)},
        {"case_no": "P2312-005", "title": "新案撰写",                   "due_date": date(2026, 3, 1)},
        {"case_no": "P2401-017", "title": "提交实质审查请求书",          "due_date": date(2026, 3, 15)},
        {"case_no": "P2401-023", "title": "答复第二次审查意见 (OA2)",    "due_date": date(2026, 2, 25)},
        {"case_no": "P2402-001", "title": "准备优先权文件",              "due_date": date(2026, 4, 1)},
    ]

    for t_data in demo_tasks:
        case_no = t_data.pop("case_no")
        case_id = created_cases.get(case_no)
        if not case_id:
            continue
        existing = db.query(T_Task).filter(T_Task.case_id == case_id, T_Task.title == t_data["title"]).first()
        if existing:
            continue
        t = T_Task(id=str(uuid4()), case_id=case_id, status="OPEN", **t_data)
        db.add(t)

    # ---- Bills ----
    demo_bills = [
        {"bill_no": "BILL-2023-109", "client_code": "C-XIAOMI", "currency": "CNY", "status": "UNSETTLED", "amount": Decimal("8500.00"),  "balance": Decimal("8500.00"),  "bill_date": date(2026, 1, 15), "due_date": date(2026, 2, 19)},
        {"bill_no": "BILL-2023-112", "client_code": "C-HUAWEI", "currency": "CNY", "status": "UNSETTLED", "amount": Decimal("12300.00"), "balance": Decimal("12300.00"), "bill_date": date(2026, 2, 1),  "due_date": date(2026, 3, 5)},
        {"bill_no": "BILL-2023-115", "client_code": "C-DJI",    "currency": "CNY", "status": "SETTLED",   "amount": Decimal("6200.00"),  "balance": Decimal("0.00"),     "bill_date": date(2025, 12, 10),"due_date": date(2026, 1, 10)},
    ]

    for b_data in demo_bills:
        existing = db.query(Bill).filter(Bill.bill_no == b_data["bill_no"]).first()
        if existing:
            continue
        client_code = b_data.pop("client_code")
        b = Bill(id=str(uuid4()), client_id=created_clients[client_code], **b_data)
        db.add(b)

    # ---- Payments ----
    demo_payments = [
        {"pay_no": "PAY-2026-055", "client_code": "C-TENCENT", "currency": "CNY", "amount": Decimal("50000.00"), "pay_date": date(2026, 2, 21)},
        {"pay_no": "PAY-2026-056", "client_code": "C-DJI",     "currency": "CNY", "amount": Decimal("6200.00"),  "pay_date": date(2026, 1, 5)},
    ]

    for p_data in demo_payments:
        existing = db.query(Payment).filter(Payment.pay_no == p_data["pay_no"]).first()
        if existing:
            continue
        client_code = p_data.pop("client_code")
        p = Payment(id=str(uuid4()), client_id=created_clients[client_code], **p_data)
        db.add(p)

    db.commit()
    print("Demo data seeded (6 clients, 6 cases, 6 tasks, 3 bills, 2 payments)")
```

---

## 5. Frontend Manual Smoke Tests

### 5.1 Pipeline Cards

| # | Test | Steps | Expected Result | Pass? |
|---|------|-------|-----------------|-------|
| SM-01 | Pipeline cards render | Navigate to `/dashboard` | 4 cards visible with colored top bars: blue, yellow, purple, green | |
| SM-02 | Pipeline card values | Observe card values | Card 1: case count (e.g. "6"); Card 2: task count (e.g. "6") with urgent badge "2 绝限"; Card 3: ¥82k; Card 4: ¥50,000 | |
| SM-03 | Card 1 click → drawer | Click "新委托" card | New Case drawer slides in from right with backdrop | |
| SM-04 | Card 2 click → tasks | Click "待办任务" card | Navigates to `/tasks` | |
| SM-05 | Card 3 click → fee drafts | Click "待出账草稿" card | Navigates to `/fees/drafts` | |
| SM-06 | Card 4 click → payments | Click "待核销" card | Navigates to `/billing/payments` | |

### 5.2 Action Center (待办任务)

| # | Test | Steps | Expected Result | Pass? |
|---|------|-------|-----------------|-------|
| SM-07 | Panel renders | Observe left panel | Title "待办任务", "查看全部 →" link visible | |
| SM-08 | Case tags monospace | Observe task rows | Case numbers (P2310-008, P2311-042, etc.) in monospace pill style | |
| SM-09 | Client names shown | Observe task rows | Each row shows client name (蔚来汽车, 大疆创新, etc.) | |
| SM-10 | Deadline badges | Observe badges | "答复第一次审查意见" → `badge urgent` "绝限: 剩2天"; "缴纳登记费" → `badge normal` "剩14天" | |
| SM-11 | Relation tags | Observe tags | `rel-tag doc` (关联文书) or `rel-tag fee` (关联费用) visible where applicable | |
| SM-12 | Row click | Click any task row | Navigates to `/cases/:id` for the linked case | |
| SM-13 | "查看全部" link | Click "查看全部 →" | Navigates to `/tasks` | |

### 5.3 Finance Panel (财务状况)

| # | Test | Steps | Expected Result | Pass? |
|---|------|-------|-----------------|-------|
| SM-14 | Panel renders | Observe right panel | Title "财务状况" visible | |
| SM-15 | Payment row (green) | Observe first row | Green background (`finance-highlight`), "+ ¥ 50,000.00", "待核销 Payment" badge, "来源: 腾讯科技(深圳)" | |
| SM-16 | Offset link | Observe payment row | "→ 关联账单 (Offset)" link visible | |
| SM-17 | Overdue bill (red) | Observe second row | "BILL-2023-109", "¥ 8,500.00", `badge urgent` "已逾期 3 天" | |
| SM-18 | Pending bill (yellow) | Observe third row | "BILL-2023-112", "¥ 12,300.00", `badge warn` "待付款" | |
| SM-19 | Max 5 items | Observe panel | At most 5 finance items displayed | |

### 5.4 New Case Drawer (新建案件)

| # | Test | Steps | Expected Result | Pass? |
|---|------|-------|-----------------|-------|
| SM-20 | Drawer opens | Click Pipeline Card 1 | Drawer slides in; backdrop visible | |
| SM-21 | Form fields | Observe drawer body | 3 fields: 客户 (searchable select), 案件类型 (select: 发明专利/实用新型/外观设计), 案件标题 (textarea) | |
| SM-22 | Close via cancel | Click "取消" button | Drawer closes, no side effects | |
| SM-23 | Close via ESC | Press ESC key | Drawer closes | |
| SM-24 | Close via backdrop | Click backdrop overlay | Drawer closes | |
| SM-25 | Submit creates case | Fill form, click "创建案件" | Case created, drawer closes, navigates to new case detail | |

### 5.5 Responsive Layout

| # | Test | Steps | Expected Result | Pass? |
|---|------|-------|-----------------|-------|
| SM-26 | Desktop (>1100px) | Set viewport to 1440px | Pipeline: 4 columns; Split grid: 2 columns (1.4fr 1fr) | |
| SM-27 | Tablet (<=1100px) | Set viewport to 1024px | Pipeline: 2x2 grid; Split grid: single column (stacked) | |

### 5.6 Chinese Text Verification

| # | Test | Steps | Expected Result | Pass? |
|---|------|-------|-----------------|-------|
| SM-28 | All UI Chinese | Scan entire dashboard | All labels, badges, button text, panel titles in Simplified Chinese | |
| SM-29 | Pipeline labels | Check card labels | "新委托", "待办任务", "待出账草稿", "待核销" | |
| SM-30 | Badge text | Check all badges | "绝限: 剩N天", "剩N天", "待核销 Payment", "已逾期 N 天", "待付款" | |
| SM-31 | Drawer labels | Open drawer | Title "新建案件", fields "客户", "案件类型", "案件标题", buttons "取消", "创建案件" | |

---

## 6. Quality Gate Checklist

Execute these steps in order. All must pass before marking the pipeline dashboard complete.

### Step 1: Backend Lint & Format

```bash
cd backend && ruff check --fix . && ruff format .
```
- [ ] No lint errors
- [ ] No format changes needed

### Step 2: Backend Tests

```bash
cd backend && pytest -q
```
- [ ] All existing tests pass
- [ ] New `test_pipeline_api.py` tests pass (4 tests)

### Step 3: Frontend Lint

```bash
cd frontend && npm run lint
```
- [ ] No ESLint errors

### Step 4: Frontend TypeScript Check

```bash
cd frontend && npm run typecheck
```
- [ ] No TypeScript errors

### Step 5: Frontend Build

```bash
cd frontend && npm run build
```
- [ ] Build completes successfully
- [ ] No warnings about missing imports

### Step 6: Manual Smoke Test Execution

- [ ] Run seed: `cd backend && python scripts/seed_dev.py` (with demo data)
- [ ] Start backend: `uvicorn app.main:app --reload --port 8000`
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Execute all SM-01 through SM-31 smoke tests
- [ ] Record pass/fail for each

### Step 7: API Contract Verification

Using `http://localhost:8000/docs` (Swagger UI):
- [ ] `GET /api/v1/bills` → items contain `amount`, `balance`, `status`, `due_date`, `bill_date`, `client_name`
- [ ] `GET /api/v1/payments` → items contain `amount`, `currency`
- [ ] `GET /api/v1/tasks` → items contain `case_no`
- [ ] `GET /api/v1/cases` → items contain `client_name`

### Step 8: Cross-Browser Spot Check (Optional)

- [ ] Chrome (primary)
- [ ] Firefox
- [ ] Safari

---

## 7. Test Data Traceability Matrix

Maps static reference HTML data to test data to ensure consistency.

| Reference (newpatent_static.html) | Test Data Entity | Test Covering |
|---|---|---|
| Pipeline Card: "12" new cases | 6 demo cases (count varies) | SM-01, SM-02 |
| Pipeline Card: "45" pending, "3 绝限" | 6 demo tasks, 2 urgent | SM-02 |
| Pipeline Card: "¥ 82k" unbilled | 3 fee drafts totaling ¥82k | SM-02 |
| Pipeline Card: "¥ 12k" unallocated | 2 payments (¥50k + ¥6.2k) | SM-02 |
| Action Center: P2310-008, 蔚来汽车, OA1 | Task 1, Case 1, Client 2 | SM-08 to SM-11, test_tasks_list_with_case_no |
| Action Center: P2311-042, 大疆创新, 缴纳登记费 | Task 2, Case 2, Client 3 | SM-08 to SM-11 |
| Action Center: P2312-005, 比亚迪电子, 新案撰写 | Task 3, Case 3, Client 6 | SM-08 to SM-11 |
| Finance: ¥50,000 腾讯科技(深圳), "待核销" | Payment 1, Client 1 | SM-15, SM-16, test_payments_list_enriched |
| Finance: BILL-2023-109, ¥8,500 小米移动, "已逾期3天" | Bill 1, Client 4 | SM-17, test_bills_list_enriched |
| Finance: BILL-2023-112, ¥12,300 华为终端, "待付款" | Bill 2, Client 5 | SM-18 |

---

## 8. Risk & Known Limitations

| Item | Note |
|---|---|
| Pipeline KPI values | Demo seed data produces different totals than static reference (12 vs 6 cases, etc.). Acceptable for demo — values are correct relative to seeded data. |
| Deadline badge calculation | Depends on current date. Tests SM-10 badges will vary; verify logic is "due_date - today". |
| Session-scoped test DB | pytest tests share a session-scoped database. Tests create their own data and filter by known IDs, so there is no cross-test contamination. |
| Payment "unallocated" | All payments shown as "待核销" for MVP. No offset status check. |
| Bill `amount` field | Bill model has `amount` column. The `BillCreateSchema` doesn't currently accept `amount`; it may need to be added or computed from `total_gov + total_service + total_misc`. Verify during BE-01 implementation. |

---

*End of Test Plan*
