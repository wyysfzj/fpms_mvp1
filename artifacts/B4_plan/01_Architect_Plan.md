# B4 — FeeRate Dimensions + CalcMode Stub — Implementation Plan

> Architect: architect-agent
> Date: 2026-02-26
> Status: READY FOR APPROVAL

---

## 1. Current State Analysis

### 1.1 T_FeeRate Model (`backend/app/modules/fees/models.py:64-75`)

Current columns:
| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | String(36) | PK | uuid4() (via UUIDPrimaryKeyMixin) |
| fee_code | String(64) | NOT NULL | — |
| fee_name | String(256) | nullable | — |
| fee_type | String(16) | NOT NULL | 'SERVICE' |
| currency | String(8) | NOT NULL | 'CNY' |
| default_amount | Numeric(18,2) | nullable | — |
| enabled | Boolean | NOT NULL | 1 (true) |
| created_at, updated_at, created_by, updated_by | (via AuditMixin) |

### 1.2 FeeRate Schemas (`backend/app/modules/fees/schemas.py`)

- **FeeRateCreateIn** (L83-89): fee_code, fee_name, fee_type, currency, default_amount, enabled
- **FeeRateUpdateIn** (L92-97): fee_name?, fee_type?, currency?, default_amount?, enabled?
- **FeeRateOut** (L100-109): id, fee_code, fee_name, fee_type, currency, default_amount?, enabled

### 1.3 Fee Service (`backend/app/modules/fees/service.py`)

Relevant functions:
- `list_fee_rates()` (L254-283): filters by fee_code, fee_type, currency, enabled
- `create_fee_rate()` (L286-299): creates with current 6 fields
- `update_fee_rate()` (L302-319): generic model_dump + setattr loop

### 1.4 Fee Enums (`backend/app/modules/fees/enums.py`)

- `FeeType`: GOV, SERVICE, MISC
- `FeeDraftStatus`: OPEN, LOCKED
- **No CalcMode enum exists yet**

### 1.5 Case Model (for calc_fee_amount reference)

`T_Case` has fields relevant to fee calculation:
- `case_type` (String(32), default 'NORMAL')
- `patent_category` (String(32), default 'INV')
- `fee_reduction` (String(32), nullable)
- `claim_count` (Integer, nullable)
- `spec_pages` (Integer, nullable)

### 1.6 Migration Chain

```
0004_fees → ... → a3_case_fields_01 → b1_doc_tpl_01 → b2_doc_reply_01
                                                         ↑ (current HEAD)
```

New migration will be: `b4_fee_rate_dims_01` (depends on `b2_doc_reply_01`)

---

## 2. Deliverables Overview

| # | Deliverable | Files Changed |
|---|------------|--------------|
| D1 | Alembic migration: 9 new columns on t_fee_rate | `alembic/versions/b4_fee_rate_dimensions.py` (NEW) |
| D2 | CalcMode enum | `app/modules/fees/enums.py` |
| D3 | Model: 9 new fields on FeeRate | `app/modules/fees/models.py` |
| D4 | Schemas: expose new fields in Create/Update/Out | `app/modules/fees/schemas.py` |
| D5 | Service: add new filter params + calculate_fee_amount stub | `app/modules/fees/service.py` |
| D6 | API: add new query params for list_fee_rates | `app/modules/fees/api.py` |
| D7 | Tests | `tests/test_b4_fee_rate_dims.py` (NEW) |

---

## 3. Task Decomposition

### Task 2A — Migration (Backend Agent)

**File**: `backend/alembic/versions/b4_fee_rate_dimensions.py` (NEW)

