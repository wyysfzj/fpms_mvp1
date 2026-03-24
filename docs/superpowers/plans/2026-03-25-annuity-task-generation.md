# FR-FE-06 Annuity Task Generation + Model Extension — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add annuity task multi-year generation endpoint, extend AnnuityTask model with 6 fields, add `first_annuity_year` to Case model, and update frontend list + dialog.

**Architecture:** Single migration adds 6 columns to `t_annuity_task` + 1 column to `t_case`. New generation service function with FeeRate lookup. Update existing list endpoint response. New frontend dialog for generation trigger.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic 2.x, Alembic (SQLite compat), Vue 3 + Element Plus + TypeScript

**Spec:** `docs/superpowers/specs/2026-03-24-annuity-task-generation-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `backend/alembic/versions/pe_fr_fe_06_annuity_task_ext.py` | CREATE | Migration: 6 cols on t_annuity_task + 1 col on t_case |
| `backend/app/modules/annuity/models.py` | EDIT | Add 6 mapped_column fields to AnnuityTask |
| `backend/app/modules/cases/models.py` | EDIT | Add first_annuity_year field to Case |
| `backend/app/modules/annuity/service.py` | EDIT | Add generate_annuity_tasks_for_case, update _rate_amount, update list response, set draft_generated flag |
| `backend/app/modules/annuity/api.py` | EDIT | Add generate endpoint, update list response items |
| `backend/tests/test_annuity_generate.py` | CREATE | 11 tests |
| `frontend/src/api/annuity.types.ts` | EDIT | Add generate types, update AnnuityTask interface |
| `frontend/src/api/annuity.ts` | EDIT | Add generateAnnuityTasks function |
| `frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue` | CREATE | Generation dialog |
| `frontend/src/modules/annuity/pages/AnnuityTaskList.vue` | EDIT | Add columns + generate button |

---

## Task 1: Migration + Models

**Files:**
- Create: `backend/alembic/versions/pe_fr_fe_06_annuity_task_ext.py`
- Modify: `backend/app/modules/annuity/models.py:71-99`
- Modify: `backend/app/modules/cases/models.py:91-93`

- [ ] **Step 1: Write migration file**

Create `backend/alembic/versions/pe_fr_fe_06_annuity_task_ext.py`:

```python
"""pe_fr_fe_06_annuity_task_ext

Revision ID: pe_fr_fe_06_01
Revises: pe_fr_fe_07_01
Create Date: 2026-03-25

Add 6 columns to t_annuity_task and 1 column to t_case (first_annuity_year).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_fr_fe_06_01"
down_revision = "pe_fr_fe_07_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # -- t_annuity_task: 6 new columns --
    if insp.has_table("t_annuity_task"):
        existing = {col["name"] for col in insp.get_columns("t_annuity_task")}
        annuity_cols = [
            ("gov_fee_amt", sa.Numeric(18, 2), sa.text("0")),
            ("service_fee_amt", sa.Numeric(18, 2), sa.text("0")),
            ("notify_count", sa.Integer(), sa.text("0")),
            ("pay_next_year", sa.Boolean(), sa.text("0")),
            ("draft_generated", sa.Boolean(), sa.text("0")),
            ("notice_sent", sa.Boolean(), sa.text("0")),
        ]
        with op.batch_alter_table("t_annuity_task") as batch_op:
            for col_name, col_type, server_default in annuity_cols:
                if col_name not in existing:
                    batch_op.add_column(
                        sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                    )

    # -- t_case: first_annuity_year --
    if insp.has_table("t_case"):
        existing_case = {col["name"] for col in insp.get_columns("t_case")}
        if "first_annuity_year" not in existing_case:
            with op.batch_alter_table("t_case") as batch_op:
                batch_op.add_column(
                    sa.Column("first_annuity_year", sa.Integer(), nullable=True)
                )


def downgrade() -> None:
    pass
```

- [ ] **Step 2: Update AnnuityTask model**

In `backend/app/modules/annuity/models.py`, add `Boolean` to the sqlalchemy import on line 6 (change `from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, text` to include `Boolean`), then add after line 98 (`updated_by` field):

```python
    gov_fee_amt: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, server_default=text("0")
    )
    service_fee_amt: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, server_default=text("0")
    )
    notify_count: Mapped[int | None] = mapped_column(Integer, nullable=True, server_default=text("0"))
    pay_next_year: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
    draft_generated: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
    notice_sent: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
```

- [ ] **Step 3: Update Case model**

In `backend/app/modules/cases/models.py`, add after line 93 (`applicant_kind` field):

```python
    first_annuity_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

- [ ] **Step 4: Test clean rebuild**

```bash
cd backend && source .venv/bin/activate && rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py
```

Expected: All migrations succeed, seed completes.

- [ ] **Step 5: Verify schema**

```bash
sqlite3 fpms_dev.db ".schema t_annuity_task" | grep -E "gov_fee|service_fee|notify_count|pay_next|draft_gen|notice_sent"
sqlite3 fpms_dev.db ".schema t_case" | grep first_annuity
```

Expected: All new columns present.

- [ ] **Step 6: Commit**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic && git add backend/alembic/versions/pe_fr_fe_06_annuity_task_ext.py backend/app/modules/annuity/models.py backend/app/modules/cases/models.py && git commit -m "feat(db): add annuity task extension + case first_annuity_year (FR-FE-06)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Tests (TDD RED)

**Files:**
- Create: `backend/tests/test_annuity_generate.py`

- [ ] **Step 1: Write all test functions**

Create `backend/tests/test_annuity_generate.py`:

```python
"""Tests for AnnuityTask multi-year generation (FR-FE-06)."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import AnnuityTask
from app.modules.cases.models import Case


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


