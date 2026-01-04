# MVP1 DB Migrations Overview

This package ships a complete MVP1 migration chain:

- 0001_mvp1_core_tables.py  (RBAC + Client + Case)
- 0002_documents.py         (DocTemplate + Template + Document + Attachment)
- 0003_tasks.py             (TaskTemplate + Task + TaskLog)
- 0004_fees.py              (FeeRate + FeeDraft + FeeItem)
- 0005_billing.py           (Bill + BillItem + Payment + PaymentLine + Offset + CaseReceipt)

Apply migrations:
```bash
cd backend
alembic upgrade head
```

Notes:
- Migrations are designed to work on SQLite (PoC) and Postgres (prod).
- Avoid PG-specific types in migrations; use generic SQLAlchemy types.
