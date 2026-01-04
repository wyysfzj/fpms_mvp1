# Backend API Atomic Tasks (Phase 3) — Unified v4

This directory contains one-task-per-endpoint API implementation tasks.

This version unifies permission naming to match `docs/02_permissions_rbac.md` style and includes request/response examples.


Prerequisites:
- DB migrated: `cd backend && alembic upgrade head`
- ORM parity completed: `tasks/backend/models_from_migrations/`


## clients

- `BE-APIv4-001_clients_get_clients` — `GET /clients` → `backend/app/modules/masterdata/clients/api.py`  (perm: `Client.Read`)
- `BE-APIv4-002_clients_post_clients` — `POST /clients` → `backend/app/modules/masterdata/clients/api.py`  (perm: `Client.Create`)
- `BE-APIv4-003_clients_put_clients_id` — `PUT /clients/{id}` → `backend/app/modules/masterdata/clients/api.py`  (perm: `Client.Edit`)
- `BE-APIv4-004_clients_put_clients_id_deactivate` — `PUT /clients/{id}/deactivate` → `backend/app/modules/masterdata/clients/api.py`  (perm: `Client.Action`)
## cases

- `BE-APIv4-005_cases_get_cases` — `GET /cases` → `backend/app/modules/cases/api.py`  (perm: `Case.Read`)
- `BE-APIv4-006_cases_post_cases` — `POST /cases` → `backend/app/modules/cases/api.py`  (perm: `Case.Create`)
- `BE-APIv4-007_cases_get_cases_case_id` — `GET /cases/{case_id}` → `backend/app/modules/cases/api.py`  (perm: `Case.Read`)
- `BE-APIv4-008_cases_put_cases_case_id` — `PUT /cases/{case_id}` → `backend/app/modules/cases/api.py`  (perm: `Case.Edit`)
- `BE-APIv4-009_cases_post_cases_case_id_limited-edit` — `POST /cases/{case_id}/limited-edit` → `backend/app/modules/cases/api.py`  (perm: `Case.EditLimited`)
- `BE-APIv4-010_cases_get_cases_export` — `GET /cases/export` → `backend/app/modules/cases/api.py`  (perm: `Case.Export`)
## documents

- `BE-APIv4-011_documents_get_documents` — `GET /documents` → `backend/app/modules/documents/api.py`  (perm: `Doc.Read`)
- `BE-APIv4-012_documents_post_documents` — `POST /documents` → `backend/app/modules/documents/api.py`  (perm: `Doc.Create`)
- `BE-APIv4-013_documents_get_documents_id` — `GET /documents/{id}` → `backend/app/modules/documents/api.py`  (perm: `Doc.Read`)
- `BE-APIv4-014_documents_put_documents_id` — `PUT /documents/{id}` → `backend/app/modules/documents/api.py`  (perm: `Doc.Edit`)
- `BE-APIv4-015_documents_post_documents_id_attachments` — `POST /documents/{id}/attachments` → `backend/app/modules/documents/api.py`  (perm: `Doc.Attach`)
- `BE-APIv4-016_documents_get_documents_id_attachments_att_id_download` — `GET /documents/{id}/attachments/{att_id}/download` → `backend/app/modules/documents/api.py`  (perm: `Doc.Attach`)
## tasks

- `BE-APIv4-017_tasks_get_tasks` — `GET /tasks` → `backend/app/modules/tasks/api.py`  (perm: `Task.Read`)
- `BE-APIv4-018_tasks_post_tasks` — `POST /tasks` → `backend/app/modules/tasks/api.py`  (perm: `Task.Create`)
- `BE-APIv4-019_tasks_get_tasks_id` — `GET /tasks/{id}` → `backend/app/modules/tasks/api.py`  (perm: `Task.Read`)
- `BE-APIv4-020_tasks_put_tasks_id` — `PUT /tasks/{id}` → `backend/app/modules/tasks/api.py`  (perm: `Task.Edit`)
- `BE-APIv4-021_tasks_post_tasks_id_close` — `POST /tasks/{id}/close` → `backend/app/modules/tasks/api.py`  (perm: `Task.Action`)
- `BE-APIv4-022_tasks_post_tasks_id_reopen` — `POST /tasks/{id}/reopen` → `backend/app/modules/tasks/api.py`  (perm: `Task.Action`)
- `BE-APIv4-023_tasks_post_tasks_id_cancel` — `POST /tasks/{id}/cancel` → `backend/app/modules/tasks/api.py`  (perm: `Task.Action`)
- `BE-APIv4-024_tasks_get_tasks_today?as=worker|supervisor` — `GET /tasks/today?as=worker|supervisor` → `backend/app/modules/tasks/api.py`  (perm: `Task.Read`)
## fees