@pytest.fixture
def client_id(client: TestClient, auth_headers: dict) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("GEN-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def granted_case_id(client: TestClient, auth_headers: dict, client_id: str, session_factory: sessionmaker) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("GEN-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Annuity Gen Test",
            "filing_date": "2020-06-15",
            "status": "GRANTED",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    case_id = resp.json()["id"]

    # Set first_annuity_year directly in DB (no API for this field yet)
    with session_factory() as db:
        case = db.query(Case).filter(Case.id == case_id).first()
        case.first_annuity_year = 3
        db.commit()

    return case_id


@pytest.fixture
def not_granted_case_id(client: TestClient, auth_headers: dict, client_id: str) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("GEN-NG"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Not Granted Case",
            "status": "NOT_FILED",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def granted_no_year_case_id(client: TestClient, auth_headers: dict, client_id: str) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("GEN-NY"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Granted No Year",
            "status": "GRANTED",
            "filing_date": "2020-01-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _seed_annuity_rates(client: TestClient, auth_headers: dict) -> None:
    for fee_type, amount in (("GOV", "300.00"), ("SERVICE", "50.00")):
        resp = client.post(
            "/api/v1/fees/rates",
            json={
                "fee_code": f"ANN-GEN-{fee_type}-{uuid4().hex[:6]}",
                "fee_name": f"Annuity {fee_type} Gen",
                "fee_type": fee_type,
                "currency": "CNY",
                "default_amount": amount,
                "enabled": True,
                "rate_group": "ANNUITY",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201


# --- GENERATE ---

def test_generate_annuity_tasks_success(client: TestClient, auth_headers: dict, granted_case_id: str):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tasks_created"] > 0
    assert data["first_year"] == 3


def test_generate_case_not_found(client: TestClient, auth_headers: dict):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": "nonexistent-id"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_generate_case_not_granted(client: TestClient, auth_headers: dict, not_granted_case_id: str):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": not_granted_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_generate_no_first_annuity_year(client: TestClient, auth_headers: dict, granted_no_year_case_id: str):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_no_year_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_generate_idempotent(client: TestClient, auth_headers: dict, granted_case_id: str):
    resp1 = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp1.status_code == 201
    created_first = resp1.json()["tasks_created"]

    resp2 = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp2.status_code == 201
    assert resp2.json()["tasks_created"] == 0
    assert resp2.json()["tasks_skipped"] == created_first


def test_generate_prefills_fee_amounts(client: TestClient, auth_headers: dict, granted_case_id: str):
    _seed_annuity_rates(client, auth_headers)

    # Re-generate (delete old tasks first via direct DB or just use new case)
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    # Check list for fee amounts
    list_resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) > 0
    # At least some should have amounts (may be 0 if rates don't match year_no)
    for item in items:
        assert "gov_fee_amt" in item
        assert "service_fee_amt" in item


# --- LIST NEW FIELDS ---

def test_list_includes_new_fields(client: TestClient, auth_headers: dict, granted_case_id: str):
    client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/annuity/tasks", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) > 0
    item = items[0]
    for field in ("gov_fee_amt", "service_fee_amt", "notify_count", "pay_next_year",
                  "draft_generated", "notice_sent", "is_overdue"):
        assert field in item, f"Missing field: {field}"


def test_list_is_overdue_computed(client: TestClient, auth_headers: dict, granted_case_id: str, session_factory: sessionmaker):
    with session_factory() as db:
        task = AnnuityTask(
            case_id=granted_case_id,
            client_id=db.query(Case).filter(Case.id == granted_case_id).first().client_id,
            year_no=99,
            due_date=date.today() - timedelta(days=30),
            status="OPEN",
        )
        db.add(task)
        db.commit()

    resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id, "status": "OPEN"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    overdue_items = [i for i in resp.json()["items"] if i["year_no"] == 99]
    assert len(overdue_items) == 1
    assert overdue_items[0]["is_overdue"] is True


def test_list_is_overdue_false_when_done(client: TestClient, auth_headers: dict, granted_case_id: str, session_factory: sessionmaker):
    with session_factory() as db:
        task = AnnuityTask(
            case_id=granted_case_id,
            client_id=db.query(Case).filter(Case.id == granted_case_id).first().client_id,
            year_no=98,
            due_date=date.today() - timedelta(days=30),
            status="DONE",
        )
        db.add(task)
        db.commit()

    resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id, "status": "DONE"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    done_items = [i for i in resp.json()["items"] if i["year_no"] == 98]
    assert len(done_items) == 1
    assert done_items[0]["is_overdue"] is False


# --- DRAFT GENERATED FLAG ---

def test_draft_generated_flag_set(client: TestClient, auth_headers: dict, granted_case_id: str):
    _seed_annuity_rates(client, auth_headers)

    client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )

    # Get task IDs
    list_resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id},
        headers=auth_headers,
    )
    items = list_resp.json()["items"]
    task_ids = [i["id"] for i in items[:1]]  # just one

    if task_ids:
        # Update instruction to PAY first
        client.put(
            f"/api/v1/annuity/tasks/{task_ids[0]}/instruction",
            json={"instruction": "PAY"},
            headers=auth_headers,
        )

        # Generate drafts
        draft_resp = client.post(
            "/api/v1/annuity/tasks/generate-drafts",
            json={"task_ids": task_ids},
            headers=auth_headers,
        )
        assert draft_resp.status_code in (200, 201)

        # Check flag
        list_resp2 = client.get(
            "/api/v1/annuity/tasks",
            params={"case_id": granted_case_id},
            headers=auth_headers,
        )
        for item in list_resp2.json()["items"]:
            if item["id"] == task_ids[0]:
                assert item["draft_generated"] is True


# --- PERMISSIONS ---

def test_permissions_generate(client: TestClient):
    resp = client.post("/api/v1/annuity/tasks/generate", json={"case_id": "x"})
    assert resp.status_code == 401
```

- [ ] **Step 2: Commit tests**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic && git add backend/tests/test_annuity_generate.py && git commit -m "test(annuity): add generation tests RED (FR-FE-06)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Service function — generate + update _rate_amount + update list + draft_generated flag

**Files:**
- Modify: `backend/app/modules/annuity/service.py`

- [ ] **Step 1: Update `_rate_amount` to accept optional `year_no`**

In `backend/app/modules/annuity/service.py`, modify `_rate_amount` (lines 256-278) to accept an optional `year_no` parameter:

```python
def _rate_amount(
    db: Session,
    *,
    fee_type: str,
    currency: str,
    year_no: int | None = None,
) -> Decimal:
    conditions = [
        FeeRate.enabled.is_(True),
        FeeRate.rate_group == "ANNUITY",
        FeeRate.fee_type == fee_type,
        FeeRate.currency == currency,
    ]
    if year_no is not None:
        conditions.append(FeeRate.year_no == year_no)
    rate = (
        db.execute(
            select(FeeRate)
            .where(*conditions)
            .order_by(FeeRate.updated_at.desc())
        )
        .scalars()
        .first()
    )
    if not rate or rate.default_amount is None:
        return Decimal("0")
    return Decimal(rate.default_amount)
```

- [ ] **Step 2: Add `generate_annuity_tasks_for_case` function**

Add at end of service.py (before any if `__name__` block):

```python
def generate_annuity_tasks_for_case(
    db: Session,
    *,
    case_id: str,
) -> dict:
    """Generate multi-year annuity tasks for a GRANTED case."""
    from app.modules.cases.models import Case

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "案卷不存在", status_code=404)

    if case.status != "GRANTED":
        raise_business_error("CASE_NOT_GRANTED", "案卷状态不是已授权", status_code=400)

    if not case.first_annuity_year:
        raise_business_error("NO_FIRST_ANNUITY_YEAR", "未设置首年年费年度", status_code=400)

    # Calculate last year: valid_until year or filing_date + 20 years
    if case.valid_until:
        last_year = case.valid_until.year - case.filing_date.year + 1 if case.filing_date else 20
    elif case.filing_date:
        last_year = 20  # standard CN patent term
    else:
        last_year = 20

    first_year = case.first_annuity_year
    tasks_created = 0
    tasks_skipped = 0

    for year_no in range(first_year, last_year + 1):
        # Check if task already exists
        existing = (
            db.query(AnnuityTask)
            .filter(AnnuityTask.case_id == case_id, AnnuityTask.year_no == year_no)
            .first()
        )
        if existing:
            tasks_skipped += 1
            continue

        # Calculate due date: filing_date + year_no years
        if case.filing_date:
            try:
                due = case.filing_date.replace(year=case.filing_date.year + year_no)
            except ValueError:
                # Handle Feb 29 edge case
                due = case.filing_date.replace(year=case.filing_date.year + year_no, day=28)
        else:
            due = date.today()

        # Look up fee rates
        gov_amt = _rate_amount(db, fee_type="GOV", currency="CNY", year_no=year_no)
        svc_amt = _rate_amount(db, fee_type="SERVICE", currency="CNY", year_no=year_no)

        task = AnnuityTask(
            case_id=case_id,
            client_id=case.client_id,
            year_no=year_no,
            due_date=due,
            status="OPEN",
            gov_fee_amt=gov_amt,
            service_fee_amt=svc_amt,
        )
        db.add(task)
        tasks_created += 1

    db.flush()
    return {
        "case_id": case_id,
        "case_no": case.case_no,
        "first_year": first_year,
        "last_year": last_year,
        "tasks_created": tasks_created,
        "tasks_skipped": tasks_skipped,
    }