```python
"""b4_fee_rate_dimensions

Revision ID: b4_fee_rate_dims_01
Revises: b2_doc_reply_01
Create Date: 2026-02-26

Add 9 dimension/calc columns to t_fee_rate.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b4_fee_rate_dims_01"
down_revision = "b2_doc_reply_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_fee_rate"):
        return

    existing = {col["name"] for col in insp.get_columns("t_fee_rate")}

    columns = [
        ("rate_group", sa.String(32), None),
        ("country_code", sa.String(10), None),
        ("case_type", sa.String(32), None),
        ("patent_category", sa.String(32), None),
        ("calc_mode", sa.String(16), sa.text("'FIXED'")),
        ("calc_params", sa.Text(), None),
        ("allow_reduction", sa.Boolean(), sa.text("0")),
        ("effective_from", sa.Date(), None),
        ("effective_to", sa.Date(), None),
    ]

    with op.batch_alter_table("t_fee_rate") as batch_op:
        for col_name, col_type, server_default in columns:
            if col_name not in existing:
                batch_op.add_column(
                    sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                )


def downgrade() -> None:
    pass
```

### Task 2B — Enum (Backend Agent)

**File**: `backend/app/modules/fees/enums.py`

Add `CalcMode` enum:

```python
class CalcMode(str, Enum):
    FIXED = "FIXED"
    PER_CLAIM = "PER_CLAIM"
    PER_PAGE = "PER_PAGE"
    TIER = "TIER"
```

### Task 2C — Model Changes (Backend Agent)

**File**: `backend/app/modules/fees/models.py`

Add 9 new fields to `FeeRate` class (after `enabled` field, before class end):

```python
from sqlalchemy import Date  # add to existing imports

# Inside FeeRate class, after enabled field:
rate_group: Mapped[str | None] = mapped_column(String(32), nullable=True)
country_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
case_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
patent_category: Mapped[str | None] = mapped_column(String(32), nullable=True)
calc_mode: Mapped[str | None] = mapped_column(
    String(16), nullable=True, server_default=text("'FIXED'")
)
calc_params: Mapped[str | None] = mapped_column(Text, nullable=True)
allow_reduction: Mapped[bool | None] = mapped_column(
    Boolean, nullable=True, server_default=text("0")
)
effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
```

**Import additions**: `from datetime import date` and `Date` from sqlalchemy.

### Task 2D — Schema Changes (Backend Agent)

**File**: `backend/app/modules/fees/schemas.py`

#### FeeRateCreateIn — add optional fields:

```python
from datetime import date as date_type
from app.modules.fees.enums import CalcMode  # add to imports

class FeeRateCreateIn(BaseModel):
    fee_code: str
    fee_name: str
    fee_type: FeeType
    currency: str
    default_amount: Decimal
    enabled: bool = True
    # New B4 fields (all optional for backward compatibility)
    rate_group: str | None = None
    country_code: str | None = None
    case_type: str | None = None
    patent_category: str | None = None
    calc_mode: CalcMode | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None
```

#### FeeRateUpdateIn — add optional fields:

```python
class FeeRateUpdateIn(BaseModel):
    fee_name: str | None = None
    fee_type: FeeType | None = None
    currency: str | None = None
    default_amount: Decimal | None = None
    enabled: bool | None = None
    # New B4 fields
    rate_group: str | None = None
    country_code: str | None = None
    case_type: str | None = None
    patent_category: str | None = None
    calc_mode: CalcMode | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None
```

#### FeeRateOut — add fields to response:

```python
class FeeRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    fee_code: str
    fee_name: str
    fee_type: FeeType
    currency: str
    default_amount: Decimal | None = None
    enabled: bool
    # New B4 fields
    rate_group: str | None = None
    country_code: str | None = None
    case_type: str | None = None
    patent_category: str | None = None
    calc_mode: str | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None
```

### Task 2E — Service Changes (Backend Agent)

**File**: `backend/app/modules/fees/service.py`

#### 2E.1 — Update `list_fee_rates()` to accept new filter params:

Add filters for `rate_group`, `country_code`, `case_type`, `patent_category`, `calc_mode`:

```python
# Inside list_fee_rates, after existing filters:
rate_group = filters.get("rate_group")
country_code = filters.get("country_code")
case_type = filters.get("case_type")
patent_category = filters.get("patent_category")
calc_mode = filters.get("calc_mode")

if rate_group:
    stmt = stmt.where(FeeRate.rate_group == rate_group)
if country_code:
    stmt = stmt.where(FeeRate.country_code == country_code)
if case_type:
    stmt = stmt.where(FeeRate.case_type == case_type)
if patent_category:
    stmt = stmt.where(FeeRate.patent_category == patent_category)
if calc_mode:
    stmt = stmt.where(FeeRate.calc_mode == calc_mode)
```

