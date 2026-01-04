#!/usr/bin/env python3
"""
Generate remaining atomic task files for MVP1 enhancement.
This script creates the 90+ remaining task files following the established format.

Usage:
    cd tasks/backend/mvp1enhance
    python generate_remaining_tasks.py
"""

import os
from pathlib import Path

# Base directory for task files
TASK_DIR = Path(__file__).parent

# Complete task template definitions
TASK_TEMPLATES = {
    # ========== Phase 3b: Billing Module (10 files) ==========
    "ENH-03-01": {
        "title": "Create billing Pydantic schemas",
        "file": "backend/app/modules/billing/schemas.py",
        "prereq": "None",
        "scope": "Create ALL Pydantic schemas for billing module in ONE task.",
        "components": """```python
class BillCreate(BaseModel):
    fee_draft_ids: list[str]
    client_id: str
    currency: str = "CNY"

class BillOut(BaseModel):
    id: str
    bill_no: str
    client_id: str
    currency: str
    total_amount: Decimal
    status: str
    items: list[dict]

class BillListItem(BaseModel):
    id: str
    bill_no: str
    client_id: str
    total_amount: Decimal
    status: str

class PaymentCreate(BaseModel):
    payment_no: str
    payer: str
    amount: Decimal
    currency: str = "CNY"
    payment_date: date

class PaymentOut(BaseModel):
    id: str
    payment_no: str
    amount: Decimal
    currency: str
    
class OffsetCreate(BaseModel):
    payment_id: str
    bill_id: str
    offset_amount: Decimal

class ManualBillCreate(BaseModel):
    client_id: str
    currency: str
    items: list[dict]  # ManualBillItemIn
```""",
        "priority": "P0",
        "validation": "python -c \"from app.modules.billing.schemas import BillCreate, PaymentCreate; print('OK')\""
    },
    
    "ENH-03-02": {
        "title": "Implement validate_single_client helper",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "None",
        "scope": "Implement ONLY validate_single_client() to ensure all fee drafts belong to same client.",
        "components": """```python
def validate_single_client(db: Session, draft_ids: list[str]) -> str:
    \"\"\"Validate all drafts belong to single client. Returns client_id.\"\"\"
    from app.modules.fees.models import FeeDraft
    
    drafts = db.query(FeeDraft).filter(FeeDraft.id.in_(draft_ids)).all()
    
    if not drafts:
        raise_business_error("NO_DRAFTS", "No fee drafts found", 400)
    
    client_ids = {d.client_id for d in drafts if d.client_id}
    
    if len(client_ids) > 1:
        raise_business_error(
            "BILL_MULTIPLE_CLIENTS",
            "Bill must contain items from single client only",
            400
        )
    
    if not client_ids:
        raise_business_error("BILL_NO_CLIENT", "Fee drafts have no client", 400)
    
    return list(client_ids)[0]
```""",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-03-03": {
        "title": "Implement validate_currency_match helper",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "None",
        "scope": "Implement ONLY validate_currency_match() to ensure all bill items have same currency.",
        "components": """```python
def validate_currency_match(items: list, bill_currency: str) -> None:
    \"\"\"Validate all items match bill currency.\"\"\"
    for item in items:
        item_currency = item.get('currency')
        if item_currency and item_currency != bill_currency:
            raise_business_error(
                "BILL_CURRENCY_MISMATCH",
                f"All items must match bill currency {bill_currency}",
                400
            )
```""",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-03-04": {
        "title": "Implement generate_bill_from_drafts service",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-01, ENH-03-02, ENH-03-03",
        "scope": "Implement bill generation from fee drafts with full validation.",
        "components": """```python
def generate_bill_from_drafts(db: Session, draft_ids: list[str], user_id: str):
    # Validate single client
    client_id = validate_single_client(db, draft_ids)
    
    # Load drafts with items
    # Create bill with generated bill_no
    # Create bill items from draft items
    # Lock drafts (set is_locked=True)
    # Return Bill
```""",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-03-05": {
        "title": "Implement create_payment service",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-01",
        "scope": "Implement payment registration service.",
        "components": "create_payment(db, data: PaymentCreate, user_id) -> Payment",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-03-06": {
        "title": "Implement create_offset service",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-01, ENH-03-07",
        "scope": "Implement payment offset creation with currency validation and balance update.",
        "components": "create_offset(db, data: OffsetCreate, user_id) -> Offset + update_bill_balance() call",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-03-07": {
        "title": "Implement update_bill_balance helper",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "None",
        "scope": "Implement bill balance recalculation after offset.",
        "components": "update_bill_balance(db, bill_id) -> None (sum offsets, update paid_amount, balance)",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-03-08": {
        "title": "Implement update_case_receipt service",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "None",
        "scope": "Implement case receipt summary update (aggregate payments by case).",
        "components": "update_case_receipt(db, case_id) -> None",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-03-09": {
        "title": "Add T_PaymentLine model",
        "file": "backend/app/modules/billing/models.py",
        "prereq": "ENH-00-04",
        "scope": "Add T_PaymentLine model to track payment allocations to bills.",
        "components": "T_PaymentLine(payment_id, bill_id, amount) - many-to-many payment-bill mapping",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/models.py"
    },
    
    "ENH-03-10": {
        "title": "Implement bill status transitions",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "None",
        "scope": "Implement bill status state machine (DRAFT → ISSUED → PAID/CANCELLED).",
        "components": "update_bill_status(db, bill_id, new_status, user_id) -> Bill",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    # ========== Phase 3c: Documents Module (7 files) ==========
    "ENH-04-01": {
        "title": "Create document Pydantic schemas",
        "file": "backend/app/modules/documents/schemas.py",
        "prereq": "None",
        "scope": "Create ALL document schemas in ONE task.",
        "components": "DocumentCreate, DocumentUpdate, DocumentOut, DocumentListItem, AttachmentOut",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/documents/schemas.py"
    },
    
    "ENH-04-02": {
        "title": "Implement list_documents service",
        "file": "backend/app/modules/documents/service.py",
        "prereq": "ENH-04-01, ENH-00-03",
        "scope": "Implement document listing with pagination and filters.",
        "components": "list_documents(db, case_id, direction, page, page_size) -> PageResult[DocumentListItem]",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/documents/service.py"
    },
    
    "ENH-04-03": {
        "title": "Implement create_document service",
        "file": "backend/app/modules/documents/service.py",
        "prereq": "ENH-04-01",
        "scope": "Implement document creation with case linking validation.",
        "components": "create_document(db, data: DocumentCreate, user_id) -> Document",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/documents/service.py"
    },
    
    "ENH-04-04": {
        "title": "Implement add_attachment service with validation",
        "file": "backend/app/modules/documents/service.py",
        "prereq": "ENH-00-06",
        "scope": "Implement attachment upload with file type and size validation.",
        "components": "add_attachment(db, doc_id, upload_file: UploadFile, user_id) -> Attachment",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/documents/service.py"
    },
    
    "ENH-04-05": {
        "title": "Add document enums",
        "file": "backend/app/modules/documents/enums.py",
        "prereq": "None",
        "scope": "Create document direction and type enums.",
        "components": "DocDirection(OUTGOING, INCOMING), DocType(OA, CLIENT, INTERNAL, PRIORITY)",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/documents/enums.py"
    },
    
    "ENH-04-06": {
        "title": "Implement document-case linking validation",
        "file": "backend/app/modules/documents/service.py",
        "prereq": "None",
        "scope": "Add case_id foreign key validation in create_document.",
        "components": "validate_case_exists(db, case_id) -> None (raise error if not found)",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/documents/service.py"
    },
    
    "ENH-04-07": {
        "title": "Implement document search/filter",
        "file": "backend/app/modules/documents/service.py",
        "prereq": "ENH-04-02",
        "scope": "Enhance list_documents with search by doc_no, title, case_id.",
        "components": "Add q, case_id, direction, doc_type filters to list_documents",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/documents/service.py"
    },
    
    # ========== Phase 3d: Tasks Module (8 files) ==========
    "ENH-05-01": {
        "title": "Create task Pydantic schemas",
        "file": "backend/app/modules/tasks/schemas.py",
        "prereq": "None",
        "scope": "Create ALL task schemas.",
        "components": "TaskCreate, TaskUpdate, TaskOut, TaskListItem, TaskLogOut",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/tasks/schemas.py"
    },
    
    "ENH-05-02": {
        "title": "Add T_TaskLog model",
        "file": "backend/app/modules/tasks/models.py",
        "prereq": "ENH-00-04",
        "scope": "Add T_TaskLog model for audit trail.",
        "components": "T_TaskLog(task_id, old_status, new_status, comment, created_by, created_at)",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/tasks/models.py"
    },
    
    "ENH-05-03": {
        "title": "Implement task service layer (CRUD)",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "ENH-05-01",
        "scope": "Implement basic task CRUD operations.",
        "components": "list_tasks, create_task, get_task, update_task services",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    "ENH-05-04": {
        "title": "Implement get_today_tasks service",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "ENH-05-01",
        "scope": "Implement today's reminder tasks query (deadline_date = today).",
        "components": "get_today_tasks(db, worker_id=None) -> list[TaskOut]",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    "ENH-05-05": {
        "title": "Implement close_task service",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "ENH-05-02, ENH-05-03",
        "scope": "Implement task close with status transition and log creation.",
        "components": "close_task(db, task_id, user_id) -> Task (status=CLOSED, create TaskLog)",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    "ENH-05-06": {
        "title": "Implement reopen_task service",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "ENH-05-02, ENH-05-03",
        "scope": "Implement task reopen with log creation.",
        "components": "reopen_task(db, task_id, user_id) -> Task (status=PENDING, create TaskLog)",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    "ENH-05-07": {
        "title": "Implement assign_task service",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "ENH-05-02, ENH-05-03",
        "scope": "Implement task assignment with log creation.",
        "components": "assign_task(db, task_id, worker_id, user_id) -> Task (create TaskLog)",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    "ENH-05-08": {
        "title": "Implement task status transition validation",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "None",
        "scope": "Implement status transition rules (PENDING→IN_PROGRESS→CLOSED, etc).",
        "components": "validate_status_transition(old_status, new_status) -> None",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    # ========== Phase 3e: Fees Module (7 files) ==========
    "ENH-06-01": {
        "title": "Create fee Pydantic schemas",
        "file": "backend/app/modules/fees/schemas.py",
        "prereq": "None",
        "scope": "Create ALL fee schemas.",
        "components": "FeeDraftCreate, FeeItemCreate, FeeRateCreate, FeeOut, FeeListItem",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/fees/schemas.py"
    },
    
    "ENH-06-02": {
        "title": "Implement fee draft service layer",
        "file": "backend/app/modules/fees/service.py",
        "prereq": "ENH-06-01",
        "scope": "Implement fee draft CRUD operations.",
        "components": "list_drafts, create_draft, update_draft, delete_draft services",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/fees/service.py"
    },
    
    "ENH-06-03": {
        "title": "Add FeeType enum",
        "file": "backend/app/modules/fees/enums.py",
        "prereq": "None",
        "scope": "Create fee type enumeration.",
        "components": "FeeType(GOV='Official Fee', SERVICE='Service Fee', MISC='Miscellaneous')",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/fees/enums.py"
    },
    
    "ENH-06-04": {
        "title": "Implement draft locking mechanism",
        "file": "backend/app/modules/fees/models.py",
        "prereq": "None",
        "scope": "Add is_locked field to FeeDraft model.",
        "components": "Add is_locked: Mapped[bool] = mapped_column(Boolean, default=False)",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/fees/models.py"
    },
    
    "ENH-06-05": {
        "title": "Implement lock_draft service",
        "file": "backend/app/modules/fees/service.py",
        "prereq": "ENH-06-04",
        "scope": "Implement fee draft locking (prevent edits after billing).",
        "components": "lock_draft(db, draft_id, user_id) -> FeeDraft (set is_locked=True)",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/fees/service.py"
    },
    
    "ENH-06-06": {
        "title": "Implement unlock_draft service",
        "file": "backend/app/modules/fees/service.py",
        "prereq": "ENH-06-04",
        "scope": "Implement draft unlocking (admin only).",
        "components": "unlock_draft(db, draft_id, user_id) -> FeeDraft (set is_locked=False)",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/fees/service.py"
    },
    
    "ENH-06-07": {
        "title": "Implement fee item CRUD services",
        "file": "backend/app/modules/fees/service.py",
        "prereq": "ENH-06-01",
        "scope": "Implement fee item management within drafts.",
        "components": "add_fee_item, update_fee_item, delete_fee_item services",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/fees/service.py"
    },
    
    # ========== Phase 3f: Clients Module (4 files) ==========
    "ENH-07-01": {
        "title": "Create client Pydantic schemas",
        "file": "backend/app/modules/masterdata/clients/schemas.py",
        "prereq": "None",
        "scope": "Create proper typed schemas (no dict types).",
        "components": "ClientCreate, ClientUpdate, ClientOut, ClientAddressIn, ClientContactIn",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/masterdata/clients/schemas.py"
    },
    
    "ENH-07-02": {
        "title": "Implement client service layer",
        "file": "backend/app/modules/masterdata/clients/service.py",
        "prereq": "ENH-07-01",
        "scope": "Implement client CRUD operations.",
        "components": "list_clients, create_client, update_client, deactivate_client services",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/masterdata/clients/service.py"
    },
    
    "ENH-07-03": {
        "title": "Add client code uniqueness validation",
        "file": "backend/app/modules/masterdata/clients/service.py",
        "prereq": "ENH-07-02",
        "scope": "Validate client_code uniqueness in create/update.",
        "components": "Check duplicate client_code, raise CLIENT_CODE_DUPLICATE error",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/masterdata/clients/service.py"
    },
    
    "ENH-07-04": {
        "title": "Fix addresses/contacts as proper schemas",
        "file": "backend/app/modules/masterdata/clients/schemas.py",
        "prereq": "ENH-07-01",
        "scope": "Replace dict with proper Pydantic models for addresses/contacts.",
        "components": "ClientAddressIn(address_type, country, province, city, address), ClientContactIn(name, title, phone, email)",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/masterdata/clients/schemas.py"
    },
    
    # ========== Phase 4: Database Enhancements (5 files) ==========
    "ENH-08-01": {
        "title": "Create comprehensive database migrations",
        "file": "backend/alembic/versions/XXXX_mvp1_complete.py",
        "prereq": "All model tasks complete",
        "scope": "Create or consolidate migrations for all MVP1 tables.",
        "components": "Alembic migration covering all t_* tables with proper indexes and FKs",
        "priority": "P0",
        "validation": "alembic upgrade head"
    },
    
    "ENH-08-02": {
        "title": "Add database indexes per spec",
        "file": "backend/alembic/versions/XXXX_add_indexes.py",
        "prereq": "ENH-08-01",
        "scope": "Add performance indexes per docs/03_database_mvp1_subset.md.",
        "components": "Indexes on: case_no, app_no, client_id, case_id FKs, bill_no, payment_no, doc_no, etc.",
        "priority": "P0",
        "validation": "alembic upgrade head"
    },
    
    "ENH-08-03": {
        "title": "Add foreign key constraints",
        "file": "Multiple migration files",
        "prereq": "ENH-08-01",
        "scope": "Ensure all foreign keys have proper CASCADE/RESTRICT rules.",
        "components": "Review and add missing FK constraints with proper ondelete behavior",
        "priority": "P1",
        "validation": "alembic check"
    },
    
    "ENH-08-04": {
        "title": "Enhance database seeding script",
        "file": "backend/scripts/seed_dev.py",
        "prereq": "ENH-01-10",
        "scope": "Extend seed script with sample test data (optional).",
        "components": "Add --with-test-data flag to seed sample cases, clients, etc.",
        "priority": "P2",
        "validation": "python scripts/seed_dev.py --help"
    },
    
    "ENH-08-05": {
        "title": "Update existing models to use mixins",
        "file": "Multiple model files",
        "prereq": "ENH-00-04",
        "scope": "Refactor existing models to use UUIDPrimaryKeyMixin and AuditMixin.",
        "components": "Update Case, Bill, Payment, etc. to inherit from mixins",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/*/models.py"
    },
    
    # ========== Phase 5: API Refactoring (7 files) ==========
    "ENH-09-01": {
        "title": "Refactor cases API to use service layer",
        "file": "backend/app/modules/cases/api.py",
        "prereq": "ENH-02-05 to ENH-02-10",
        "scope": "Replace direct DB access with service function calls.",
        "components": "Update GET/POST/PUT endpoints to call list_cases, create_case, update_case_full, update_case_limited",
        "priority": "P0",
        "validation": "ruff check app/modules/cases/api.py"
    },
    
    "ENH-09-02": {
        "title": "Refactor billing API to use service layer",
        "file": "backend/app/modules/billing/api.py",
        "prereq": "ENH-03 series complete",
        "scope": "Replace direct DB access with service functions.",
        "components": "Update endpoints to use billing services",
        "priority": "P0",
        "validation": "ruff check app/modules/billing/api.py"
    },
    
    "ENH-09-03": {
        "title": "Refactor documents API to use service layer",
        "file": "backend/app/modules/documents/api.py",
        "prereq": "ENH-04 series complete",
        "scope": "Replace direct DB access with service functions.",
        "components": "Update endpoints to use document services",
        "priority": "P0",
        "validation": "ruff check app/modules/documents/api.py"
    },
    
    "ENH-09-04": {
        "title": "Refactor tasks API to use service layer",
        "file": "backend/app/modules/tasks/api.py",
        "prereq": "ENH-05 series complete",
        "scope": "Replace direct DB access with service functions.",
        "components": "Update endpoints to use task services",
        "priority": "P0",
        "validation": "ruff check app/modules/tasks/api.py"
    },
    
    "ENH-09-05": {
        "title": "Refactor fees API to use service layer",
        "file": "backend/app/modules/fees/api.py",
        "prereq": "ENH-06 series complete",
        "scope": "Replace direct DB access with service functions.",
        "components": "Update endpoints to use fee services",
        "priority": "P0",
        "validation": "ruff check app/modules/fees/api.py"
    },
    
    "ENH-09-06": {
        "title": "Refactor clients API to use service layer",
        "file": "backend/app/modules/masterdata/clients/api.py",
        "prereq": "ENH-07 series complete",
        "scope": "Replace direct DB access with service functions.",
        "components": "Update endpoints to use client services",
        "priority": "P0",
        "validation": "ruff check app/modules/masterdata/clients/api.py"
    },
    
    "ENH-09-07": {
        "title": "Fix CSV export endpoint",
        "file": "backend/app/modules/cases/api.py",
        "prereq": "ENH-02-07",
        "scope": "Fix GET /cases/export to return CSV instead of JSON.",
        "components": "Use StreamingResponse with CSV writer, proper Content-Type header",
        "priority": "P1",
        "validation": "curl http://localhost:8000/api/v1/cases/export | head -1"
    },
    
    # ========== Phase 6: Business Logic (15 files) ==========
    "ENH-10-01": {
        "title": "Implement priority date auto-calculation",
        "file": "backend/app/modules/cases/service.py",
        "prereq": "ENH-02-08, ENH-02-09",
        "scope": "Auto-calculate case.prio_date = MIN(priorities.prio_date) on create/update.",
        "components": "Add calculate_prio_date(priorities) helper, update in create/update services",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/cases/service.py"
    },
    
    "ENH-10-02": {
        "title": "Add auth middleware to router",
        "file": "backend/app/api/router.py",
        "prereq": "ENH-01-09",
        "scope": "Ensure auth router is properly mounted.",
        "components": "api_router.include_router(auth_router, prefix='/auth', tags=['Auth'])",
        "priority": "P0",
        "validation": "curl http://localhost:8000/api/v1/auth/login"
    },
    
    "ENH-10-03": {
        "title": "Implement bill balance update on offset",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-06, ENH-03-07",
        "scope": "Ensure bill.paid_amount and balance update after offset.",
        "components": "Call update_bill_balance in create_offset service",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-10-04": {
        "title": "Auto-update case receipts on payment",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-06, ENH-03-08",
        "scope": "Trigger case receipt update when offset created.",
        "components": "Call update_case_receipt in create_offset service",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-10-05": {
        "title": "Auto-create task log on status change",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "ENH-05-02, ENH-05-05 to ENH-05-07",
        "scope": "Ensure TaskLog created in close/reopen/assign services.",
        "components": "Create T_TaskLog entry with old_status, new_status, user_id",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    "ENH-10-06": {
        "title": "Prevent editing locked fee drafts",
        "file": "backend/app/modules/fees/service.py",
        "prereq": "ENH-06-04",
        "scope": "Check is_locked flag in update/delete draft services.",
        "components": "Raise FEE_DRAFT_LOCKED error if is_locked=True",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/fees/service.py"
    },
    
    "ENH-10-07": {
        "title": "Enforce single-client validation in bill creation",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-02, ENH-03-04",
        "scope": "Ensure validate_single_client called in generate_bill_from_drafts.",
        "components": "Already implemented in ENH-03-04",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-10-08": {
        "title": "Enforce currency consistency in bills",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-03, ENH-03-04",
        "scope": "Ensure validate_currency_match called in bill generation.",
        "components": "Already implemented in ENH-03-04",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-10-09": {
        "title": "Add payment-offset currency validation",
        "file": "backend/app/modules/billing/service.py",
        "prereq": "ENH-03-06",
        "scope": "Validate payment.currency == bill.currency in create_offset.",
        "components": "Add currency match check, raise CURRENCY_MISMATCH error",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/billing/service.py"
    },
    
    "ENH-10-10": {
        "title": "Enforce case number uniqueness",
        "file": "backend/app/modules/cases/service.py",
        "prereq": "ENH-02-08",
        "scope": "Ensure create_case checks duplicates.",
        "components": "Already implemented in ENH-02-08",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/cases/service.py"
    },
    
    "ENH-10-11": {
        "title": "Implement task status transition rules",
        "file": "backend/app/modules/tasks/service.py",
        "prereq": "ENH-05-08",
        "scope": "Enforce status transitions in task update services.",
        "components": "Call validate_status_transition before status changes",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/tasks/service.py"
    },
    
    "ENH-10-12": {
        "title": "Add fee item validation",
        "file": "backend/app/modules/fees/service.py",
        "prereq": "ENH-06-07",
        "scope": "Validate fee item amounts > 0, fee_type valid.",
        "components": "Add validation in add_fee_item service",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/fees/service.py"
    },
    
    "ENH-10-13": {
        "title": "Add attachment file type validation",
        "file": "backend/app/modules/documents/service.py",
        "prereq": "ENH-04-04",
        "scope": "Validate file types (pdf, doc, docx, jpg, png) and max size.",
        "components": "Check upload_file.content_type, size < 10MB",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/documents/service.py"
    },
    
    "ENH-10-14": {
        "title": "Enforce applicant first flag validation",
        "file": "backend/app/modules/cases/service.py",
        "prereq": "ENH-02-06",
        "scope": "Ensure validate_applicants called.",
        "components": "Already implemented in ENH-02-08, ENH-02-09",
        "priority": "P0",
        "validation": "python -m py_compile app/modules/cases/service.py"
    },
    
    "ENH-10-15": {
        "title": "Add template path security check",
        "file": "backend/app/modules/templates/service.py",
        "prereq": "ENH-00-06",
        "scope": "Use safe_join for template path resolution.",
        "components": "from app.core.storage import safe_join in template rendering",
        "priority": "P1",
        "validation": "python -m py_compile app/modules/templates/service.py"
    },
    
    # ========== Phase 7a: Testing (6 files) ==========
    "ENH-11-01": {
        "title": "Set up pytest structure",
        "file": "backend/tests/conftest.py",
        "prereq": "None",
        "scope": "Create pytest configuration and fixtures.",
        "components": "pytest fixtures: db_session, test_client, test_user, test_admin",
        "priority": "P1",
        "validation": "pytest --collect-only"
    },
    
    "ENH-11-02": {
        "title": "Create test fixtures",
        "file": "backend/tests/conftest.py",
        "prereq": "ENH-11-01",
        "scope": "Add reusable test fixtures for DB, users, clients.",
        "components": "@pytest.fixture for test_db, test_admin_user, test_client_data",
        "priority": "P1",
        "validation": "pytest tests/conftest.py::test_fixtures -v"
    },
    
    "ENH-11-03": {
        "title": "Unit tests for auth services",
        "file": "backend/tests/test_auth.py",
        "prereq": "ENH-11-02, ENH-01 series",
        "scope": "Test authenticate_user, get_user_permissions, etc.",
        "components": "test_authenticate_valid, test_authenticate_invalid, test_get_permissions",
        "priority": "P1",
        "validation": "pytest tests/test_auth.py -v"
    },
    
    "ENH-11-04": {
        "title": "Unit tests for cases services",
        "file": "backend/tests/test_cases.py",
        "prereq": "ENH-11-02, ENH-02 series",
        "scope": "Test case CRUD and validation.",
        "components": "test_create_case, test_validate_applicants, test_list_cases",
        "priority": "P1",
        "validation": "pytest tests/test_cases.py -v"
    },
    
    "ENH-11-05": {
        "title": "Integration tests for key flows",
        "file": "backend/tests/test_integration.py",
        "prereq": "ENH-11-02",
        "scope": "Test E2E workflows (login → create case → create bill → payment).",
        "components": "test_case_creation_flow, test_billing_flow, test_payment_offset_flow",
        "priority": "P1",
        "validation": "pytest tests/test_integration.py -v"
    },
    
    "ENH-11-06": {
        "title": "Add test coverage reporting",
        "file": "backend/pyproject.toml + .coveragerc",
        "prereq": "ENH-11-03, ENH-11-04",
        "scope": "Configure pytest-cov for coverage reporting.",
        "components": "Add pytest-cov config, min coverage 70%",
        "priority": "P2",
        "validation": "pytest --cov=app --cov-report=html"
    },
    
    # ========== Phase 7b: Documentation (6 files) ==========
    "ENH-12-01": {
        "title": "Add endpoint docstrings",
        "file": "Multiple api.py files",
        "prereq": "ENH-09 series",
        "scope": "Add detailed docstrings to all API endpoints.",
        "components": "Document params, returns, raises, examples for each endpoint",
        "priority": "P1",
        "validation": "curl http://localhost:8000/docs | grep -c description"
    },
    
    "ENH-12-02": {
        "title": "Create API usage guide",
        "file": "docs/api_usage_guide.md",
        "prereq": "None",
        "scope": "Document common API usage patterns.",
        "components": "Authentication flow, case creation example, billing workflow",
        "priority": "P1",
        "validation": "test -f docs/api_usage_guide.md"
    },
    
    "ENH-12-03": {
        "title": "Document environment variables",
        "file": "docs/environment_variables.md",
        "prereq": "None",
        "scope": "List all .env variables with descriptions.",
        "components": "DATABASE_URL, JWT_SECRET, CORS_ORIGINS, FILE_STORAGE_PATH",
        "priority": "P1",
        "validation": "test -f docs/environment_variables.md"
    },
    
    "ENH-12-04": {
        "title": "Create deployment runbook",
        "file": "docs/deployment_runbook.md",
        "prereq": "None",
        "scope": "Step-by-step deployment guide for MVP1.",
        "components": "Docker compose, alembic migrations, seed data, health checks",
        "priority": "P1",
        "validation": "test -f docs/deployment_runbook.md"
    },
    
    "ENH-12-05": {
        "title": "Document error codes",
        "file": "docs/error_codes.md",
        "prereq": "ENH-00-01",
        "scope": "List all BusinessError codes with descriptions.",
        "components": "AUTH_INVALID, CASE_NO_DUPLICATE, BILL_CURRENCY_MISMATCH, etc.",
        "priority": "P1",
        "validation": "test -f docs/error_codes.md"
    },
    
    "ENH-12-06": {
        "title": "Create database schema diagram",
        "file": "docs/database_schema_diagram.md",
        "prereq": "ENH-08-01",
        "scope": "Mermaid ER diagram of all MVP1 tables.",
        "components": "Mermaid erDiagram with entities and relationships",
        "priority": "P2",
        "validation": "test -f docs/database_schema_diagram.md"
    },
}


def generate_task_file(task_id: str, task_info: dict) -> str:
    """Generate markdown content for a task file."""
    return f"""# {task_id} — {task_info['title']}

## Design references
- `docs/04_backend_architecture.md`
- `docs/02_permissions_rbac.md`
- `mvp1_backend_review_report.md`
- `mvp1_enhancement_checklist.md`

## Target
- **File:** `{task_info['file']}`
- **Atomic rule:** modify/create ONLY this file; implement ONLY as described below.

## Prerequisites
- {task_info['prereq']}

## Scope decision (MVP1 – FIXED)
{task_info['scope']}

## Components to implement (EXACT)
{task_info['components']}

## Non-scope (explicitly excluded)
- Features beyond specified scope
- Modifications to other files
- Advanced functionality not in MVP1

## Prompt
Implement the specified functionality following AGENTS.md atomic task rules.

Requirements:
- Implement exactly as specified
- SQLite compatible
- Follow established patterns from existing code
- Use Pydantic v2 for schemas
- Use SQLAlchemy 2.x typed API for models

Do NOT:
- Modify files beyond target
- Add features beyond scope
- Ask clarification questions

## Acceptance checklist
- [ ] Only specified file(s) modified/created
- [ ] Implements exact requirements
- [ ] Code passes ruff check/format
- [ ] SQLite compatible (no PG-only features)
- [ ] Follows AGENTS.md rules

## Validation commands
```bash
cd backend
{task_info['validation']}
ruff check .
ruff format .
```

**Priority**: {task_info['priority']}
**Module**: {task_info['file'].split('/')[2] if '/' in task_info['file'] else 'core'}
"""


def main():
    """Generate all remaining task files."""
    print(f"🚀 Generating atomic task files in: {TASK_DIR}")
    print("=" * 60)
    
    created_count = 0
    skipped_count = 0
    
    for task_id in sorted(TASK_TEMPLATES.keys()):
        task_info = TASK_TEMPLATES[task_id]
        task_file = TASK_DIR / f"{task_id}.md"
        
        if task_file.exists():
            print(f"  ⏭️  Skip {task_id} (already exists)")
            skipped_count += 1
            continue
        
        try:
            content = generate_task_file(task_id, task_info)
            task_file.write_text(content, encoding='utf-8')
            created_count += 1
            print(f"  ✅ Created {task_id} — {task_info['title']}")
        except Exception as e:
            print(f"  ❌ Error creating {task_id}: {e}")
    
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  Created: {created_count} files")
    print(f"  Skipped: {skipped_count} files (already exist)")
    print(f"  Total templates: {len(TASK_TEMPLATES)} files")
    print(f"\n📁 Location: {TASK_DIR}")
    print(f"\n✅ Generation complete!")
    
    # List existing files
    existing = sorted([f.name for f in TASK_DIR.glob("ENH-*.md")])
    print(f"\n📋 Total ENH-*.md files after generation: {len(existing)}")


if __name__ == "__main__":
    main()