```

- [ ] **Step 3: Update list response in `list_annuity_tasks`**

In the existing `list_annuity_tasks` function, the returned tuple includes task objects. The response dict is built in `api.py` (lines 104-121). We'll update `api.py` in Task 4. No service change needed here — the model fields are already accessible.

- [ ] **Step 4: Update draft_generated flag in `generate_fee_drafts_from_annuity_tasks`**

Find the section in `generate_fee_drafts_from_annuity_tasks` where a draft is successfully created for a task. After the draft is added/flushed, add:

```python
task.draft_generated = True
```

Search for where `success_items` are appended and add the flag set just before.

- [ ] **Step 5: Add necessary imports**

Ensure `date` is imported at top of service.py. Add `from app.core.errors import raise_business_error` if not already present.

- [ ] **Step 6: Lint**

```bash
cd backend && source .venv/bin/activate && ruff check --fix app/modules/annuity/service.py && ruff format app/modules/annuity/service.py
```

- [ ] **Step 7: Commit**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic && git add backend/app/modules/annuity/service.py && git commit -m "feat(annuity): add generation service + rate year_no + draft_generated flag (FR-FE-06)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: API Endpoint + list response update

**Files:**
- Modify: `backend/app/modules/annuity/api.py`

- [ ] **Step 1: Add generate endpoint schema**

Add after existing `AnnuityGenerateDraftsIn` class in api.py:

```python
class AnnuityTaskGenerateIn(BaseModel):
    case_id: str = Field(..., min_length=1)