#### 2E.2 — Update `create_fee_rate()` to pass new fields:

The existing generic approach of passing `data` fields into the constructor already works since `data.model_dump()` isn't used — fields are set explicitly. We need to add the new fields:

```python
def create_fee_rate(db: Session, *, data: FeeRateCreateIn, actor_id: str | None) -> FeeRate:
    rate = FeeRate(
        id=str(uuid4()),
        fee_code=data.fee_code,
        fee_name=data.fee_name,
        fee_type=data.fee_type,
        currency=data.currency,
        default_amount=data.default_amount,
        enabled=data.enabled if data.enabled is not None else True,
        # New B4 fields
        rate_group=data.rate_group,
        country_code=data.country_code,
        case_type=data.case_type,
        patent_category=data.patent_category,
        calc_mode=data.calc_mode.value if data.calc_mode else None,
        calc_params=data.calc_params,
        allow_reduction=data.allow_reduction,
        effective_from=data.effective_from,
        effective_to=data.effective_to,
    )
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate
```

#### 2E.3 — Add `calculate_fee_amount()` stub:

```python
import logging

logger = logging.getLogger(__name__)

def calculate_fee_amount(rate: FeeRate, case: Case | None = None) -> Decimal:
    """Calculate fee amount based on rate's calc_mode.

    Currently only FIXED mode is implemented.
    Other modes (PER_CLAIM, PER_PAGE, TIER) return default_amount with a TODO log.
    """
    amount = rate.default_amount if rate.default_amount is not None else Decimal("0")
    calc_mode = getattr(rate, "calc_mode", None) or "FIXED"

    if calc_mode == "FIXED":
        return amount

    # Stub: log and return default for unimplemented modes
    logger.warning(
        "calculate_fee_amount: calc_mode=%s not yet implemented for rate=%s, "
        "returning default_amount=%s",
        calc_mode,
        rate.fee_code,
        amount,
    )
    return amount
```

### Task 2F — API Changes (Backend Agent)

**File**: `backend/app/modules/fees/api.py`

Update `get_fee_rates()` endpoint to accept new query parameters:

```python
@router.get("/fees/rates", summary="List fee rates")
def get_fee_rates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    fee_code: str | None = Query(default=None),
    fee_type: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    # New B4 filters
    rate_group: str | None = Query(default=None),
    country_code: str | None = Query(default=None),
    case_type: str | None = Query(default=None),
    patent_category: str | None = Query(default=None),
    calc_mode: str | None = Query(default=None),
    _perm: None = Depends(require_perm("FeeRate.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    filters = {
        "fee_code": fee_code,
        "fee_type": fee_type,
        "currency": currency,
        "enabled": enabled,
        "rate_group": rate_group,
        "country_code": country_code,
        "case_type": case_type,
        "patent_category": patent_category,
        "calc_mode": calc_mode,
    }
    rates, total = list_fee_rates(db, filters=filters, page=page, page_size=page_size)
    items = [FeeRateOut.model_validate(rate) for rate in rates]
    return {"items": items, "page": page, "page_size": page_size, "total": total}
```

### Task 3 — Tests (Test Agent)

**File**: `backend/tests/test_b4_fee_rate_dims.py` (NEW)

#### Test Plan:

