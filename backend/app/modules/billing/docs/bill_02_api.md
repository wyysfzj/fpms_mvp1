# Billing APIs (MVP1)

Base: `/api/v1/billing`

Bills
- GET /bills
- POST /bills/from-drafts
- POST /bills/manual (optional MVP1)
- GET /bills/{id}
- GET /bills/{id}/print (docx download)

Payments
- GET /payments
- POST /payments
- GET /payments/{id}

Offsets
- POST /offsets (allocate)
- POST /offsets/{id}/reverse (future)

Case receipts
- GET /cases/{case_id}/receipts