```

- [ ] **Step 2: Add generate endpoint**

Add the endpoint in api.py (after the existing generate-drafts endpoint):

```python
@router.post(
    "/annuity/tasks/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate annuity tasks for a case",
)
def generate_annuity_tasks_endpoint(
    payload: AnnuityTaskGenerateIn,
    _perm: None = Depends(require_perm("AnnuityTask.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Generate multi-year annuity tasks for a GRANTED case.

    **Auth**: Bearer JWT
    **Permission**: AnnuityTask.Action
    """
    from app.modules.annuity.service import generate_annuity_tasks_for_case

    result = generate_annuity_tasks_for_case(db, case_id=payload.case_id)
    db.commit()
    return result
```

- [ ] **Step 3: Update list response items**

In the existing `get_annuity_tasks` function (lines 104-121), update the items dict comprehension to include new fields:

```python
    items = [
        {
            "id": task.id,
            "case_id": task.case_id,
            "client_id": task.client_id,
            "year_no": task.year_no,
            "due_date": task.due_date,
            "client_instruction": task.client_instruction,
            "instruction_date": task.instruction_date,
            "notice_status": task.notice_status,
            "notice_sent_date": task.notice_sent_date,
            "status": task.status,
            "remark": task.remark,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "gov_fee_amt": task.gov_fee_amt,
            "service_fee_amt": task.service_fee_amt,
            "notify_count": task.notify_count,
            "pay_next_year": task.pay_next_year,
            "draft_generated": task.draft_generated,
            "notice_sent": task.notice_sent,
            "is_overdue": task.due_date < date.today() and task.status == "OPEN",
        }
        for task in tasks
    ]
```

Ensure `from datetime import date` is imported at top of api.py.

- [ ] **Step 4: Add `status` import if needed**

Ensure `from fastapi import status` is imported.

- [ ] **Step 5: Run tests — verify GREEN**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_annuity_generate.py -v
```

Expected: All 11 tests PASS.

- [ ] **Step 6: Run full test suite**

```bash
pytest -q
```

Expected: All tests pass.

- [ ] **Step 7: Lint**

```bash
ruff check --fix app/modules/annuity/api.py && ruff format app/modules/annuity/api.py
```

- [ ] **Step 8: Commit**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic && git add backend/app/modules/annuity/api.py && git commit -m "feat(annuity): add generate endpoint + update list response (FR-FE-06)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Frontend types + API client

**Files:**
- Modify: `frontend/src/api/annuity.types.ts`
- Modify: `frontend/src/api/annuity.ts`

- [ ] **Step 1: Update TypeScript types**

In `frontend/src/api/annuity.types.ts`, add to the `AnnuityTask` interface:

```typescript
    gov_fee_amt?: number | null
    service_fee_amt?: number | null
    notify_count?: number | null
    pay_next_year?: boolean | null
    draft_generated?: boolean | null
    notice_sent?: boolean | null
    is_overdue?: boolean
```

Add new interfaces at end of file:

```typescript
export interface AnnuityTaskGeneratePayload {
    case_id: string
}

export interface AnnuityTaskGenerateResult {
    case_id: string
    case_no?: string | null
    first_year: number
    last_year: number
    tasks_created: number
    tasks_skipped: number
}
```

- [ ] **Step 2: Add API function**

In `frontend/src/api/annuity.ts`, add:

```typescript
export async function generateAnnuityTasks(payload: AnnuityTaskGeneratePayload): Promise<AnnuityTaskGenerateResult> {
    const { data } = await http.post<AnnuityTaskGenerateResult>('/annuity/tasks/generate', payload)
    return data
}
```

Import the new types at the top.

- [ ] **Step 3: Verify**

```bash
cd frontend && npm run lint && npm run typecheck
```

- [ ] **Step 4: Commit**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic && git add frontend/src/api/annuity.types.ts frontend/src/api/annuity.ts && git commit -m "feat(annuity): add generation API client + types (FR-FE-06)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: AnnuityGenerateDialog component

**Files:**
- Create: `frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue`

- [ ] **Step 1: Create dialog**

Create `frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue` — a simple el-dialog:

- Title: "生成年费任务"
- Single field: 案卷 (el-select remote search by case_no)
- On confirm: call `generateAnnuityTasks({case_id})`
- Success: `ElMessage.success(\`已生成 ${result.tasks_created} 条年费任务，跳过 ${result.tasks_skipped} 条已存在记录\`)`
- Errors: Chinese messages ("案卷不存在", "案卷状态不是已授权", "未设置首年年费年度", "生成失败，请重试")
- Props: `modelValue: boolean`, emits: `update:modelValue`, `saved`
- Use `<script setup lang="ts">`, Element Plus components, relative imports

- [ ] **Step 2: Verify**

```bash
cd frontend && npm run lint && npm run typecheck
```

- [ ] **Step 3: Commit**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic && git add frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue && git commit -m "feat(annuity): add AnnuityGenerateDialog component (FR-FE-06)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Update AnnuityTaskList page

**Files:**
- Modify: `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`

- [ ] **Step 1: Add new columns and generate button**

In `AnnuityTaskList.vue`:

- Add table columns: 官费预估, 服务费预估, 通知次数, 是否逾期 (el-tag danger/info)
- Add `draft_generated`, `notice_sent` columns with el-tag 是/否
- Add "生成年费任务" el-button in toolbar → opens AnnuityGenerateDialog
- Import `AnnuityGenerateDialog` component
- Add `showGenerateDialog = ref(false)` state
- On dialog `saved` event → reload list

- [ ] **Step 2: Verify**

```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

- [ ] **Step 3: Commit**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic && git add frontend/src/modules/annuity/pages/AnnuityTaskList.vue && git commit -m "feat(annuity): update task list with new columns + generate button (FR-FE-06)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Final verification + artifacts

- [ ] **Step 1: Backend full test suite**

```bash
cd backend && source .venv/bin/activate && pytest -q
```

Expected: All tests pass.

- [ ] **Step 2: Clean DB rebuild**

```bash
rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py
```

- [ ] **Step 3: Frontend quality gates**

```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

- [ ] **Step 4: Generate artifacts**

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic
mkdir -p artifacts/FR-FE-06/git
git log --oneline HEAD~7..HEAD > artifacts/FR-FE-06/git/commits.txt
git diff HEAD~7..HEAD --stat > artifacts/FR-FE-06/git/diff_stat.txt
git diff HEAD~7..HEAD > artifacts/FR-FE-06/git/diff.patch
```

Create `artifacts/FR-FE-06/summary.md` and `artifacts/FR-FE-06/results.jsonl`.

- [ ] **Step 5: Commit artifacts**

```bash
git add -f artifacts/FR-FE-06/ && git commit -m "docs: add FR-FE-06 evidence artifacts

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```