| # | Test Name | Purpose |
|---|----------|---------|
| T1 | `test_create_fee_rate_with_dimensions` | Create rate with all 9 new fields, verify response contains them |
| T2 | `test_create_fee_rate_without_dimensions` | Create rate without new fields (backward compat), verify defaults |
| T3 | `test_update_fee_rate_dimensions` | Update rate with new dimension fields |
| T4 | `test_list_fee_rates_filter_by_rate_group` | Filter rates by rate_group |
| T5 | `test_list_fee_rates_filter_by_country_code` | Filter rates by country_code |
| T6 | `test_list_fee_rates_filter_by_calc_mode` | Filter rates by calc_mode |
| T7 | `test_calc_fee_amount_fixed_mode` | calculate_fee_amount with FIXED mode returns default_amount |
| T8 | `test_calc_fee_amount_fixed_is_default` | Rate with no calc_mode falls back to FIXED |
| T9 | `test_calc_fee_amount_per_claim_stub` | PER_CLAIM mode returns default_amount (stub) |
| T10 | `test_calc_fee_amount_none_default_amount` | Rate with None default_amount returns Decimal("0") |
| T11 | `test_fee_rate_out_schema_has_new_fields` | FeeRateOut response schema includes all 9 new fields |

#### Test Helpers:

```python
RATE_BASE = "/api/v1/fees/rates"

def _unique(prefix: str = "B4") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

def _create_rate(client, auth_headers, **overrides) -> dict:
    payload = {
        "fee_code": _unique("RATE"),
        "fee_name": "Test Rate",
        "fee_type": "SERVICE",
        "currency": "CNY",
        "default_amount": "100.00",
        "enabled": True,
        **overrides,
    }
    resp = client.post(RATE_BASE, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Rate creation failed: {resp.text}"
    return resp.json()
```

#### Key Test — calculate_fee_amount (unit test, no HTTP):

```python
def test_calc_fee_amount_fixed_mode(session_factory):
    from app.modules.fees.models import FeeRate
    from app.modules.fees.service import calculate_fee_amount

    rate = FeeRate(
        id=str(uuid4()),
        fee_code="TEST",
        fee_type="SERVICE",
        currency="CNY",
        default_amount=Decimal("250.00"),
        calc_mode="FIXED",
    )
    result = calculate_fee_amount(rate)
    assert result == Decimal("250.00")
```

---

## 4. Dependency Graph

```
Task 2A (Migration)  ──┐
Task 2B (Enum)       ──┤
                        ├──→ Task 2C (Model) ──→ Task 2D (Schema) ──→ Task 2E (Service) ──→ Task 2F (API)
                        │
                        │    (can start after 2E)
                        └──→ Task 3 (Tests)
```

**Practical sequencing**: All of 2A-2F should be done by a single Backend Agent in order (they're small, interdependent). Task 3 (Tests) can be done in parallel by Test Agent once the plan is approved — they only need to read the plan, not wait for impl.

---

## 5. File-by-File Change Summary

| File | Action | Lines Changed (est.) |
|------|--------|---------------------|
| `alembic/versions/b4_fee_rate_dimensions.py` | **NEW** | ~50 lines |
| `app/modules/fees/enums.py` | EDIT — add CalcMode enum | +7 lines |
| `app/modules/fees/models.py` | EDIT — add 9 fields + imports | +15 lines |
| `app/modules/fees/schemas.py` | EDIT — add fields to 3 schemas + imports | +30 lines |
| `app/modules/fees/service.py` | EDIT — extend filters, create, add calc stub | +40 lines |
| `app/modules/fees/api.py` | EDIT — add 5 query params + filter dict entries | +15 lines |
| `tests/test_b4_fee_rate_dims.py` | **NEW** | ~200 lines |

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Migration fails on existing DB | Low | High | Idempotent `_col_exists` check; all columns nullable |
| calc_mode enum mismatch (Pydantic vs DB) | Medium | Low | Schema uses `CalcMode | None`, DB stores as string |
| calc_params JSON not validated | Expected | None | By design — not parsed in B4, just stored as Text |
| Backward compatibility break | Low | Medium | All new fields optional/nullable in all schemas |
| Test isolation (session-scoped DB) | Low | Low | Use unique fee_code per test via `_unique()` helper |

---

## 7. Quality Gate

After implementation:
```bash
cd backend
rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py
pytest --tb=short
ruff check --fix . && ruff format .
```

---

## 8. Non-Scope (Explicitly Excluded)

- No actual PER_CLAIM / PER_PAGE / TIER calculation logic
- No UI/frontend changes
- No calc_params JSON schema validation
- No index additions on new columns (can be added later if needed)
- No changes to FeeItem or FeeDraft models