- `BE-APIv4-025_fees_get_fees_drafts` — `GET /fees/drafts` → `backend/app/modules/fees/api.py`  (perm: `Fee.Draft.Read`)
- `BE-APIv4-026_fees_post_fees_drafts` — `POST /fees/drafts` → `backend/app/modules/fees/api.py`  (perm: `Fee.Draft.Create`)
- `BE-APIv4-027_fees_get_fees_drafts_id` — `GET /fees/drafts/{id}` → `backend/app/modules/fees/api.py`  (perm: `Fee.Draft.Read`)
- `BE-APIv4-028_fees_put_fees_drafts_id` — `PUT /fees/drafts/{id}` → `backend/app/modules/fees/api.py`  (perm: `Fee.Draft.Edit`)
- `BE-APIv4-029_fees_post_fees_drafts_id_lock` — `POST /fees/drafts/{id}/lock` → `backend/app/modules/fees/api.py`  (perm: `Fee.Draft.Action`)
- `BE-APIv4-030_fees_post_fees_drafts_id_unlock` — `POST /fees/drafts/{id}/unlock` → `backend/app/modules/fees/api.py`  (perm: `Fee.Draft.Action`)
- `BE-APIv4-031_fees_post_fees_drafts_id_items` — `POST /fees/drafts/{id}/items` → `backend/app/modules/fees/api.py`  (perm: `Fee.Item.Create`)
- `BE-APIv4-032_fees_put_fees_items_item_id` — `PUT /fees/items/{item_id}` → `backend/app/modules/fees/api.py`  (perm: `Fee.Item.Edit`)
- `BE-APIv4-033_fees_delete_fees_items_item_id` — `DELETE /fees/items/{item_id}` → `backend/app/modules/fees/api.py`  (perm: `Fee.Item.Delete`)
- `BE-APIv4-034_fees_get_fees_rates` — `GET /fees/rates` → `backend/app/modules/fees/api.py`  (perm: `Fee.Rate.Read`)
- `BE-APIv4-035_fees_post_fees_rates` — `POST /fees/rates` → `backend/app/modules/fees/api.py`  (perm: `Fee.Rate.Create`)
- `BE-APIv4-036_fees_put_fees_rates_id` — `PUT /fees/rates/{id}` → `backend/app/modules/fees/api.py`  (perm: `Fee.Rate.Edit`)
## billing

- `BE-APIv4-037_billing_get_bills` — `GET /bills` → `backend/app/modules/billing/api.py`  (perm: `Bill.Read`)
- `BE-APIv4-038_billing_post_bills_from-drafts` — `POST /bills/from-drafts` → `backend/app/modules/billing/api.py`  (perm: `Bill.Create`)
- `BE-APIv4-039_billing_post_bills_manual` — `POST /bills/manual` → `backend/app/modules/billing/api.py`  (perm: `Bill.Create`)
- `BE-APIv4-040_billing_get_bills_id` — `GET /bills/{id}` → `backend/app/modules/billing/api.py`  (perm: `Bill.Read`)
- `BE-APIv4-041_billing_get_bills_id_print` — `GET /bills/{id}/print` → `backend/app/modules/billing/api.py`  (perm: `Bill.Print`)
- `BE-APIv4-042_billing_get_payments` — `GET /payments` → `backend/app/modules/billing/api.py`  (perm: `Payment.Read`)
- `BE-APIv4-043_billing_post_payments` — `POST /payments` → `backend/app/modules/billing/api.py`  (perm: `Payment.Create`)
- `BE-APIv4-044_billing_get_payments_id` — `GET /payments/{id}` → `backend/app/modules/billing/api.py`  (perm: `Payment.Read`)
- `BE-APIv4-045_billing_post_offsets` — `POST /offsets` → `backend/app/modules/billing/api.py`  (perm: `Payment.Create`)
- `BE-APIv4-046_billing_post_offsets_id_reverse` — `POST /offsets/{id}/reverse` → `backend/app/modules/billing/api.py`  (perm: `Payment.Create`)
- `BE-APIv4-047_billing_get_cases_case_id_receipts` — `GET /cases/{case_id}/receipts` → `backend/app/modules/billing/api.py`  (perm: `CaseReceipt.Read`)
